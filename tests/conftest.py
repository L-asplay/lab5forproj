import pytest

from utils.db_utils import DBUtils
from services.record_service import RecordService
from services.statistics_engine import StatisticsEngine
from services.search_engine import SearchEngine

# 1) 默认关闭你注入的 fuzz bug，避免污染单元/集成测试
@pytest.fixture(autouse=True)
def _disable_lab5_fuzz_bug(monkeypatch):
    monkeypatch.delenv("LAB5_FUZZ_BUG", raising=False)

# 2) 单元测试用：独立临时 DB
@pytest.fixture()
def db(tmp_path):
    return DBUtils(db_path=str(tmp_path / "db"))

@pytest.fixture()
def user_id():
    return "u_test_001"

@pytest.fixture()
def seed_categories(db, user_id):
    db.insert("categories", {"id": "c_inc", "name": "工资", "type": "收入", "user_id": user_id, "create_time": "2025-01-01 00:00:00"})
    db.insert("categories", {"id": "c_exp", "name": "餐饮", "type": "支出", "user_id": user_id, "create_time": "2025-01-01 00:00:00"})

@pytest.fixture()
def record_service(db):
    rs = RecordService()
    rs.db = db
    return rs

@pytest.fixture()
def stat_engine(record_service):
    stt = StatisticsEngine()
    stt.record_service = record_service
    return stt

@pytest.fixture()
def search_engine(record_service):
    se = SearchEngine()
    se.record_service = record_service
    return se

# 3) 如果你的 unit tests 需要 insert_record，就放这里
from datetime import datetime
from models.record import Record, RecordType

def insert_record(db, *, rid: str, user_id: str, amount: float, type_: str, category: str, desc: str, dt: datetime):
    r = Record(
        id=rid,
        amount=float(amount),
        type=RecordType(type_),
        category=category,
        description=desc,
        create_time=dt,
        user_id=user_id,
    )
    db.insert("records", r.to_dict())
    return r

# 4) 集成测试夹具（如果你之前写过 integrated_services，可用这个版本）
@pytest.fixture()
def integrated_services(tmp_path):
    db = DBUtils(db_path=str(tmp_path / "db"))

    rs = RecordService()
    rs.db = db

    stat = StatisticsEngine()
    stat.record_service = rs

    search = SearchEngine()
    search.record_service = rs

    uid = "u_test_001"
    db.insert("categories", {"id": "c_inc", "name": "工资", "type": "收入", "user_id": uid, "create_time": "2025-01-01 00:00:00"})
    db.insert("categories", {"id": "c_exp", "name": "餐饮", "type": "支出", "user_id": uid, "create_time": "2025-01-01 00:00:00"})

    return db, rs, stat, search, uid
