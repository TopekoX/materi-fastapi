"""Penanda pytest: skip, skipif, dan xfail."""

import sys

import pytest
from fastapi.testclient import TestClient

import main_mw

client = TestClient(main_mw.app)


@pytest.mark.skip(reason="fitur kompresi respons belum dibuat")
def test_response_dikompres():
    assert client.get("/halo", headers={"Accept-Encoding": "gzip"}).headers["content-encoding"] == "gzip"


@pytest.mark.skipif(sys.platform != "linux", reason="hanya relevan di Linux")
def test_khusus_linux():
    assert sys.platform == "linux"


@pytest.mark.xfail(reason="bug yang diketahui: /halo belum mengembalikan versi API", strict=True)
def test_versi_api_ada_di_response():
    assert client.get("/halo").json()["versi"] == "v1"
