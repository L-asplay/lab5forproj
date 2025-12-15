from utils.db_utils import DBUtils
from services.record_service import RecordService
import pytest
pytestmark = pytest.mark.integration

def test_flow_persistence_reload(tmp_path):
    # 1) 第一次“运行”：创建 db + service，写入一条记录
    db_path = str(tmp_path / "db")
    db1 = DBUtils(db_path=db_path)

    user_id = "u_test_001"
    db1.insert("categories", {"id": "c_inc", "name": "工资", "type": "收入", "user_id": user_id, "create_time": "2025-01-01 00:00:00"})

    rs1 = RecordService()
    rs1.db = db1
    r = rs1.create_record(user_id=user_id, amount=88.0, record_type="收入", category_name="工资", description="persist")

    # 2) 第二次“运行”：重新 new DBUtils/RecordService（模拟程序重启）
    db2 = DBUtils(db_path=db_path)
    rs2 = RecordService()
    rs2.db = db2

    records = rs2.get_records(user_id=user_id)
    assert any(x.id == r.id and x.amount == 88.0 for x in records)
