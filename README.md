# Puls 180 - Blutdruck und Puls dokumentieren

Aktueller Stand: **Android-App 5.24 (Code 65)** und **PC-Tagebuch 5.13 (Code 63)**.

- [Handy-App herunterladen](Puls-180-5.24.apk)
- [PC-Tagebuch herunterladen](Puls-180-PC-Tagebuch-5.13.zip)
- [PC-Anleitung als PDF](anleitungen/PC-Tagebuch-5.13-Anleitung.pdf)
- [Handy-Anleitung](anleitungen/App-5.24-Anleitung.txt)
- [PC-Anleitung als Text](anleitungen/PC-Tagebuch-5.13-Anleitung.txt)

## Neu in dieser Ausgabe

Die Handy-App hat fünf Hauptbereiche. Einstellungen ist auf vier Gruppen reduziert; Export & Sicherung bietet Messwerte exportieren, Datensicherung und PC-Tagebuch & Vorlagen. Die PC-Datei ist als „PC-Datei fürs Tagebuch (JSON)“ bezeichnet. Gedrückt halten und nach links ziehen öffnet die Löschbestätigung für eine Messung.

Das PC-Tagebuch zeigt Blutdruck und Puls in einer kompakten Zeile. Text ist mit der Maus markierbar; Messungen werden über Kästchen ausgewählt. Notiz speichern ist nur bei einer Änderung aktiv. Doppelte Import- und Sicherungszugänge sind entfernt.

Im Menü stehen Datensicherung erstellen und Datensicherung wiederherstellen. Eine vollständige PC-JSON-Sicherung wird zunächst geprüft und als Vorschau angezeigt. Die Wiederherstellung ersetzt nach ausdrücklicher Bestätigung alle vier Benutzer mit Messungen, ausgeblendeten Einträgen, Notizen, Profilangaben und Monatsdateien. Vorher wird eine separate SQLite-Sicherung angelegt. PIN, Lizenz und Programmeinstellungen werden nicht ersetzt. Handy-Messwertdatei, Handy-Sicherung und PC-Sicherung sind unterschiedliche Dateien.

## Übertragung und Update

Handywerte als PC-JSON-Datei übertragen, am PC den passenden Benutzer wählen und den Import bestätigen. Doppelte Kennungen werden vermieden. Kein automatischer WLAN-/QR-Abgleich. Das PC-Programm nutzt eine lokale Browserseite; es ist kein natives Windows-Programm ohne Browser.

Vor einem Update eine Datensicherung erstellen und den bisherigen Hintergrundserver beenden; das Browserfenster zu schließen reicht dafür nicht. ZIP vollständig entpacken, Start-Web-App.cmd öffnen. Persönliche Daten liegen getrennt unter dem Windows-Benutzerprofil und dürfen nicht gelöscht werden. Die Handy-App als Update installieren, nicht vorher deinstallieren. Bei alter Darstellung Strg+F5 drücken.

## Prüfung und Grenzen

19 automatisierte PC-Prüfungen bestanden, darunter Wiederherstellung und Vorgängersicherung mit synthetischen Daten, Rücknahme bei Fehlern und Schutz vor ungültigen Dateien. Android-Build und APK-v3-Signatur geprüft. PDF visuell geprüft; eingebettetes und separates PC-ZIP sind bytegleich. Frühere Menüänderungen wurden auf dem Testhandy vom Benutzer bestätigt. Ein neuer durchgängiger Gerätetest von 5.24 mit Import und Wiederherstellung echter Daten ist noch offen.

Quellcode und Tests: [quellcode](quellcode/README.md). Bestehende Git-Historie bleibt erhalten. Ältere Downloads sind keine aktuelle Empfehlung. Werbemotive verwenden Beispielwerte; die Bilder sind keine neuen Originalaufnahmen der aktuellen Version. Keine neue Google-Play-Veröffentlichung erfolgt.

Android 10 und neuer; Health Connect in der App ab Android 14. Bluetooth benötigt geeignete Geräte. Beim ersten Öffnen beginnt die vierzehntägige Testzeit; für dauerhafte Nutzung ist ein passender gerätegebundener Kaufschlüssel nötig.

Puls 180 ist ein privates Hobbyprojekt zur Dokumentation. Es misst keinen Blutdruck, stellt keine Diagnose und ersetzt keine ärztliche Beratung. Kontakt: Kerstin Kubernat, puls180@t-online.de.
