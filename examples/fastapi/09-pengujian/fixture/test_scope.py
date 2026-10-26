import pytest

jumlah_dibuat = {"per_fungsi": 0, "per_modul": 0}


@pytest.fixture  # scope bawaan: function (dibuat ulang untuk setiap pengujian)
def per_fungsi():
    jumlah_dibuat["per_fungsi"] += 1
    return jumlah_dibuat["per_fungsi"]


@pytest.fixture(scope="module")  # dibuat sekali untuk seluruh berkas ini
def per_modul():
    jumlah_dibuat["per_modul"] += 1
    return jumlah_dibuat["per_modul"]


def test_pertama(per_fungsi, per_modul):
    assert per_fungsi == 1
    assert per_modul == 1


def test_kedua(per_fungsi, per_modul):
    assert per_fungsi == 2  # dibuat lagi
    assert per_modul == 1  # dipakai ulang, tidak dibuat lagi
