using System;
using System.IO;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows.Forms;
class DirectFileActions {
 [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
 struct Attachment { public uint reserved, flags, position; [MarshalAs(UnmanagedType.LPWStr)] public string path, name; public IntPtr type; }
 [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
 class Message { public uint reserved; [MarshalAs(UnmanagedType.LPWStr)] public string subject="Blutdruck – Messliste", body="", type, date, conversation; public uint flags; public IntPtr originator; public uint recipients=0; public IntPtr recipient; public uint files=1; public IntPtr attachment; }
 [DllImport("MAPI32.dll",CharSet=CharSet.Unicode,ExactSpelling=true)]
 static extern uint MAPISendMailW(IntPtr session,IntPtr owner,Message message,uint flags,uint reserved);
 [STAThread] static int Main(string[] args) {
  if(args.Length!=2 || !File.Exists(args[0]))return 40;
  string file=Path.GetFullPath(args[0]),ext=Path.GetExtension(file).ToLowerInvariant();
  if(ext!=".pdf"&&ext!=".xlsx"&&ext!=".csv"&&ext!=".zip")return 40;
  try {
   if(args[1]=="copy" || args[1]=="whatsapp") {
    var files=new System.Collections.Specialized.StringCollection();files.Add(file);
    Clipboard.SetDataObject(new DataObject(DataFormats.FileDrop,new string[]{file}),true,10,100);
    if(args[1]=="whatsapp") {try {Process.Start(new ProcessStartInfo("whatsapp:"){UseShellExecute=true});}catch{return 31;}}
    return 0;
   }
   if(args[1]=="save") {
    Application.EnableVisualStyles();
    using(var dialog=new SaveFileDialog {FileName=Path.GetFileName(file),Filter="Datei (*"+ext+")|*"+ext,DefaultExt=ext.TrimStart('.'),AddExtension=true,OverwritePrompt=true}) {
     if(dialog.ShowDialog()!=DialogResult.OK)return 1;
     if(!String.Equals(file,dialog.FileName,StringComparison.OrdinalIgnoreCase))File.Copy(file,dialog.FileName,true);
     return 0;
    }
   }
   if(args[1]=="email") {
    var attachment=new Attachment{position=0xffffffff,path=file,name=Path.GetFileName(file)};
    IntPtr ptr=Marshal.AllocHGlobal(Marshal.SizeOf(typeof(Attachment)));
    try {
     Marshal.StructureToPtr(attachment,ptr,false);
     // Always show the compose dialog, with NO recipient. Never send silently.
     uint result=MAPISendMailW(IntPtr.Zero,IntPtr.Zero,new Message{attachment=ptr},0x8|0x1,0);
     return result==0?0:result==1?1:50;
    } finally {Marshal.DestroyStructure(ptr,typeof(Attachment));Marshal.FreeHGlobal(ptr);}
   }
   return 40;
  }catch{return 50;}
 }
}
