# import uuid
# from datetime import datetime
# from models.record import Record, RecordType
# from models.category import Category
# from utils.db_utils import DBUtils

# class RecordService:
#     """记录CRUD服务"""
#     def __init__(self):
#         self.db = DBUtils()

#     def create_record(self, user_id: str, amount: float, record_type: str, 
#                      category_name: str, description: str) -> Record:
#         """创建新记录"""
#         # 验证分类是否存在
#         categories = self.db.get_by_condition(
#             "categories",
#             lambda c: c["user_id"] == user_id and c["type"] == record_type
#         )
#         if not any(c["name"] == category_name for c in categories):
#             raise ValueError(f"分类 {category_name} 不存在")
        
#         # 生成唯一ID
#         record_id = f"{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"
#         record = Record(
#             id=record_id,
#             amount=amount,
#             type=RecordType(record_type),
#             category=category_name,
#             description=description,
#             create_time=datetime.now(),
#             user_id=user_id
#         )
        
#         # 保存到数据库
#         self.db.insert("records", record.to_dict())
#         return record

#     def get_records(self, user_id: str, **filters) -> list[Record]:
#         """查询记录（支持多条件筛选）"""
#         conditions = [lambda r: r["user_id"] == user_id]
        
#         # 时间范围筛选（格式：YYYY-MM）
#         if "month" in filters:
#             target_month = filters["month"]
#             conditions.append(
#                 lambda r: r["create_time"].startswith(target_month)
#             )
        
#         # 类型筛选
#         if "type" in filters:
#             conditions.append(lambda r: r["type"] == filters["type"])
        
#         # 分类筛选
#         if "category" in filters:
#             conditions.append(lambda r: r["category"] == filters["category"])
        
#         # 金额范围筛选
#         if "min_amount" in filters:
#             conditions.append(lambda r: float(r["amount"]) >= filters["min_amount"])
#         if "max_amount" in filters:
#             conditions.append(lambda r: float(r["amount"]) <= filters["max_amount"])
        
#         # 执行查询
#         record_dicts = self.db.get_by_condition(
#             "records",
#             lambda r: all(cond(r) for cond in conditions)
#         )
#         return [Record.from_dict(rd) for rd in record_dicts]

#     def update_record(self, record_id: str, user_id: str, **new_data) -> bool:
#         """更新记录"""
#         # 验证记录归属
#         def condition(r):
#             return r["id"] == record_id and r["user_id"] == user_id
        
#         # 处理类型转换
#         if "type" in new_data:
#             new_data["type"] = RecordType(new_data["type"]).value
#         if "amount" in new_data:
#             new_data["amount"] = float(new_data["amount"])
        
#         return self.db.update("records", condition, new_data)

#     def delete_record(self, record_id: str, user_id: str) -> bool:
#         """删除记录"""
#         return self.db.delete(
#             "records",
#             lambda r: r["id"] == record_id and r["user_id"] == user_id
#         )

#     def create_category(self, user_id: str, name: str, type_: str) -> Category:
#         """创建分类"""
#         # 验证分类是否已存在
#         existing = self.db.get_by_condition(
#             "categories",
#             lambda c: c["user_id"] == user_id and c["name"] == name and c["type"] == type_
#         )
#         if existing:
#             raise ValueError(f"分类 {name} 已存在")
        
#         category_id = str(uuid.uuid4())[:12]
#         category = Category(
#             id=category_id,
#             name=name,
#             type=type_,
#             user_id=user_id,
#             create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         )
        
#         self.db.insert("categories", category.to_dict())
#         return category
# services/record_service.py
import uuid
from datetime import datetime
from typing import Optional

from models.record import Record, RecordType
from models.category import Category
from utils.db_utils import DBUtils


class RecordService:
    """记录CRUD服务"""

    def __init__(self, db: Optional[DBUtils] = None):
        self.db = db or DBUtils()

    def create_record(
        self,
        user_id: str,
        amount: float,
        record_type: str,
        category_name: str,
        description: str,
    ) -> Record:
        """创建新记录"""
        if record_type not in ("收入", "支出"):
            raise ValueError("record_type 必须是 '收入' 或 '支出'")
        if amount is None or float(amount) <= 0:
            raise ValueError("amount 必须为正数")

        categories = self.db.get_by_condition(
            "categories",
            lambda c: c["user_id"] == user_id and c["type"] == record_type,
        )
        if not any(c["name"] == category_name for c in categories):
            raise ValueError(f"分类 {category_name} 不存在")

        record_id = f"{int(datetime.now().timestamp())}_{str(uuid.uuid4())[:8]}"
        record = Record(
            id=record_id,
            amount=float(amount),
            type=RecordType(record_type),
            category=category_name,
            description=description,
            create_time=datetime.now(),
            user_id=user_id,
        )
        self.db.insert("records", record.to_dict())
        return record

    def get_records(self, user_id: str, **filters) -> list[Record]:
        conditions = [lambda r: r["user_id"] == user_id]

        if "month" in filters:
            target_month = filters["month"]
            conditions.append(lambda r: r["create_time"].startswith(target_month))

        if "type" in filters:
            conditions.append(lambda r: r["type"] == filters["type"])

        if "category" in filters:
            conditions.append(lambda r: r["category"] == filters["category"])

        if "min_amount" in filters:
            conditions.append(lambda r: float(r["amount"]) >= filters["min_amount"])
        if "max_amount" in filters:
            conditions.append(lambda r: float(r["amount"]) <= filters["max_amount"])

        record_dicts = self.db.get_by_condition("records", lambda r: all(cond(r) for cond in conditions))
        return [Record.from_dict(rd) for rd in record_dicts]

    def update_record(self, record_id: str, user_id: str, **new_data) -> bool:
        def condition(r):
            return r["id"] == record_id and r["user_id"] == user_id

        if "type" in new_data:
            if new_data["type"] not in ("收入", "支出"):
                raise ValueError("type 必须是 '收入' 或 '支出'")
            new_data["type"] = RecordType(new_data["type"]).value

        if "amount" in new_data:
            amt = float(new_data["amount"])
            if amt <= 0:
                raise ValueError("amount 必须为正数")
            new_data["amount"] = amt

        return self.db.update("records", condition, new_data)

    def delete_record(self, record_id: str, user_id: str) -> bool:
        return self.db.delete("records", lambda r: r["id"] == record_id and r["user_id"] == user_id)

    def create_category(self, user_id: str, name: str, type_: str) -> Category:
        if type_ not in ("收入", "支出"):
            raise ValueError("type_ 必须是 '收入' 或 '支出'")

        existing = self.db.get_by_condition(
            "categories",
            lambda c: c["user_id"] == user_id and c["name"] == name and c["type"] == type_,
        )
        if existing:
            raise ValueError(f"分类 {name} 已存在")

        category_id = str(uuid.uuid4())[:12]
        category = Category(
            id=category_id,
            name=name,
            type=type_,
            user_id=user_id,
            create_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self.db.insert("categories", category.to_dict())
        return category
