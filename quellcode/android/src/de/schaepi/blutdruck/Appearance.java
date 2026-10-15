package de.schaepi.puls180;
import android.app.*;import android.content.*;import android.content.res.Configuration;import android.graphics.Color;
public final class Appearance{
 private Appearance(){}
 public static int choice(Context c){return c.getSharedPreferences("appearance",0).getInt("theme",0);}
 public static boolean isDark(Context c){int v=choice(c);return v==2||(v==0&&(c.getResources().getConfiguration().uiMode&Configuration.UI_MODE_NIGHT_MASK)==Configuration.UI_MODE_NIGHT_YES);}
 public static void apply(Activity a){a.setTheme(isDark(a)?android.R.style.Theme_Material_NoActionBar:android.R.style.Theme_Material_Light_NoActionBar);}
 public static int background(Context c){return isDark(c)?Color.rgb(18,24,32):Color.rgb(241,245,250);}
 public static int card(Context c){return isDark(c)?Color.rgb(35,44,56):Color.WHITE;}
 public static int text(Context c){return isDark(c)?Color.rgb(235,240,247):Color.rgb(20,38,63);}
 public static int secondary(Context c){return isDark(c)?Color.rgb(190,202,216):Color.rgb(70,82,98);}
}


