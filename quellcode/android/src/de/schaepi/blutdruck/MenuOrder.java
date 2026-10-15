package de.schaepi.puls180;
import java.util.*;
public final class MenuOrder {
public static ArrayList<String> restore(String[] available,String saved){ArrayList<String> out=new ArrayList<>();List<String> valid=Arrays.asList(available);for(String s:saved.split("\n"))if(valid.contains(s)&&!out.contains(s))out.add(s);for(String s:available)if(!out.contains(s))out.add(s);return out;}
public static void move(List<String> order,String from,String to){int a=order.indexOf(from),b=order.indexOf(to);if(a<0||b<0||a==b)return;order.remove(a);order.add(b,from);}
}


