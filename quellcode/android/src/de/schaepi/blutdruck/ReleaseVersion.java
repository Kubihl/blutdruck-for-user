package de.schaepi.puls180;
public final class ReleaseVersion {
 public static boolean newer(String remote,String local){if(remote==null||local==null||!remote.matches("v?[0-9]{1,6}(\\.[0-9]{1,6}){1,3}")||!local.matches("[0-9]{1,6}(\\.[0-9]{1,6}){1,3}"))return false;String[] a=remote.replaceFirst("^v","").split("\\."),b=local.split("\\.");for(int i=0;i<Math.max(a.length,b.length);i++){int x=i<a.length?Integer.parseInt(a[i]):0,y=i<b.length?Integer.parseInt(b[i]):0;if(x!=y)return x>y;}return false;}
}


