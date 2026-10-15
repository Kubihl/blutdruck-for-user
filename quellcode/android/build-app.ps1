$ErrorActionPreference='Stop'
$base='G:\Projekt Puls 180\AndroidTools'
if (!(Test-Path -LiteralPath (Join-Path $base 'java/jdk-17.0.20.1+1/bin/javac.exe'))) { throw ('AndroidTools fehlen neben dem Projektordner: ' + $base) }
$p=$PSScriptRoot
New-Item -ItemType Directory -Force -Path "$p/build/classes","$p/build/dex" | Out-Null
$env:JAVA_HOME="$base/java/jdk-17.0.20.1+1"
$javaFiles=Get-ChildItem "$p/src/de/schaepi/blutdruck" -Filter '*.java' | ForEach-Object FullName
& "$env:JAVA_HOME/bin/javac.exe" -encoding UTF-8 -source 8 -target 8 -classpath "$base/sdk/platforms/android-36/android.jar;$p/libs/zxing-core-3.5.4.jar" -d "$p/build/classes" $javaFiles
if ($LASTEXITCODE -ne 0) {throw 'javac failed'}
& "$env:JAVA_HOME/bin/jar.exe" cf "$p/build/classes.jar" -C "$p/build/classes" .
if ($LASTEXITCODE -ne 0) {throw 'jar failed'}
& "$base/sdk/build-tools/36.0.0/d8.bat" --lib "$base/sdk/platforms/android-36/android.jar" --min-api 29 --output "$p/build/dex" "$p/build/classes.jar" "$p/libs/zxing-core-3.5.4.jar"
if ($LASTEXITCODE -ne 0) {throw 'd8 failed'}
& "$base/sdk/build-tools/36.0.0/aapt2.exe" compile --dir "$p/res" -o "$p/build/resources.zip"
if ($LASTEXITCODE -ne 0) {throw 'resources failed'}
& "$base/sdk/build-tools/36.0.0/aapt2.exe" link -o "$p/build/current-unsigned.apk" --manifest "$p/AndroidManifest.xml" -I "$base/sdk/platforms/android-36/android.jar" "$p/build/resources.zip"
if ($LASTEXITCODE -ne 0) {throw 'aapt failed'}
& "$env:JAVA_HOME/bin/jar.exe" uf "$p/build/current-unsigned.apk" -C "$p/build/dex" classes.dex
if ($LASTEXITCODE -ne 0) {throw 'dex packaging failed'}
& "$base/sdk/build-tools/36.0.0/zipalign.exe" -f 4 "$p/build/current-unsigned.apk" "$p/build/current-aligned.apk"
if ($LASTEXITCODE -ne 0) {throw 'align failed'}
& "$base/sdk/build-tools/36.0.0/apksigner.bat" sign --ks "G:/Projekt Puls 180/Blutdruck Projekt/Schluesselverwaltung/verkauf.keystore" --ks-pass "file:G:/Projekt Puls 180/Blutdruck Projekt/Schluesselverwaltung/signatur-passwort.txt" --out "$p/Puls-180-5.20.apk" "$p/build/current-aligned.apk"
if ($LASTEXITCODE -ne 0) {throw 'sign failed'}
& "$base/sdk/build-tools/36.0.0/apksigner.bat" verify --verbose "$p/Puls-180-5.20.apk"
if ($LASTEXITCODE -ne 0) {throw 'verify failed'}


















































