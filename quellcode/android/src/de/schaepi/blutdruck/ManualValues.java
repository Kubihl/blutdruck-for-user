package de.schaepi.puls180;

public final class ManualValues {
    public final int systolic;
    public final int diastolic;
    public final double pulse;

    private ManualValues(int systolic, int diastolic, double pulse) {
        this.systolic = systolic;
        this.diastolic = diastolic;
        this.pulse = pulse;
    }

    public static ManualValues parse(String systolicText, String diastolicText, String pulseText) {
        try {
            int systolic = Integer.parseInt(systolicText.trim());
            int diastolic = Integer.parseInt(diastolicText.trim());
            double pulse = pulseText.trim().isEmpty() ? Double.NaN : Integer.parseInt(pulseText.trim());
            if (systolic < 40 || systolic > 300) throw new IllegalArgumentException("Systolisch muss zwischen 40 und 300 liegen.");
            if (diastolic < 30 || diastolic > 200) throw new IllegalArgumentException("Diastolisch muss zwischen 30 und 200 liegen.");
            if (systolic <= diastolic) throw new IllegalArgumentException("Systolisch muss größer als diastolisch sein.");
            if (Double.isFinite(pulse) && (pulse < 20 || pulse > 250)) throw new IllegalArgumentException("Puls muss zwischen 20 und 250 liegen oder leer bleiben.");
            return new ManualValues(systolic, diastolic, pulse);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Bitte nur ganze Zahlen eintragen.");
        }
    }
}


