package de.schaepi.puls180;
public final class TrialPolicy {
 public static final long DURATION=14L*24*60*60*1000,TOLERANCE=120000;
 public static long effective(long wall,long last,long elapsed,long lastElapsed,int boot,int lastBoot){if(wall<=0||last<=0||elapsed<0||lastElapsed<0||boot<0||lastBoot<0)return -1;long floor=last;if(boot==lastBoot){if(elapsed<lastElapsed)return -1;long delta=elapsed-lastElapsed;if(last>Long.MAX_VALUE-delta)return -1;floor=last+delta;}if(wall<floor&&floor-wall>TOLERANCE)return -1;return Math.max(wall,floor);}
 public static long remaining(long start,long now){if(start<=0||now<start)return 0;long used=now-start;return used>=DURATION?0:DURATION-used;}
}

