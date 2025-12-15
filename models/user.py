from dataclasses import dataclass

@dataclass
class User:
    """用户实体类"""
    id: str  # 唯一标识
    username: str  # 用户名
    password: str  # 密码（简化存储，实际应加密）
    settings: dict  # 用户设置（如默认视图、显示格式等）

    def to_dict(self) -> dict:
        """转换为字典用于存储"""
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "settings": self.settings
        }

    @staticmethod
    def from_dict(data: dict) -> "User":
        """从字典解析为User对象"""
        return User(
            id=data["id"],
            username=data["username"],
            password=data["password"],
            settings=data["settings"]
        )