package de.schaepi.puls180;
import android.os.Bundle;import android.content.*;import android.widget.*;
public class LicenseActivity extends FontActivity {
 private TextView status;private EditText key;
 @Override public void onCreate(Bundle b){super.onCreate(b);ScrollView scroll=new ScrollView(this);LinearLayout box=new LinearLayout(this);box.setOrientation(1);int pad=(int)(20*getResources().getDisplayMetrics().density);box.setPadding(pad,pad*2,pad,pad);scroll.addView(box);setContentView(scroll);
  TextView title=new TextView(this);title.setText("Puls 180 · Freischaltung");title.setTextSize(25);box.addView(title);
  status=new TextView(this);box.addView(status);
  TextView help=new TextView(this);help.setText("\nPuls 180 ist beim ersten Öffnen vierzehn Tage vollständig freigeschaltet.\n\nFür die dauerhafte Nutzung:\n1. Gerätecode kopieren oder direkt an den Anbieter von Puls 180 senden.\n2. Den erhaltenen Kaufschlüssel unten einfügen.\n3. Auf Dauerhaft freischalten tippen.\n");help.setTextSize(17);box.addView(help);
  TextView device=new TextView(this);device.setText(License.code(this));device.setTextSize(16);device.setTextIsSelectable(true);box.addView(device);
  Button copy=new Button(this);copy.setText("Gerätecode kopieren");copy.setOnClickListener(v->{((ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText("Puls-180-Gerätecode",License.code(this)));Toast.makeText(this,"Gerätecode kopiert",0).show();});box.addView(copy);
  Button send=new Button(this);send.setText("Gerätecode senden");send.setOnClickListener(v->{String code=License.code(this);Intent share=new Intent(Intent.ACTION_SEND);share.setType("text/plain");share.putExtra(Intent.EXTRA_SUBJECT,"Puls 180 – Gerätecode zur Freischaltung");share.putExtra(Intent.EXTRA_TEXT,"Guten Tag,\n\nich möchte Puls 180 dauerhaft freischalten.\n\nMein Gerätecode: "+code+"\n\nBitte senden Sie mir den passenden Freischaltschlüssel.");startActivity(Intent.createChooser(share,"Gerätecode senden mit …"));});box.addView(send);
  key=new EditText(this);key.setHint("Kaufschlüssel hier einfügen");key.setMinLines(3);key.setMaxLines(6);key.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE|android.text.InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);key.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(2048)});box.addView(key);
  Button activate=new Button(this);activate.setText("Dauerhaft freischalten");activate.setTextColor(android.graphics.Color.WHITE);activate.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);activate.setBackgroundTintList(android.content.res.ColorStateList.valueOf(android.graphics.Color.rgb(18,105,55)));activate.setOnClickListener(v->{if(License.paid(this)){status.setText("\n✓ DAUERHAFT FREIGESCHALTET\n");return;}if(License.activate(this,key.getText().toString())){Toast.makeText(this,"Puls 180 dauerhaft freigeschaltet",1).show();open();}else Toast.makeText(this,"Schlüssel ungültig oder für eine andere Installation. Bitte den Gerätecode prüfen.",1).show();});box.addView(activate);
  Button go=new Button(this);go.setText("Zurück zu meinen Werten");go.setOnClickListener(v->{if(License.allowed(this))open();else status.setText("\n"+License.status(this)+"\n");});box.addView(go);
  TextView note=new TextView(this);note.setText("\nDer Kaufschlüssel gilt dauerhaft für dieses Handy und kann nach Neuinstallation oder Löschen der App-Daten erneut verwendet werden. Bitte sicher aufbewahren. Bei Gerätewechsel oder Zurücksetzen des Handys kann eine neue kostenpflichtige Freischaltung erforderlich sein. Deine Messwerte werden beim Ende der Testzeit nicht gelöscht.");box.addView(note);
  Button privacy=new Button(this);privacy.setText("Datenschutz");privacy.setOnClickListener(v->startActivity(new Intent(this,PrivacyActivity.class)));box.addView(privacy);
  Button close=new Button(this);close.setText("Schließen");close.setOnClickListener(v->finishAndRemoveTask());box.addView(close);
  android.net.Uri activation=getIntent()==null?null:getIntent().getData();if(activation!=null&&"puls180".equals(activation.getScheme())&&"activate".equals(activation.getHost())){String received=activation.getQueryParameter("key");if(License.activate(this,received)){Toast.makeText(this,"Puls 180 dauerhaft freigeschaltet",Toast.LENGTH_LONG).show();open();}else{status.setText("\nFreischalt-Link ungültig oder für ein anderes Handy.\n");status.setTextColor(android.graphics.Color.rgb(190,45,45));}}
 }
 @Override protected void onResume(){super.onResume();boolean paid=License.paid(this),free=License.allowed(this);status.setText(paid?"\n✓ DAUERHAFT FREIGESCHALTET\n":"\n"+License.status(this)+"\n");status.setTextColor(free?android.graphics.Color.rgb(20,145,70):android.graphics.Color.rgb(190,45,45));status.setTextSize(paid?22:18);status.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);status.setGravity(android.view.Gravity.CENTER);status.setContentDescription(License.status(this));}
 private void open(){startActivity(new Intent(this,MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK));finish();}
}








