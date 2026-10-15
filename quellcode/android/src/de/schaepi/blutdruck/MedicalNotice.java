package de.schaepi.puls180;
import android.app.*;
public final class MedicalNotice {
 public static void show(Activity a,boolean once){if(once&&a.getSharedPreferences("medicalNotice",0).getBoolean("v2",false))return;
 new AlertDialog.Builder(a).setTitle("Wichtiger medizinischer Hinweis").setMessage("Puls 180 dient ausschließlich als digitales Tagebuch zur persönlichen Protokollierung und Übersicht deiner Blutdruck- und Pulswerte.\n\nKeine Messfunktion: Die App selbst misst keinen Blutdruck. Sie erfasst nur Werte, die du per Hand eingibst oder die ein vorhandenes, separat erworbenes Blutdruckmessgerät über Bluetooth beziehungsweise Health Connect bereitstellt.\n\nKeine Diagnose oder Therapieempfehlung: Farbmarkierungen, gewählte ESH-/ESC-Skalen, Durchschnittswerte, Pulsdruck, mittlerer arterieller Druck und Gerätemeldungen dienen nur der übersichtlichen Darstellung. Sie stellen keine Diagnose dar. Die App empfiehlt weder eine Behandlung noch Medikamente oder Dosierungen. Ein Hinweis auf unregelmäßigen Herzschlag stammt vom Messgerät.\n\nKein Ersatz für den Arzt: Die App ersetzt keine ärztliche Beratung, Diagnose oder Behandlung. Prüfe übertragene Werte mit dem Messgerät und wende dich bei Beschwerden, auffälligen Werten oder gesundheitlichen Fragen an medizinisches Fachpersonal.").setPositiveButton("Verstanden",(d,w)->a.getSharedPreferences("medicalNotice",0).edit().putBoolean("v2",true).apply()).setCancelable(!once).show();
 }
}


