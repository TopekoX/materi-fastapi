"""Pemeriksa checklist rilis (heuristik berbasis teks).

Pemakaian:  python periksa_rilis.py <folder-proyek>

Skrip hanya membaca berkas. Ia tidak menjalankan aplikasi, Docker, atau pengujian,
sehingga LULUS di sini bukan jaminan aman: ini penyaring kesalahan yang paling umum.
"""

import re
import sys
from pathlib import Path
from typing import Callable, NamedTuple

NAMA_RAHASIA = r"(secret|password|kata_sandi|token|api_key)"


class Hasil(NamedTuple):
    nama: str
    status: str  # "LULUS", "GAGAL", atau "LEWAT" (tidak berlaku)
    catatan: str


def berkas_python(folder: Path) -> list[Path]:
    """Semua .py aplikasi, tanpa folder lingkungan virtual dan berkas pengujian."""
    hasil = []
    for p in folder.rglob("*.py"):
        if any(b in {".venv", "venv", "__pycache__", "alembic"} for b in p.parts):
            continue
        if p.name.startswith("test_") or "tests" in p.parts or p.name == "conftest.py":
            continue
        hasil.append(p)
    return hasil


def cari_gitignore(folder: Path) -> Path | None:
    for induk in [folder, *folder.parents][:5]:
        if (induk / ".gitignore").is_file():
            return induk / ".gitignore"
    return None


def baris_aktif(path: Path) -> list[str]:
    return [b.strip() for b in path.read_text(encoding="utf-8").splitlines() if b.strip() and not b.strip().startswith("#")]


def periksa_gitignore(folder: Path) -> Hasil:
    nama = ".env dan *.db diabaikan Git"
    git = cari_gitignore(folder)
    if git is None:
        return Hasil(nama, "GAGAL", "tidak ada .gitignore")
    isi = baris_aktif(git)
    kurang = [x for x in (".env", "*.db") if x not in isi]
    return Hasil(nama, "GAGAL" if kurang else "LULUS", f"belum ada di {git.name}: {', '.join(kurang)}" if kurang else str(git))


def periksa_dockerignore(folder: Path) -> Hasil:
    nama = ".dockerignore menutup .env"
    if not (folder / "Dockerfile").is_file():
        return Hasil(nama, "LEWAT", "tidak ada Dockerfile")
    di = folder / ".dockerignore"
    if not di.is_file():
        return Hasil(nama, "GAGAL", "tidak ada .dockerignore")
    return Hasil(nama, "LULUS" if ".env" in baris_aktif(di) else "GAGAL", ".dockerignore ada")


def periksa_user_bukan_root(folder: Path) -> Hasil:
    nama = "container berjalan sebagai non-root"
    df = folder / "Dockerfile"
    if not df.is_file():
        return Hasil(nama, "LEWAT", "tidak ada Dockerfile")
    pengguna = re.findall(r"^\s*USER\s+(\S+)", df.read_text(encoding="utf-8"), flags=re.M)
    if not pengguna or pengguna[-1] in {"root", "0"}:
        return Hasil(nama, "GAGAL", "tidak ada instruksi USER non-root")
    return Hasil(nama, "LULUS", f"USER {pengguna[-1]}")


def periksa_rahasia_di_dockerfile(folder: Path) -> Hasil:
    nama = "tidak ada rahasia di Dockerfile/Compose"
    ditemukan = []
    for fn in ("Dockerfile", "docker-compose.yml", "compose.yaml"):
        p = folder / fn
        if not p.is_file():
            continue
        for b in p.read_text(encoding="utf-8").splitlines():
            if re.search(NAMA_RAHASIA, b, flags=re.I) and re.search(r"(ENV|ARG|:|=)\s*\S+", b):
                nilai = re.split(r"[:=]", b, maxsplit=1)[-1].strip().strip("\"'")
                if nilai and not nilai.startswith("${") and not b.strip().startswith("#"):
                    ditemukan.append(f"{fn}: {b.strip()}")
    return Hasil(nama, "GAGAL" if ditemukan else "LULUS", "; ".join(ditemukan) if ditemukan else "bersih")


def periksa_requirements_terkunci(folder: Path) -> Hasil:
    nama = "versi dependensi dikunci (==)"
    req = folder / "requirements.txt"
    if not req.is_file():
        return Hasil(nama, "GAGAL", "tidak ada requirements.txt di folder ini")
    longgar = [b for b in baris_aktif(req) if "==" not in b]
    return Hasil(nama, "GAGAL" if longgar else "LULUS", ", ".join(longgar) if longgar else f"{len(baris_aktif(req))} paket")


def periksa_cors(folder: Path) -> Hasil:
    nama = "CORS tidak memakai '*' di kode"
    cacat = [
        p.name
        for p in berkas_python(folder)
        if re.search(r"allow_origins\s*=\s*\[\s*[\"']\*[\"']\s*\]", p.read_text(encoding="utf-8"))
    ]
    return Hasil(nama, "GAGAL" if cacat else "LULUS", ", ".join(cacat) if cacat else "tidak ditemukan")


def periksa_rahasia_di_kode(folder: Path) -> Hasil:
    nama = "tidak ada rahasia tertulis di kode"
    pola = re.compile(rf"(secret|password|kata_sandi|api_key)\w*\s*(:\s*\w+\s*)?=\s*[\"'][^\"']{{6,}}[\"']", re.I)
    ditemukan = [
        f"{p.name}:{no}"
        for p in berkas_python(folder)
        for no, b in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
        if pola.search(b)
    ]
    return Hasil(nama, "GAGAL" if ditemukan else "LULUS", ", ".join(ditemukan) if ditemukan else "tidak ditemukan")


def periksa_ada_pengujian(folder: Path) -> Hasil:
    nama = "ada pengujian"
    ada = any(folder.rglob("test_*.py")) or (folder / "tests").is_dir()
    return Hasil(nama, "LULUS" if ada else "GAGAL", "berkas test_*.py ditemukan" if ada else "tidak ada")


def periksa_migrasi(folder: Path) -> Hasil:
    nama = "ada konfigurasi migrasi (Alembic)"
    ada = (folder / "alembic.ini").is_file()
    return Hasil(nama, "LULUS" if ada else "GAGAL", "alembic.ini ada" if ada else "tidak ada alembic.ini")


PEMERIKSA: list[Callable[[Path], Hasil]] = [
    periksa_gitignore,
    periksa_dockerignore,
    periksa_user_bukan_root,
    periksa_rahasia_di_dockerfile,
    periksa_requirements_terkunci,
    periksa_cors,
    periksa_rahasia_di_kode,
    periksa_ada_pengujian,
    periksa_migrasi,
]


def jalankan(folder: Path) -> list[Hasil]:
    return [periksa(folder) for periksa in PEMERIKSA]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Pemakaian: python periksa_rilis.py <folder-proyek>")
        return 2
    folder = Path(argv[1]).resolve()
    if not folder.is_dir():
        print(f"Folder tidak ditemukan: {folder}")
        return 2
    hasil = jalankan(folder)
    for h in hasil:
        print(f"[{h.status:5}] {h.nama} - {h.catatan}")
    gagal = sum(h.status == "GAGAL" for h in hasil)
    print(f"\n{gagal} gagal dari {len(hasil)} pemeriksaan")
    return 1 if gagal else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
