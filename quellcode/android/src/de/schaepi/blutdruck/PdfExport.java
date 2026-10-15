package de.schaepi.puls180;
import android.app.Activity;
import android.print.*;
import android.os.*;
import android.graphics.*;
import android.graphics.pdf.PdfDocument;
import java.io.*;
import java.util.*;
public final class PdfExport {
private static ArrayList<String> noteLines(String value){ArrayList<String> lines=new ArrayList<>();String remaining=value.replaceAll("\\s+"," ").trim();if(remaining.isEmpty())return lines;remaining="Notiz: "+remaining;Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);p.setTextSize(10);while(!remaining.isEmpty()){int n=p.breakText(remaining,true,523,null);if(n<1)n=1;lines.add(remaining.substring(0,n));remaining=remaining.substring(n);}return lines;}
private static int rowHeight(String[] row){return 36+noteLines(row[4]).size()*12;}
private static ArrayList<Integer> pageStarts(ArrayList<String[]> rows){ArrayList<Integer> starts=new ArrayList<>();starts.add(0);int y=165;for(int i=0;i<rows.size();i++){int h=rowHeight(rows.get(i));if(y+h>785&&i>starts.get(starts.size()-1)){starts.add(i);y=165;}y+=h;}starts.add(rows.size());return starts;}

public static void open(Activity activity,ArrayList<String[]> rows,String period,String warning,String profile){
PrintManager manager=(PrintManager)activity.getSystemService(Activity.PRINT_SERVICE);
if(manager==null){android.widget.Toast.makeText(activity,"Druckfunktion nicht verfügbar.",1).show();return;}
final ArrayList<Integer> starts=pageStarts(rows);final int pages=starts.size()-1;
manager.print("Blutdruckliste",new PrintDocumentAdapter(){
@Override public void onLayout(PrintAttributes old,PrintAttributes now,CancellationSignal cancel,LayoutResultCallback callback,Bundle extras){
if(cancel.isCanceled()){callback.onLayoutCancelled();return;}
callback.onLayoutFinished(new PrintDocumentInfo.Builder("Blutdruckliste.pdf").setContentType(PrintDocumentInfo.CONTENT_TYPE_DOCUMENT).setPageCount(pages).build(),true);
}
@Override public void onWrite(PageRange[] ranges,ParcelFileDescriptor destination,CancellationSignal cancel,WriteResultCallback callback){
ArrayList<PageRange> written=new ArrayList<>();
PdfDocument doc=new PdfDocument();try{
for(int page=0;page<pages;page++){
boolean selected=false;for(PageRange range:ranges)if(page>=range.getStart()&&page<=range.getEnd())selected=true;
if(!selected)continue;if(cancel.isCanceled()){callback.onWriteCancelled();return;}
drawPage(doc,rows,period,warning,profile,page,pages,starts);written.add(new PageRange(page,page));
}
if(cancel.isCanceled()){callback.onWriteCancelled();return;}
try(FileOutputStream output=new FileOutputStream(destination.getFileDescriptor())){doc.writeTo(output);}
if(cancel.isCanceled())callback.onWriteCancelled();else callback.onWriteFinished(written.toArray(new PageRange[0]));
}catch(Exception e){callback.onWriteFailed("PDF konnte nicht erstellt werden. Bitte erneut versuchen.");}finally{doc.close();}
}
},new PrintAttributes.Builder().setMediaSize(PrintAttributes.MediaSize.ISO_A4).setColorMode(PrintAttributes.COLOR_MODE_MONOCHROME).setMinMargins(PrintAttributes.Margins.NO_MARGINS).build());
}
private static void drawPage(PdfDocument doc,ArrayList<String[]> rows,String period,String warning,String profile,int page,int pages,ArrayList<Integer> starts){drawPage(doc,rows,period,warning,profile,page,pages,starts,0);}
private static void drawPage(PdfDocument doc,ArrayList<String[]> rows,String period,String warning,String profile,int page,int pages,ArrayList<Integer> starts,int offset){
PdfDocument.Page sheet=doc.startPage(new PdfDocument.PageInfo.Builder(595,842,page+1+offset).create());Canvas c=sheet.getCanvas();Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);paint.setColor(Color.BLACK);
paint.setTextSize(21);paint.setTypeface(Typeface.create(Typeface.DEFAULT,Typeface.BOLD));c.drawText("Mein Blutdruck – Messliste",36,48,paint);
paint.setTypeface(Typeface.DEFAULT);paint.setTextSize(10);c.drawText(period,36,70,paint);c.drawText("Gedruckt am: "+java.time.LocalDateTime.now().format(java.time.format.DateTimeFormatter.ofPattern("dd.MM.yyyy HH:mm"))+" | "+rows.size()+" Messungen",36,86,paint);
c.drawText("Puls nur bei identischer Messzeit und Quelle; — = nicht zugeordnet.",36,102,paint);
if(profile!=null&&!profile.isEmpty())c.drawText(profile,36,118,paint);
if(!warning.isEmpty())c.drawText(warning,36,132,paint);
paint.setTypeface(Typeface.create(Typeface.DEFAULT,Typeface.BOLD));paint.setTextSize(12);c.drawText("Datum / Uhrzeit",36,147,paint);c.drawText("Blutdruck (mmHg)",270,147,paint);c.drawText("Puls (/min)",455,147,paint);paint.setTypeface(Typeface.DEFAULT);
int y=165;
for(int i=starts.get(page);i<starts.get(page+1);i++){
String[] row=rows.get(i);paint.setTextSize(10);c.drawText(row[0],36,y,paint);c.drawText(row[1],270,y,paint);c.drawText(row[2],455,y,paint);
paint.setTextSize(10);c.drawText(row[3],36,y+14,paint);
ArrayList<String> lines=noteLines(row[4]);for(int line=0;line<lines.size();line++)c.drawText(lines.get(line),36,y+26+line*12,paint);
int height=rowHeight(row);paint.setColor(Color.LTGRAY);c.drawLine(36,y+height-12,559,y+height-12,paint);paint.setColor(Color.BLACK);y+=height;
}
paint.setTextSize(10);c.drawText("Seite "+(page+1+offset)+" von "+pages,470,813,paint);doc.finishPage(sheet);
}
public static void saveReport(java.io.File file,ArrayList<String[]> rows,String period,String warning,String name)throws java.io.IOException{PdfDocument doc=new PdfDocument();try{ArrayList<Integer> starts=pageStarts(rows);int pages=starts.size();ReportSummary.draw(doc,rows,period,name,pages);for(int i=0;i<starts.size()-1;i++)drawPage(doc,rows,period,warning,name,i,pages,starts,1);try(java.io.FileOutputStream out=new java.io.FileOutputStream(file)){doc.writeTo(out);}}finally{doc.close();}}
public static void save(java.io.File file,ArrayList<String[]> rows,String period,String warning,String profile)throws java.io.IOException{
PdfDocument doc=new PdfDocument();try{ArrayList<Integer> starts=pageStarts(rows);int pages=starts.size()-1;for(int page=0;page<pages;page++)drawPage(doc,rows,period,warning,profile,page,pages,starts);try(java.io.FileOutputStream out=new java.io.FileOutputStream(file)){doc.writeTo(out);}}finally{doc.close();}
}
}




