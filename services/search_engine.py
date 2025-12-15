# from models.record import Record
# from services.record_service import RecordService

# class SearchEngine:
#     """搜索引擎"""
#     def __init__(self):
#         self.record_service = RecordService()

#     def fuzzy_search(self, user_id: str, keyword: str) -> list[Record]:
#         """关键词模糊搜索（匹配描述、分类）"""
#         all_records = self.record_service.get_records(user_id=user_id)
#         keyword = keyword.lower()
#         return [
#             record for record in all_records
#             if keyword in record.description.lower() or keyword in record.category.lower()
#         ]

#     def advanced_search(self, user_id: str, **filters) -> list[Record]:
#         """高级搜索（支持多条件组合）"""
#         return self.record_service.get_records(user_id=user_id, **filters)

# services/search_engine.py
from typing import Optional
from models.record import Record
from services.record_service import RecordService


class SearchEngine:
    def __init__(self, record_service: Optional[RecordService] = None):
        self.record_service = record_service or RecordService()

    def fuzzy_search(self, user_id: str, keyword: str) -> list[Record]:
        all_records = self.record_service.get_records(user_id=user_id)
        keyword = (keyword or "").lower()
        return [r for r in all_records if keyword in r.description.lower() or keyword in r.category.lower()]

    def advanced_search(self, user_id: str, **filters) -> list[Record]:
        return self.record_service.get_records(user_id=user_id, **filters)
