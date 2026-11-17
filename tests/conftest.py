import pytest
from backend import database

@pytest.fixture(autouse=True)
def isolated_sqlite(tmp_path, monkeypatch):
    monkeypatch.setattr(database,"DB_PATH",tmp_path/"isolated-q3.sqlite3")
    database.initialize()
