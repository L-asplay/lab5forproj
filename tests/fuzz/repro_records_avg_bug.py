import json
import os
import tempfile
from pathlib import Path

from utils.db_utils import DBUtils

import pytest

@pytest.fixture(autouse=True)
def _enable_lab5_fuzz_bug(monkeypatch):
    monkeypatch.setenv("LAB5_FUZZ_BUG", "1")

def main():
    os.environ["LAB5_FUZZ_BUG"] = "1"  # 复现时确保打开

    crash_path = Path("fuzz_results") / "records_avg_bug" / "crash_records.json"
    records = json.loads(crash_path.read_text(encoding="utf-8"))

    tmpdir = Path(tempfile.mkdtemp(prefix="lab5_repro_avg_"))
    db_dir = tmpdir / "db"
    db = DBUtils(db_path=str(db_dir))

    (db_dir / "records.json").write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")

    print("[REPRO] calling db.get_all('records') ...")
    db.get_all("records")  # 这里应崩溃（ZeroDivisionError 或 KeyError）

if __name__ == "__main__":
    main()
