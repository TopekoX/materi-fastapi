from pathlib import Path

import pytest

import periksa_rilis as pr


def tulis(folder: Path, nama: str, isi: str) -> None:
    (folder / nama).parent.mkdir(parents=True, exist_ok=True)
    (folder / nama).write_text(isi, encoding="utf-8")


def status(hasil: list[pr.Hasil], potongan_nama: str) -> str:
    return next(h.status for h in hasil if potongan_nama in h.nama)


@pytest.fixture
def proyek_baik(tmp_path):
    tulis(tmp_path, ".gitignore", ".env\n*.db\n")
    tulis(tmp_path, "Dockerfile", "FROM python:3.14\nUSER aplikasi\n")
    tulis(tmp_path, ".dockerignore", ".env\n.venv\n")
    tulis(tmp_path, "requirements.txt", "fastapi==0.162.0\n# komentar\n")
    tulis(tmp_path, "alembic.ini", "[alembic]\n")
    tulis(tmp_path, "app/main.py", "x = 1\n")
    tulis(tmp_path, "tests/test_a.py", "def test_a(): pass\n")
    return tmp_path


def test_proyek_baik_lulus_semua(proyek_baik):
    assert [h.status for h in pr.jalankan(proyek_baik)] == ["LULUS"] * len(pr.PEMERIKSA)


def test_gitignore_tanpa_env_gagal(proyek_baik):
    tulis(proyek_baik, ".gitignore", "*.db\n")
    assert status(pr.jalankan(proyek_baik), ".env dan *.db") == "GAGAL"


def test_dockerignore_hilang_gagal(proyek_baik):
    (proyek_baik / ".dockerignore").unlink()
    assert status(pr.jalankan(proyek_baik), ".dockerignore") == "GAGAL"


def test_tanpa_dockerfile_dilewati(proyek_baik):
    (proyek_baik / "Dockerfile").unlink()
    hasil = pr.jalankan(proyek_baik)
    assert status(hasil, ".dockerignore") == "LEWAT"
    assert status(hasil, "non-root") == "LEWAT"


@pytest.mark.parametrize("isi", ["FROM python:3.14\n", "FROM python:3.14\nUSER root\n", "FROM x\nUSER 0\n"])
def test_container_root_gagal(proyek_baik, isi):
    tulis(proyek_baik, "Dockerfile", isi)
    assert status(pr.jalankan(proyek_baik), "non-root") == "GAGAL"


def test_rahasia_di_dockerfile_gagal(proyek_baik):
    tulis(proyek_baik, "Dockerfile", "FROM x\nUSER aplikasi\nENV TUGASKU_SECRET_KEY=abc123456\n")
    assert status(pr.jalankan(proyek_baik), "Dockerfile/Compose") == "GAGAL"


def test_rujukan_variabel_di_compose_boleh(proyek_baik):
    tulis(proyek_baik, "docker-compose.yml", "services:\n  api:\n    environment:\n      TUGASKU_SECRET_KEY: ${TUGASKU_SECRET_KEY:?wajib}\n")
    assert status(pr.jalankan(proyek_baik), "Dockerfile/Compose") == "LULUS"


def test_versi_longgar_gagal(proyek_baik):
    tulis(proyek_baik, "requirements.txt", "fastapi>=0.100\nuvicorn==0.54.0\n")
    hasil = pr.jalankan(proyek_baik)
    assert status(hasil, "versi dependensi") == "GAGAL"
    assert "fastapi>=0.100" in next(h.catatan for h in hasil if "versi dependensi" in h.nama)


def test_cors_bintang_gagal(proyek_baik):
    tulis(proyek_baik, "app/main.py", 'app.add_middleware(CORSMiddleware, allow_origins=["*"])\n')
    assert status(pr.jalankan(proyek_baik), "CORS") == "GAGAL"


def test_rahasia_tertulis_di_kode_gagal(proyek_baik):
    tulis(proyek_baik, "app/config.py", 'secret_key: str = "kunci-yang-bocor"\n')
    assert status(pr.jalankan(proyek_baik), "rahasia tertulis") == "GAGAL"


def test_token_type_bukan_rahasia(proyek_baik):
    tulis(proyek_baik, "app/a.py", 'x = Token(token_type="bearer")\n')
    assert status(pr.jalankan(proyek_baik), "rahasia tertulis") == "LULUS"


def test_rahasia_di_berkas_uji_diabaikan(proyek_baik):
    tulis(proyek_baik, "tests/test_b.py", 'password = "kata-sandi-uji-123"\n')
    assert status(pr.jalankan(proyek_baik), "rahasia tertulis") == "LULUS"


def test_tanpa_pengujian_dan_migrasi_gagal(proyek_baik):
    (proyek_baik / "tests" / "test_a.py").unlink()
    (proyek_baik / "tests").rmdir()
    (proyek_baik / "alembic.ini").unlink()
    hasil = pr.jalankan(proyek_baik)
    assert status(hasil, "ada pengujian") == "GAGAL"
    assert status(hasil, "Alembic") == "GAGAL"


def test_main_kode_keluar(proyek_baik, capsys):
    assert pr.main(["x", str(proyek_baik)]) == 0
    (proyek_baik / "requirements.txt").write_text("fastapi\n", encoding="utf-8")
    assert pr.main(["x", str(proyek_baik)]) == 1
    assert "1 gagal dari" in capsys.readouterr().out
    assert pr.main(["x"]) == 2
    assert pr.main(["x", str(proyek_baik / "tidak-ada")]) == 2
