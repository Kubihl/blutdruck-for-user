package de.schaepi.puls180;

import android.content.Context;
import android.view.MotionEvent;
import android.view.ViewConfiguration;
import android.widget.LinearLayout;

/** Hold, then drag left. A plain hold retains the existing selection action. */
public final class HoldSwipeRow extends LinearLayout {
    private float downX, downY;
    private boolean held, cancelled, swiping;
    private Runnable deleteAction;
    private final int slop;
    private final float density;
    private final Runnable hold = () -> {
        if (!cancelled) {
            held = true;
            getParent().requestDisallowInterceptTouchEvent(true);
            performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS);
        }
    };
    public HoldSwipeRow(Context context) {
        super(context);
        density = getResources().getDisplayMetrics().density;
        slop = ViewConfiguration.get(context).getScaledTouchSlop();
    }
    public void setDeleteAction(Runnable action) { deleteAction = action; }
    @Override public boolean dispatchTouchEvent(MotionEvent e) {
        int action = e.getActionMasked();
        float dx = e.getRawX() - downX, dy = e.getRawY() - downY;
        if (action == MotionEvent.ACTION_DOWN) {
            downX = e.getRawX(); downY = e.getRawY();
            held = cancelled = swiping = false;
            // Handle the hold here, avoiding the normal long-click timer.
            postDelayed(hold, ViewConfiguration.getLongPressTimeout());
            return true;
        }
        if (action == MotionEvent.ACTION_POINTER_DOWN) {
            cancelled = true; held = false; removeCallbacks(hold);
            setTranslationX(0); getParent().requestDisallowInterceptTouchEvent(false);
            return true;
        }
        if (action == MotionEvent.ACTION_MOVE) {
            if (!held && (Math.abs(dx) > slop || Math.abs(dy) > slop)) {
                cancelled = true; removeCallbacks(hold);
            }
            if (held && !cancelled) {
                swiping |= dx < -slop;
                setTranslationX(Math.max(-getWidth() * .65f, Math.min(0, dx)));
            }
            return true;
        }
        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_CANCEL) {
            removeCallbacks(hold);
            getParent().requestDisallowInterceptTouchEvent(false);
            boolean delete = action == MotionEvent.ACTION_UP && held && !cancelled
                && -dx >= Math.max(72 * density, getWidth() * .25f)
                && Math.abs(dy) < 64 * density;
            setTranslationX(0);
            if (delete && deleteAction != null) deleteAction.run();
            else if (action == MotionEvent.ACTION_UP && !cancelled) {
                if (held && !swiping) performLongClick();
                else if (!held) {
                    // Preserve child actions such as the colour legend.
                    MotionEvent down = MotionEvent.obtain(e);
                    down.setAction(MotionEvent.ACTION_DOWN);
                    super.dispatchTouchEvent(down); down.recycle();
                    super.dispatchTouchEvent(e);
                }
            }
            return true;
        }
        return true;
    }
    @Override protected void onDetachedFromWindow() {
        removeCallbacks(hold);
        super.onDetachedFromWindow();
    }
}
