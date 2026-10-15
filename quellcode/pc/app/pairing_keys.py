from pathlib import Path
import os,json,secrets,hashlib,datetime
DATA=Path(os.environ['LOCALAPPDATA'])/'BlutdruckTagebuchVerkauf'/'daten'
def ensure_keys():
 DATA.mkdir(parents=True,exist_ok=True)
 if (DATA/'sync.json').exists():return
 from cryptography import x509
 from cryptography.hazmat.primitives import hashes,serialization
 from cryptography.hazmat.primitives.asymmetric import rsa
 from cryptography.x509.oid import NameOID
 key=rsa.generate_private_key(public_exponent=65537,key_size=3072)
 name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Blutdruck Tagebuch')]);now=datetime.datetime.now(datetime.timezone.utc)
 cert=x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key()).serial_number(x509.random_serial_number()).not_valid_before(now-datetime.timedelta(days=1)).not_valid_after(now+datetime.timedelta(days=3650)).sign(key,hashes.SHA256())
 (DATA/'sync-key.pem').write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
 (DATA/'sync-cert.pem').write_bytes(cert.public_bytes(serialization.Encoding.PEM))
 (DATA/'sync.json').write_text(json.dumps({'token':secrets.token_hex(32),'pin':hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()}),encoding='utf-8')
