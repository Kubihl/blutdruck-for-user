package de.schaepi.puls180;
import android.content.Context;import android.graphics.*;import android.view.View;
public class PressureScaleView extends View{
 private final float sys,dia;private final boolean esh,showPoint;private final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
 public PressureScaleView(Context c,double systolic,double diastolic,boolean useEsh){super(c);sys=(float)systolic;dia=(float)diastolic;esh=useEsh;showPoint=true;setMinimumHeight((int)(270*c.getResources().getDisplayMetrics().density));}public PressureScaleView(Context c,boolean useEsh){super(c);sys=0;dia=0;esh=useEsh;showPoint=false;setMinimumHeight((int)(270*c.getResources().getDisplayMetrics().density));}
 private float x(float value,float left,float width){return left+(Math.max(50,Math.min(110,value))-50)/60f*width;}
 private float y(float value,float top,float height){return top+(180-Math.max(100,Math.min(180,value)))/80f*height;}
 @Override protected void onDraw(Canvas c){super.onDraw(c);float d=getResources().getDisplayMetrics().density,left=54*d,top=30*d,right=getWidth()-18*d,bottom=getHeight()-48*d,w=right-left,h=bottom-top;float yellowSys=esh?130:120,yellowDia=esh?85:70,redSys=140,redDia=90;
  p.setStyle(Paint.Style.FILL);p.setColor(Color.rgb(240,120,145));c.drawRect(left,top,right,bottom,p);p.setColor(Color.rgb(246,198,105));c.drawRect(left,y(redSys,top,h),x(redDia,left,w),bottom,p);p.setColor(Color.rgb(76,196,150));c.drawRect(left,y(yellowSys,top,h),x(yellowDia,left,w),bottom,p);
  p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2*d);p.setColor(Appearance.text(getContext()));c.drawRect(left,top,right,bottom,p);p.setStyle(Paint.Style.FILL);p.setTextSize(13*d);c.drawText("SYS",4*d,top+12*d,p);c.drawText("DIA",left,bottom+22*d,p);c.drawText(String.valueOf((int)yellowSys),4*d,y(yellowSys,top,h)+5*d,p);c.drawText("140",4*d,y(140,top,h)+5*d,p);c.drawText(String.valueOf((int)yellowDia),x(yellowDia,left,w)-12*d,bottom+22*d,p);c.drawText("90",x(90,left,w)-8*d,bottom+22*d,p);
  p.setStyle(Paint.Style.FILL);p.setTextSize(12*d);p.setColor(Appearance.text(getContext()));if(showPoint){float px=x(dia,left,w),py=y(sys,top,h);p.setColor(Color.rgb(40,105,220));c.drawCircle(px,py,8*d,p);p.setStyle(Paint.Style.STROKE);p.setStrokeWidth(2*d);p.setColor(Color.WHITE);c.drawCircle(px,py,8*d,p);p.setStyle(Paint.Style.FILL);p.setTextSize(12*d);p.setColor(Appearance.text(getContext()));c.drawText((esh?"ESH 2023":"ESC 2024")+" · Punkt: "+Math.round(sys)+"/"+Math.round(dia),left,bottom+42*d,p);}else c.drawText((esh?"ESH 2023":"ESC 2024")+" · Übersicht",left,bottom+42*d,p);
 }
}



