# Dockerfile untuk TugasKU API (versi modular, proyek tahap 5).
# Letakkan di folder yang sama dengan requirements.txt, alembic.ini, alembic/, dan app/.
#
# CATATAN: Dockerfile ini BELUM dibangun atau dijalankan saat materi ditulis,
# karena daemon Docker tidak aktif pada mesin penulis. Lihat penjelasan di halaman Container.

FROM python:3.14

WORKDIR /code

# Salin daftar dependensi lebih dulu. Lapisan ini hanya dibangun ulang bila requirements.txt berubah.
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Salin kode aplikasi dan migrasi. Bagian ini paling sering berubah, jadi ditaruh paling akhir.
COPY ./app /code/app
COPY ./alembic.ini /code/alembic.ini
COPY ./alembic /code/alembic

# Jalankan sebagai pengguna biasa, bukan root
RUN useradd --create-home --uid 1000 aplikasi \
    && mkdir /data \
    && chown aplikasi:aplikasi /data
USER aplikasi

# Basis data SQLite disimpan di /data, yang dipasang sebagai volume agar data tidak hilang
ENV TUGASKU_DATABASE_URL=sqlite:////data/database.db
VOLUME ["/data"]

# Agar perintah alembic yang dijalankan dari folder lain (/data) tetap bisa mengimpor paket "app"
ENV PYTHONPATH=/code

EXPOSE 8000

# Bentuk exec (dengan tanda kurung siku): memungkinkan penghentian baik-baik dan menjalankan lifespan.
# Satu proses per container; replikasi diserahkan ke pengelola container.
CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--proxy-headers"]
