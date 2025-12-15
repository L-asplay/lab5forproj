# from typing import Dict, Tuple
# from models.record import Record
# from services.record_service import RecordService

# class StatisticsEngine:
#     """统计分析引擎"""
#     def __init__(self):
#         self.record_service = RecordService()

#     def category_statistics(self, user_id: str, month: str, record_type: str) -> Tuple[Dict[str, float], float]:
#         """按分类统计金额"""
#         # 获取目标月份的记录
#         records = self.record_service.get_records(
#             user_id=user_id,
#             month=month,
#             type=record_type
#         )
        
#         # 按分类汇总
#         stat_result = {}
#         total_amount = 0.0
#         for record in records:
#             category = record.category
#             if category not in stat_result:
#                 stat_result[category] = 0.0
#             stat_result[category] += record.amount
#             total_amount += record.amount
        
#         return stat_result, total_amount

#     def rank_statistics(self, user_id: str, month: str, record_type: str, top_n: int = 5) -> list[Tuple[str, float]]:
#         """收支排行统计（按金额降序）"""
#         stat_result, _ = self.category_statistics(user_id, month, record_type)
#         # 排序并取前N名
#         sorted_rank = sorted(stat_result.items(), key=lambda x: x[1], reverse=True)[:top_n]
#         return sorted_rank

#     def time_period_statistics(self, user_id: str, year: str, record_type: str) -> Dict[str, float]:
#         """按月份统计年度收支"""
#         stat_result = {}
#         # 遍历12个月
#         for month in [f"{year}-{str(i).zfill(2)}" for i in range(1, 13)]:
#             _, total = self.category_statistics(user_id, month, record_type)
#             stat_result[month] = total
#         return stat_result

# services/statistics_engine.py
from typing import Dict, Tuple, Optional
from services.record_service import RecordService


class StatisticsEngine:
    def __init__(self, record_service: Optional[RecordService] = None):
        self.record_service = record_service or RecordService()

    def category_statistics(self, user_id: str, month: str, record_type: str) -> Tuple[Dict[str, float], float]:
        records = self.record_service.get_records(user_id=user_id, month=month, type=record_type)
        stat_result: Dict[str, float] = {}
        total_amount = 0.0
        for record in records:
            stat_result[record.category] = stat_result.get(record.category, 0.0) + record.amount
            total_amount += record.amount
        return stat_result, total_amount

    def rank_statistics(self, user_id: str, month: str, record_type: str, top_n: int = 5):
        stat_result, _ = self.category_statistics(user_id, month, record_type)
        return sorted(stat_result.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def time_period_statistics(self, user_id: str, year: str, record_type: str) -> Dict[str, float]:
        stat_result: Dict[str, float] = {}
        for month in [f"{year}-{str(i).zfill(2)}" for i in range(1, 13)]:
            _, total = self.category_statistics(user_id, month, record_type)
            stat_result[month] = total
        return stat_result
