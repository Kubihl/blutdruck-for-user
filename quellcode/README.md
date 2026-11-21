# Quellstand App 5.24 / PC-Tagebuch 5.13

Android: SDK 36, JDK 17, privater Signaturschlüssel außerhalb dieses Repositories. build-app.ps1 enthält lokale Pfade, keine privaten Schlüssel oder Passwörter. Das aktuelle veröffentlichte PC-ZIP liegt identisch in android/res/raw/pc_tagebuch.zip.

PC: Python-Laufzeit aus dem veröffentlichten ZIP verwenden. PYTHONPATH auf pc/app setzen, dann `python -m unittest discover -s pc/tests -v`. 19 Prüfungen bestanden. Persönliche Daten werden außerhalb des Programms gespeichert. Wiederherstellung prüft und ersetzt nach Bestätigung in einer Transaktion; davor konsistente SQLite-Vorsicherung. Tests verwenden getrennte temporäre Datenbanken.
