import base64
import json
import time
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError

# Kunci contoh untuk percobaan ini saja. Jangan dipakai di aplikasi nyata.
KUNCI = "kunci-contoh-hanya-untuk-percobaan-ini-1234567890"
ALGORITMA = "HS256"

# 1. Membuat token: isi (payload) lalu ditandatangani dengan kunci
isi = {"sub": "budi", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
token = jwt.encode(isi, KUNCI, algorithm=ALGORITMA)
print("token  :", token)

# 2. Token terdiri dari tiga bagian yang dipisah titik: header.payload.tanda_tangan
header_b64, payload_b64, tanda_tangan = token.split(".")
print("bagian :", len(token.split(".")))


def baca_base64(teks: str) -> dict:
    teks += "=" * (-len(teks) % 4)  # base64 membutuhkan padding
    return json.loads(base64.urlsafe_b64decode(teks))


print("header :", baca_base64(header_b64))
print("payload:", baca_base64(payload_b64))  # bisa dibaca siapa saja: JWT ditandatangani, bukan dienkripsi

# 3. Memverifikasi token dengan kunci yang benar
print("valid  :", jwt.decode(token, KUNCI, algorithms=[ALGORITMA])["sub"])

# 4. Token yang diubah isinya
isi_palsu = baca_base64(payload_b64)
isi_palsu["sub"] = "admin"
payload_palsu = base64.urlsafe_b64encode(json.dumps(isi_palsu).encode()).decode().rstrip("=")
token_palsu = f"{header_b64}.{payload_palsu}.{tanda_tangan}"
try:
    jwt.decode(token_palsu, KUNCI, algorithms=[ALGORITMA])
except InvalidSignatureError as galat:
    print("diubah :", type(galat).__name__, "-", galat)

# 5. Kunci yang salah
try:
    jwt.decode(token, "kunci-lain-yang-salah-1234567890123456", algorithms=[ALGORITMA])
except InvalidSignatureError as galat:
    print("kunci salah:", type(galat).__name__)

# 6. Token kedaluwarsa
kedaluwarsa = jwt.encode(
    {"sub": "budi", "exp": datetime.now(timezone.utc) - timedelta(seconds=5)}, KUNCI, algorithm=ALGORITMA
)
try:
    jwt.decode(kedaluwarsa, KUNCI, algorithms=[ALGORITMA])
except ExpiredSignatureError as galat:
    print("kedaluwarsa:", type(galat).__name__, "-", galat)

# 7. Sembarang teks
try:
    jwt.decode("bukan-token", KUNCI, algorithms=[ALGORITMA])
except InvalidTokenError as galat:
    print("sembarang  :", type(galat).__name__, "-", galat)
