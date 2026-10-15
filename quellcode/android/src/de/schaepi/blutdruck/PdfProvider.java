package de.schaepi.puls180;
import android.content.*;import android.database.*;import android.net.Uri;import android.os.ParcelFileDescriptor;import android.provider.OpenableColumns;import java.io.*;
public class PdfProvider extends ContentProvider{
public boolean onCreate(){return true;}
private File file(Uri uri)throws FileNotFoundException{if(!License.allowed(getContext()))throw new FileNotFoundException("Test abgelaufen");String name=uri.getLastPathSegment();if(!(getContext().getPackageName()+".pdf").equals(uri.getAuthority())||uri.getPathSegments().size()!=1||name==null||!name.matches("[a-f0-9-]{36}\\.(pdf|xlsx|csv|json)"))throw new FileNotFoundException();File file=new File(getContext().getCacheDir(),name);if(!file.isFile())throw new FileNotFoundException();return file;}
public String getType(Uri uri){String name=uri.getLastPathSegment();if(name!=null&&name.endsWith(".json"))return "application/json";return TableExport.mime(name==null?"pdf":name.substring(name.lastIndexOf('.')+1));}
public ParcelFileDescriptor openFile(Uri uri,String mode)throws FileNotFoundException{if(!"r".equals(mode))throw new FileNotFoundException("Read only");return ParcelFileDescriptor.open(file(uri),ParcelFileDescriptor.MODE_READ_ONLY);}
public Cursor query(Uri uri,String[] projection,String selection,String[] args,String sort){try{File f=file(uri);String[] cols=projection==null?new String[]{OpenableColumns.DISPLAY_NAME,OpenableColumns.SIZE}:projection;MatrixCursor c=new MatrixCursor(cols);Object[] row=new Object[cols.length];for(int i=0;i<cols.length;i++)row[i]=OpenableColumns.DISPLAY_NAME.equals(cols[i])?(f.getName().endsWith(".json")?"Puls-180-PC-Werte.json":"Blutdruckliste"+f.getName().substring(f.getName().lastIndexOf('.'))):OpenableColumns.SIZE.equals(cols[i])?f.length():null;c.addRow(row);return c;}catch(FileNotFoundException e){return null;}}
public Uri insert(Uri u,ContentValues v){throw new UnsupportedOperationException();}public int update(Uri u,ContentValues v,String s,String[] a){throw new UnsupportedOperationException();}public int delete(Uri u,String s,String[] a){throw new UnsupportedOperationException();}
}


