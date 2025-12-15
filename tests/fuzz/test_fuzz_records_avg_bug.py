import json
import os
import shutil
import tempfile
from pathlib import Path

from hypothesis import given, settings, strategies as st, HealthCheck

from utils.db_utils import DBUtils
import utils.db_utils as db_mod


def _close_leaks():
    leaked = getattr(db_mod, "_leaked_file_handles", None)
    if isinstance(leaked, list):
        for fh in leaked:
            try:
                fh.close()
            except Exception:
                pass
        leaked.clear()


# 生成“records 表”的合法 JSON：list[dict]，允许空列表、允许缺少 amount
records_strategy = st.lists(
    st.dictionaries(
        keys=st.sampled_from(["amount", "note"]),               # 可能不含 amount
        values=st.integers(min_value=-10, max_value=10),        # JSON 可序列化
        min_size=0,
        max_size=2,
    ),
    min_size=0,
    max_size=5,
)

@settings(
    max_examples=2000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(records=records_strategy)
def test_fuzz_records_avg_bug(records):
    # 每个样本独立临时目录，避免脏状态
    tmpdir = Path(tempfile.mkdtemp(prefix="lab5_fuzz_avg_"))
    try:
        db_dir = tmpdir / "db"
        db = DBUtils(db_path=str(db_dir))

        # 写入合法 JSON（确保能走到你插入的 avg 逻辑）
        (db_dir / "records.json").write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")

        try:
            db.get_all("records")
        except Exception:
            outdir = Path("fuzz_results") / "records_avg_bug"
            outdir.mkdir(parents=True, exist_ok=True)
            (outdir / "crash_records.json").write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
            raise
        finally:
            _close_leaks()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
