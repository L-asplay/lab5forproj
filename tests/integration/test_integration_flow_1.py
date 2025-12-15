import pytest
pytestmark = pytest.mark.integration

def test_flow_create_search_stat_update_delete(integrated_services):
    db, rs, stat, search, user_id = integrated_services

    # 1) 创建两条记录（收入/支出）
    r1 = rs.create_record(user_id=user_id, amount=100.0, record_type="收入", category_name="工资", description="December salary")
    r2 = rs.create_record(user_id=user_id, amount=30.0, record_type="支出", category_name="餐饮", description="Lunch")

    # 2) 搜索：关键词命中 description/category
    hits = search.fuzzy_search(user_id=user_id, keyword="salary")
    assert any(x.id == r1.id for x in hits)

    hits2 = search.fuzzy_search(user_id=user_id, keyword="餐饮")
    assert any(x.id == r2.id for x in hits2)

    # 3) 统计：按当前月份统计（用 create_time 写入格式 "YYYY-MM-..."）
    month = r1.create_time.strftime("%Y-%m")
    stat_inc, total_inc = stat.category_statistics(user_id=user_id, month=month, record_type="收入")
    assert stat_inc.get("工资", 0) >= 100.0
    assert total_inc >= 100.0

    stat_exp, total_exp = stat.category_statistics(user_id=user_id, month=month, record_type="支出")
    assert stat_exp.get("餐饮", 0) >= 30.0
    assert total_exp >= 30.0

    # 4) 更新：修改金额与描述，统计结果应变化
    ok = rs.update_record(r2.id, user_id, amount=50.0, description="Lunch updated")
    assert ok is True

    stat_exp2, total_exp2 = stat.category_statistics(user_id=user_id, month=month, record_type="支出")
    assert stat_exp2.get("餐饮", 0) >= 50.0
    assert total_exp2 >= 50.0

    # 5) 删除：删除收入记录后，收入统计应降低
    assert rs.delete_record(r1.id, user_id) is True
    stat_inc2, total_inc2 = stat.category_statistics(user_id=user_id, month=month, record_type="收入")
    assert total_inc2 == 0.0
