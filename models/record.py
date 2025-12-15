from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class RecordType(Enum):
    """收支类型枚举"""
    INCOME = "收入"
    EXPENSE = "支出"

@dataclass
class Record:
    """记录实体类"""
    id: str  # 唯一标识（格式：时间戳+随机数）
    amount: float  # 金额
    type: RecordType  # 收支类型
    category: str  # 分类名称
    description: str  # 描述
    create_time: datetime  # 创建时间
    user_id: str  # 所属用户ID

    def to_dict(self) -> dict:
        """转换为字典用于存储"""
        return {
            "id": self.id,
            "amount": self.amount,
            "type": self.type.value,
            "category": self.category,
            "description": self.description,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": self.user_id
        }

    @staticmethod
    def from_dict(data: dict) -> "Record":
        """从字典解析为Record对象"""
        return Record(
            id=data["id"],
            amount=float(data["amount"]),
            type=RecordType(data["type"]),
            category=data["category"],
            description=data["description"],
            create_time=datetime.strptime(data["create_time"], "%Y-%m-%d %H:%M:%S"),
            user_id=data["user_id"]
        )