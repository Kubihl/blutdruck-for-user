package de.schaepi.puls180;
import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.view.MotionEvent;
import android.view.ViewConfiguration;
import android.widget.ScrollView;
public final class RefreshScrollView extends ScrollView {
private final float threshold;private final int slop;private float x,y,pull;private boolean candidate,dragging;private Runnable refresh;private java.util.function.BooleanSupplier allowed;
public RefreshScrollView(Context c){super(c);threshold=96*c.getResources().getDisplayMetrics().density;slop=ViewConfiguration.get(c).getScaledTouchSlop();}
public void setRefreshAction(Runnable action,java.util.function.BooleanSupplier enabled){refresh=action;allowed=enabled;}
@Override public boolean dispatchTouchEvent(MotionEvent e){
int action=e.getActionMasked();
if(action==MotionEvent.ACTION_DOWN){x=e.getX();y=e.getY();pull=0;dragging=false;candidate=!canScrollVertically(-1)&&allowed!=null&&allowed.getAsBoolean();}
if(action==MotionEvent.ACTION_POINTER_DOWN){candidate=false;if(dragging){pull=0;invalidate();}}
if(action==MotionEvent.ACTION_MOVE&&candidate){float dy=e.getY()-y;float dx=Math.abs(e.getX()-x);
if(!dragging&&(dy < -slop||dx>slop&&dx>Math.abs(dy)))candidate=false;
if(candidate&&!dragging&&dy>slop&&dy>dx){dragging=true;MotionEvent cancel=MotionEvent.obtain(e);cancel.setAction(MotionEvent.ACTION_CANCEL);super.dispatchTouchEvent(cancel);cancel.recycle();}
if(dragging){pull=Math.max(0,dy);invalidate();return true;}}
if(action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_CANCEL){boolean handled=dragging;boolean run=handled&&candidate&&action==MotionEvent.ACTION_UP&&pull>=threshold&&allowed!=null&&allowed.getAsBoolean();candidate=false;dragging=false;pull=0;invalidate();if(run&&refresh!=null)refresh.run();if(handled)return true;}
if(dragging)return true;return super.dispatchTouchEvent(e);
}
@Override public void draw(Canvas c){super.draw(c);if(!dragging||pull<=0)return;float d=getResources().getDisplayMetrics().density;Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);p.setColor(0xff1553aa);float top=getPaddingTop();c.drawRect(0,top,getWidth(),top+48*d,p);p.setColor(0xffffffff);p.setTextAlign(Paint.Align.CENTER);p.setTextSize(16*getResources().getDisplayMetrics().scaledDensity);c.drawText(pull>=threshold?"Loslassen zum Aktualisieren":"Zum Aktualisieren weiter ziehen",getWidth()/2f,top+30*d,p);}
}


