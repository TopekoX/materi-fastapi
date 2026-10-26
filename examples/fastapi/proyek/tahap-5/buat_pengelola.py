"""Membuat akun pengelola pertama. Jalankan sekali setelah `alembic upgrade head`.

Contoh:
    python buat_pengelola.py rina "kata-sandi-rina-123"
Skrip memakai pengaturan yang sama dengan aplikasi (TUGASKU_SECRET_KEY harus terisi).
"""

import sys

from sqlmodel import Session, select

from app.database import engine
from app.keamanan import password_hash
from app.models import Pengguna

if len(sys.argv) != 3:
    raise SystemExit('Pemakaian: python buat_pengelola.py <nama_pengguna> "<kata_sandi>"')

nama_pengguna, kata_sandi = sys.argv[1], sys.argv[2]

with Session(engine) as session:
    if session.exec(select(Pengguna).where(Pengguna.nama_pengguna == nama_pengguna)).first():
        raise SystemExit(f"Pengguna '{nama_pengguna}' sudah ada.")
    pengguna = Pengguna(
        nama_pengguna=nama_pengguna,
        hash_kata_sandi=password_hash.hash(kata_sandi),
        peran="pengelola",
    )
    session.add(pengguna)
    session.commit()
    print(f"Pengelola '{nama_pengguna}' dibuat.")
