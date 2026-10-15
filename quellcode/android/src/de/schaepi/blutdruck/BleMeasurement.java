package de.schaepi.puls180;
import java.time.*;import java.time.format.*;import java.util.*;
public final class BleMeasurement{
public final Integer measurementStatus;public final double sys,dia,pulse;public final String time;
private BleMeasurement(double s,double d,double p,String t,Integer status){sys=s;dia=d;pulse=p;time=t;measurementStatus=status;}
private static int u(byte b){return b&255;}
private static double number(byte[] a,int i){int raw=u(a[i])|(u(a[i+1])<<8);int m=raw&4095;if(m>=2046&&m<=2050)return Double.NaN;if(m>=2048)m-=4096;int e=raw>>12;if(e>=8)e-=16;return m*Math.pow(10,e);}
public static BleMeasurement parse(byte[] a){if(a==null||a.length<7)throw new IllegalArgumentException("Unvollständige Messung");int flags=u(a[0]);int expected=7+((flags&2)!=0?7:0)+((flags&4)!=0?2:0)+((flags&8)!=0?1:0)+((flags&16)!=0?2:0);if(a.length<expected)throw new IllegalArgumentException("Unvollständige Messung");double factor=(flags&1)==0?1:7.500616827;double sys=number(a,1)*factor,dia=number(a,3)*factor;int offset=7;String time="Messzeit vom Gerät nicht verfügbar";if((flags&2)!=0){try{time=LocalDateTime.of(u(a[7])|(u(a[8])<<8),u(a[9]),u(a[10]),u(a[11]),u(a[12]),u(a[13])).format(DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm:ss"));}catch(DateTimeException e){time="Gerätezeit ungültig oder unvollständig";}offset+=7;}double pulse=(flags&4)!=0?number(a,offset):Double.NaN;if(!Double.isFinite(sys)||!Double.isFinite(dia)||sys<=0||dia<=0||sys<=dia)throw new IllegalArgumentException("Gerät liefert keinen gültigen Blutdruck");if((flags&4)!=0)offset+=2;if((flags&8)!=0)offset++;Integer status=(flags&16)!=0?(u(a[offset])|(u(a[offset+1])<<8)):null;return new BleMeasurement(sys,dia,pulse,time,status);}
public String display(){return time+"\n"+String.format(Locale.GERMANY,"%.0f / %.0f mmHg",sys,dia)+"\nPuls "+(Double.isFinite(pulse)&&pulse>0?String.format(Locale.GERMANY,"%.0f bpm",pulse):"—");}
}


