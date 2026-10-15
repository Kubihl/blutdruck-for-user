package de.schaepi.puls180;
import android.app.Activity;import android.content.*;import android.content.res.Configuration;import android.os.*;import android.view.MotionEvent;
public class FontActivity extends Activity {
 @Override protected void onCreate(Bundle state){Appearance.apply(this);applyStoredBrightness();getWindow().setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(Appearance.background(this)));super.onCreate(state);} private void applyStoredBrightness(){android.content.SharedPreferences prefs=getSharedPreferences("display",0);android.view.WindowManager.LayoutParams params=getWindow().getAttributes();if(prefs.contains("brightness")){int value=prefs.getInt("brightness",45);params.screenBrightness=Math.max(0.05f,Math.min(1f,(value+5)/100f));}else params.screenBrightness=android.view.WindowManager.LayoutParams.BRIGHTNESS_OVERRIDE_NONE;getWindow().setAttributes(params);}
 private final Handler licenseHandler=new Handler(Looper.getMainLooper());private boolean redirecting;
 protected boolean licenseBlocked(){
  if(this instanceof LicenseActivity||this instanceof PrivacyActivity)return false;
  if(License.allowed(this))return false;
  if(!redirecting){redirecting=true;stopService(new Intent(this,MeasurementService.class));startActivity(new Intent(this,LicenseActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK));finish();}
  return true;
 }
 private final Runnable checkLicense=new Runnable(){public void run(){if(!licenseBlocked())schedule();}};
 private void schedule(){licenseHandler.removeCallbacks(checkLicense);if(!(this instanceof LicenseActivity)&&!(this instanceof PrivacyActivity))licenseHandler.postDelayed(checkLicense,Math.max(1,Math.min(30000,License.remaining(this))));}
 @Override protected void onResume(){super.onResume();applyStoredBrightness();if(!licenseBlocked()){schedule();LicenseRevocation.checkOnOpen(this,()->{if(!isFinishing()&&!isDestroyed())licenseBlocked();});}}
 @Override protected void onPause(){licenseHandler.removeCallbacks(checkLicense);AppLock.notePause();super.onPause();}
 @Override public boolean dispatchTouchEvent(MotionEvent e){if(e.getActionMasked()==MotionEvent.ACTION_DOWN&&licenseBlocked())return true;return super.dispatchTouchEvent(e);}
 @Override protected void attachBaseContext(Context base){int choice=base.getSharedPreferences("appearance",0).getInt("fontSize",1);Configuration config=new Configuration();config.fontScale=(choice==0?0.85f:choice==2?1.2f:1f);super.attachBaseContext(base);applyOverrideConfiguration(config);}
}







