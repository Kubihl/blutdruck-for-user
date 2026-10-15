package de.schaepi.puls180;
import java.time.YearMonth;import java.util.*;
public final class MonthPlacement {
 public static Set<String> plan(Collection<String> existing,String target,boolean move){YearMonth month=YearMonth.parse(target);if(month.getYear()<1970||month.getYear()>2200)throw new IllegalArgumentException("Jahr außerhalb des Bereichs");Set<String> result=new LinkedHashSet<>();if(!move)result.addAll(existing);result.add(month.toString());return result;}
}


