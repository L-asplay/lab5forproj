from datetime import datetime

from tests.conftest import insert_record


def test_category_statistics_basic(db, stat_engine, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    insert_record(db, rid="r2", user_id=user_id, amount=20, type_="收入", category="工资", desc="b", dt=datetime(2025, 12, 2, 10, 0))
    stat, total = stat_engine.category_statistics(user_id=user_id, month="2025-12", record_type="收入")
    assert stat["工资"] == 30
    assert total == 30


def test_category_statistics_multi_category(db, stat_engine, seed_categories, user_id):
    # 补充一个支出分类记录也不应算进收入统计
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    insert_record(db, rid="r2", user_id=user_id, amount=99, type_="支出", category="餐饮", desc="b", dt=datetime(2025, 12, 1, 10, 0))
    stat, total = stat_engine.category_statistics(user_id=user_id, month="2025-12", record_type="收入")
    assert stat == {"工资": 10.0}
    assert total == 10.0


def test_category_statistics_empty(db, stat_engine, seed_categories, user_id):
    stat, total = stat_engine.category_statistics(user_id=user_id, month="2025-12", record_type="收入")
    assert stat == {}
    assert total == 0.0


def test_rank_statistics_top_n(db, stat_engine, seed_categories, user_id):
    # 额外插入一个分类（直接写DB）
    db.insert("categories", {"id": "c3", "name": "兼职", "type": "收入", "user_id": user_id, "create_time": "2025-01-01 00:00:00"})
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    insert_record(db, rid="r2", user_id=user_id, amount=50, type_="收入", category="兼职", desc="b", dt=datetime(2025, 12, 1, 11, 0))
    rank = stat_engine.rank_statistics(user_id=user_id, month="2025-12", record_type="收入", top_n=1)
    assert rank == [("兼职", 50.0)]


def test_rank_statistics_order(db, stat_engine, seed_categories, user_id):
    db.insert("categories", {"id": "c3", "name": "兼职", "type": "收入", "user_id": user_id, "create_time": "2025-01-01 00:00:00"})
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    insert_record(db, rid="r2", user_id=user_id, amount=50, type_="收入", category="兼职", desc="b", dt=datetime(2025, 12, 1, 11, 0))
    rank = stat_engine.rank_statistics(user_id=user_id, month="2025-12", record_type="收入", top_n=5)
    assert rank[0][0] == "兼职" and rank[0][1] == 50.0


def test_time_period_statistics_has_12_months(stat_engine, user_id):
    stat = stat_engine.time_period_statistics(user_id=user_id, year="2025", record_type="收入")
    assert len(stat) == 12
    assert "2025-01" in stat and "2025-12" in stat


def test_time_period_statistics_sum_is_float(stat_engine, user_id):
    stat = stat_engine.time_period_statistics(user_id=user_id, year="2025", record_type="收入")
    assert all(isinstance(v, float) for v in stat.values())


def test_time_period_statistics_no_data_all_zero(stat_engine, user_id):
    stat = stat_engine.time_period_statistics(user_id=user_id, year="2025", record_type="收入")
    assert all(v == 0.0 for v in stat.values())


def test_category_statistics_month_boundary(db, stat_engine, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="收入", category="工资", desc="a", dt=datetime(2025, 12, 31, 23, 59))
    insert_record(db, rid="r2", user_id=user_id, amount=20, type_="收入", category="工资", desc="b", dt=datetime(2026, 1, 1, 0, 0))
    stat, total = stat_engine.category_statistics(user_id=user_id, month="2025-12", record_type="收入")
    assert total == 10.0


def test_category_statistics_type_filter_strict(db, stat_engine, seed_categories, user_id):
    insert_record(db, rid="r1", user_id=user_id, amount=10, type_="支出", category="餐饮", desc="a", dt=datetime(2025, 12, 1, 10, 0))
    stat, total = stat_engine.category_statistics(user_id=user_id, month="2025-12", record_type="收入")
    assert stat == {} and total == 0.0
