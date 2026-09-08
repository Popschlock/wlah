import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import wlah_check  # noqa: E402

FIX = ROOT / "tests" / "fixtures"

@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path); return tmp_path
