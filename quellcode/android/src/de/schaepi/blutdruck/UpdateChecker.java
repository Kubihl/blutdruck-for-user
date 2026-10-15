package de.schaepi.puls180;

import android.app.*;
import android.content.*;
import android.content.pm.PackageInfo;
import android.net.Uri;
import org.json.JSONObject;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

public final class UpdateChecker {
 private static final String API_URL="https://api.github.com/repos/Kubihl/blutdruck-for-user/contents/version.json?ref=main";
 private static final String INFO_URL="https://raw.githubusercontent.com/Kubihl/blutdruck-for-user/main/version.json";
 private static final long DAY=24L*60L*60L*1000L;
 private UpdateChecker(){}
 public static void check(Activity a,boolean manual){
  if(!manual){long last=a.getSharedPreferences("updates",0).getLong("lastCheck",0);if(System.currentTimeMillis()-last<DAY)return;}
  final AlertDialog wait=manual?new AlertDialog.Builder(a).setTitle("Puls 180 · Updates").setMessage("Neue Version wird gesucht …").setCancelable(false).show():null;
  Executors.newSingleThreadExecutor().execute(()->{
   try{
    JSONObject info;try{info=load(API_URL+"&t="+System.currentTimeMillis(),"application/vnd.github.raw+json");}catch(Exception primary){info=load(INFO_URL+"?t="+System.currentTimeMillis(),"application/json");}
    long latest=info.getLong("versionCode");String name=info.getString("versionName"),url=info.getString("apkUrl");
    PackageInfo own=a.getPackageManager().getPackageInfo(a.getPackageName(),0);long installed=own.getLongVersionCode();String installedName=own.versionName;
    a.getSharedPreferences("updates",0).edit().putLong("lastCheck",System.currentTimeMillis()).apply();
    a.runOnUiThread(()->{if(wait!=null)wait.dismiss();if(latest>installed)new AlertDialog.Builder(a).setTitle("Neue Version verfügbar").setMessage("Installiert: "+installedName+"\nNeu: "+name+"\n\nAPK herunterladen und anschließend die Installation in Android bestätigen.").setNegativeButton("Später",null).setPositiveButton("Herunterladen",(d,w)->a.startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(url)))).show();else if(manual)new AlertDialog.Builder(a).setTitle("Puls 180 · Updates").setMessage("Installiert: "+installedName+"\nKeine Updates verfügbar.").setPositiveButton("OK",null).show();});
   }catch(Exception e){a.runOnUiThread(()->{if(wait!=null)wait.dismiss();if(manual)new AlertDialog.Builder(a).setTitle("Updateprüfung nicht möglich").setMessage("Bitte Internetverbindung prüfen und später erneut versuchen.").setPositiveButton("OK",null).show();});}
  });
 }
 private static JSONObject load(String address,String accept)throws Exception{
  HttpURLConnection c=(HttpURLConnection)new URL(address).openConnection();c.setConnectTimeout(8000);c.setReadTimeout(8000);c.setUseCaches(false);c.setRequestProperty("Accept",accept);c.setRequestProperty("Cache-Control","no-cache");c.setRequestProperty("User-Agent","Puls-180-Android");
  if(c.getResponseCode()!=200)throw new IOException("HTTP "+c.getResponseCode());
  ByteArrayOutputStream out=new ByteArrayOutputStream();try(InputStream in=c.getInputStream()){byte[] b=new byte[4096];for(int n;(n=in.read(b))!=-1;)out.write(b,0,n);}finally{c.disconnect();}
  return new JSONObject(new String(out.toByteArray(),StandardCharsets.UTF_8));
 }
 public static void menu(Activity a){check(a,true);}
}
