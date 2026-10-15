package de.schaepi.puls180;
import android.content.*;import android.os.*;import android.speech.tts.*;import java.util.*;
public final class MeasurementSpeech {
private static TextToSpeech engine;private static String pending,last="";private static long lastAt;private static final Handler h=new Handler(Looper.getMainLooper());private static boolean ready;
public static void stop(){h.post(()->{pending=null;ready=false;if(engine!=null){engine.stop();engine.shutdown();engine=null;}});}
public static void announce(Context ctx,double sys,double dia,double pulse){if(!License.allowed(ctx))return;Context c=ctx.getApplicationContext();h.post(()->{if(!c.getSharedPreferences("bluetooth",0).getBoolean("speech",true))return;String words=String.format(Locale.GERMANY,"Blutdruck %.0f zu %.0f",sys,dia)+(Double.isFinite(pulse)&&pulse>0?String.format(Locale.GERMANY,", Puls %.0f",pulse):"");long now=SystemClock.elapsedRealtime();if(words.equals(last)&&now-lastAt<10000)return;last=words;lastAt=now;pending=words;if(engine==null){engine=new TextToSpeech(c,status->{h.post(()->{if(engine==null)return;if(status==TextToSpeech.SUCCESS&&engine.getVoices()!=null){for(Voice v:engine.getVoices())if(v.getLocale().getLanguage().equals("de")&&!v.isNetworkConnectionRequired()){engine.setVoice(v);ready=true;break;}}if(ready)say(c);else{c.getSharedPreferences("bluetooth",0).edit().putString("speechStatus","Keine deutsche Offline-Stimme verfügbar. Bitte in Android eine deutsche Offline-Stimme installieren.").apply();stop();}});});}else if(ready)say(c);});}
private static void say(Context c){if(!License.allowed(c))return;if(pending==null||!c.getSharedPreferences("bluetooth",0).getBoolean("speech",true))return;engine.speak(pending,TextToSpeech.QUEUE_FLUSH,null,"measurement");pending=null;c.getSharedPreferences("bluetooth",0).edit().putString("speechStatus","Deutsche Offline-Ansage bereit").apply();}
}


