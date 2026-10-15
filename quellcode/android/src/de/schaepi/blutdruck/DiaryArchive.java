package de.schaepi.puls180;
import android.content.*;import android.database.*;import android.database.sqlite.*;import org.json.*;import java.util.*;
/** Local snapshots and folder references; never changes Health Connect records. */
public final class DiaryArchive extends SQLiteOpenHelper {
 public DiaryArchive(Context c){super(c,"diary-archive.db",null,1);}
 public void onCreate(SQLiteDatabase db){db.execSQL("CREATE TABLE entries(k TEXT PRIMARY KEY,payload TEXT NOT NULL)");db.execSQL("CREATE TABLE folders(k TEXT NOT NULL,month TEXT NOT NULL,PRIMARY KEY(k,month))");}
 public void onUpgrade(SQLiteDatabase db,int a,int b){}
 public void capture(JSONArray rows)throws JSONException {SQLiteDatabase db=getWritableDatabase();db.beginTransaction();try{for(int i=0;i<rows.length();i++){JSONObject row=rows.getJSONObject(i);String key=row.getString("key");boolean fresh;try(Cursor c=db.rawQuery("SELECT 1 FROM entries WHERE k=?",new String[]{key})){fresh=!c.moveToFirst();}ContentValues v=new ContentValues();v.put("k",key);v.put("payload",row.toString());db.insertWithOnConflict("entries",null,v,SQLiteDatabase.CONFLICT_REPLACE);if(fresh){ContentValues f=new ContentValues();f.put("k",key);f.put("month",row.getString("month"));db.insertOrThrow("folders",null,f);}}db.setTransactionSuccessful();}finally{db.endTransaction();}}
 public void place(String key,String month,boolean move){java.time.YearMonth.parse(month);SQLiteDatabase db=getWritableDatabase();db.beginTransaction();try{try(Cursor c=db.rawQuery("SELECT 1 FROM entries WHERE k=?",new String[]{key})){if(!c.moveToFirst())throw new IllegalArgumentException("Messung fehlt");}ArrayList<String> existing=new ArrayList<>();try(Cursor c=db.rawQuery("SELECT month FROM folders WHERE k=?",new String[]{key})){while(c.moveToNext())existing.add(c.getString(0));}Set<String> targets=MonthPlacement.plan(existing,month,move);db.delete("folders","k=?",new String[]{key});for(String target:targets){ContentValues v=new ContentValues();v.put("k",key);v.put("month",target);db.insertOrThrow("folders",null,v);}db.setTransactionSuccessful();}finally{db.endTransaction();}}
 public JSONArray rows(String month)throws JSONException {JSONArray result=new JSONArray();String query=month==null?"SELECT payload FROM entries ORDER BY k":"SELECT e.payload FROM entries e JOIN folders f ON f.k=e.k WHERE f.month=? ORDER BY e.k";try(Cursor c=getReadableDatabase().rawQuery(query,month==null?null:new String[]{month})){while(c.moveToNext())result.put(new JSONObject(c.getString(0)));}return result;}
 public void removeMonths(Collection<String> months){SQLiteDatabase db=getWritableDatabase();db.beginTransaction();try{for(String month:months){java.time.YearMonth.parse(month);db.delete("folders","month=?",new String[]{month});}db.setTransactionSuccessful();}finally{db.endTransaction();}}
 public JSONArray links()throws JSONException {JSONArray result=new JSONArray();try(Cursor c=getReadableDatabase().rawQuery("SELECT k,month FROM folders ORDER BY month,k",null)){while(c.moveToNext())result.put(new JSONObject().put("key",c.getString(0)).put("month",c.getString(1)));}return result;}
}



