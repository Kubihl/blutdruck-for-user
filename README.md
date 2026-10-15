# Puls 180 – Blutdruck und Puls dokumentieren

Aktueller Stand: **Android-App 5.20 (Code 61)** und **PC-Tagebuch 5.12 (Code 62)**.

- [Handy-App herunterladen](Puls-180-5.20.apk)
- [PC-Tagebuch herunterladen](Puls-180-PC-Tagebuch-5.12.zip)
- [PC-Anleitung als PDF](anleitungen/PC-Tagebuch-5.12-Anleitung.pdf)
- [Handy-Anleitung](anleitungen/App-5.20-Anleitung.txt)
- [PC-Anleitung als Text](anleitungen/PC-Tagebuch-5.12-Anleitung.txt)

Handeingabe mit optionaler Notiz, Health Connect, geeignete Bluetooth-Geräte, Sprachansage und PDF-/Excel-/CSV-Berichte. Vier getrennte PC-Benutzer; Größe, Gewicht und Datum sind über **Benutzer bearbeiten → Profil** bearbeitbar. Der Gewichtsverlauf bleibt erhalten. **Profil** neben dem aktiven Benutzer klappt die Anzeige auf.

Die JSON-Messwertdatei vom Handy wird am PC zuerst geprüft und dann bestätigt importiert. Vorhandene Werte werden nicht doppelt angelegt. Dies ist eine Dateiübertragung; spätere Änderungen am Handy oder PC werden nicht automatisch auf das andere Gerät übertragen. Vor dem Update den bisherigen PC-Server beenden. Messdaten im Windows-Benutzerprofil nicht löschen und die Handy-App als Update installieren.

## Bilder und Quellcode

Die bestätigten blauen Werbemotive liegen unter assets; das Google-Bilderpaket unter assets/google-bilder. Die Messwerte sind erfunden. Bearbeitete Archivansichten sind dort dokumentiert und stellen keine neuen Originalscreenshots von 5.20 dar. Eine Veröffentlichung im Google Play Store wurde nicht vorgenommen.

Aktueller Quellcode und Tests: [quellcode](quellcode/README.md). Alte Downloads wurden aus dem aktuellen Dateibaum entfernt und lokal im OLD-Archiv gesichert; frühere Git-Commits bleiben erhalten.

## Prüfung

Android-Build und APK-v3-Signatur geprüft; vierzehn Import-/Profil-/Startprüfungen erfolgreich. TXT-, HTML- und PDF-Anleitungen aktualisiert, PDF visuell geprüft. Neuer durchgängiger Test auf einem echten Handy mit anschließendem PC-Import noch offen.

Android 10 und neuer. Health Connect steht in der App ab Android 14 zur Verfügung. Geeignete Geräte sind für Bluetooth erforderlich. Beim ersten Öffnen beginnt die vierzehntägige Freischaltung; dauerhaft wird ein passender gerätegebundener Kaufschlüssel benötigt.

Puls 180 ist ein privates Hobbyprojekt zur persönlichen Dokumentation. Die App misst keinen Blutdruck, stellt keine Diagnose und ersetzt keine ärztliche Beratung. Kontakt: Kerstin Kubernat · puls180@t-online.de.
