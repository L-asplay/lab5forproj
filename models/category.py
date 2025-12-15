from dataclasses import dataclass

@dataclass
class Category:
    """分类实体类"""
    id: str  # 唯一标识
    name: str  # 分类名称
    type: str  # 关联收支类型（收入/支出）
    user_id: str  # 所属用户ID
    create_time: str  # 创建时间（字符串格式）

    def to_dict(self) -> dict:
        """转换为字典用于存储"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "user_id": self.user_id,
            "create_time": self.create_time
        }

    @staticmethod
    def from_dict(data: dict) -> "Category":
        """从字典解析为Category对象"""
        return Category(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            user_id=data["user_id"],
            create_time=data["create_time"]
        )