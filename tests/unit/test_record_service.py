import pytest
from datetime import datetime

from tests.conftest import insert_record


def test_create_record_success(record_service, seed_categories, user_id):
    r = record_service.create_record(user_id=user_id, amount=100, record_type="收入", category_name="工资", description="x")
    assert r.amount == 100.0
    assert r.type.value == "收入"
    assert r.category == "工资"
    assert r.user_id == user_id


def test_create_record_invalid_type(record_service, seed_categories, user_id):
    with pytest.raises(ValueError):
        record_service.create_record(user_id=user_id, amount=1, record_type="IN", category_name="工资", description="x")


def test_create_record_invalid_amount_zero(record_service, seed_categories, user_id):
    with pytest.raises(ValueError):
        record_service.create_record(user_id=user_id, amount=0, record_type="收入", category_name="工资", description="x")


def test_create_record_invalid_amount_negative(record_service, seed_categories, user_id):
    with pytest.raises(ValueError):
        record_service.create_record(user_id=user_id, amount=-1, record_type="收入", category_name="工资", description="x")


def test_create_record_missing_category(record_service, seed_categories, user_id):
    with pytest.raises(ValueError):
        record_service.create_record(user_id=user_id, amount=1, record_type="收入", category_name="不存在", description="x")


def test_get_records_filter_month(db, record_service, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    insert_record(db, rid="r2", user_id=user_id, amount=20, type_="收入", category="工资", desc="b", dt=datetime(2025, 11, 1, 10, 0))
    rs = record_service.get_records(user_id=user_id, month="2025-12")
    assert {r.id for r in rs} == {"r1"}


def test_get_records_filter_type(db, record_service, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    insert_record(db, rid="r2", user_id=user_id, amount=20, type_="支出", category="餐饮", desc="b", dt=datetime(2025, 12, 2, 10, 0))
    rs = record_service.get_records(user_id=user_id, type="支出")
    assert [r.id for r in rs] == ["r2"]


def test_get_records_filter_category(db, record_service, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="支出", category="餐饮", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    rs = record_service.get_records(user_id=user_id, category="餐饮")
    assert len(rs) == 1 and rs[0].id == "r1"


def test_get_records_amount_range(db, record_service, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    insert_record(db, rid="r2", user_id=user_id, amount=99, type_="收入", category="工资", desc="b", dt=datetime(2025, 12, 1, 11, 0))
    rs = record_service.get_records(user_id=user_id, min_amount=50, max_amount=120)
    assert {r.id for r in rs} == {"r2"}


def test_update_record_success(db, record_service, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    ok = record_service.update_record("r1", user_id, amount=33, type="收入", description="zz")
    assert ok is True
    rs = record_service.get_records(user_id=user_id)
    assert rs[0].amount == 33.0 and rs[0].description == "zz"


def test_update_record_invalid_amount(db, record_service, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    with pytest.raises(ValueError):
        record_service.update_record("r1", user_id, amount=0)


def test_delete_record_success(db, record_service, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    assert record_service.delete_record("r1", user_id) is True
    assert record_service.get_records(user_id=user_id) == []
