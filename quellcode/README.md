# Quellstand App 5.20 / PC-Tagebuch 5.12

Android: build-app.ps1 benötigt Android SDK 36, JDK 17 und den privaten Signaturschlüssel außerhalb dieses Repositories. Vor dem Build das veröffentlichte Puls-180-PC-Tagebuch-5.12.zip nach android/res/raw/pc_tagebuch.zip kopieren. Das Buildskript enthält die lokalen Werkzeugpfade des Projekts, keine Passwörter oder Schlüssel.

PC: Das veröffentlichte PC-Paket enthält die passende Python-Laufzeit. Quellcode und Tests liegen unter pc. Zum Prüfen PYTHONPATH auf pc/app setzen und mit der mitgelieferten Laufzeit `python -m unittest discover -s pc/tests -q` ausführen. Messdaten liegen außerhalb des Programms im Windows-Benutzerprofil.
