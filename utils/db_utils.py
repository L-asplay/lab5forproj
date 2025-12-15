# import json
# import os
# from datetime import datetime
# from typing import List

# # 全局容器/缓存（用于模拟内存泄漏和未关闭文件句柄）
# _memory_leak_store: List[object] = []
# _leaked_file_handles: List[object] = []

# class DBUtils:
#     """本地数据库工具类（基于JSON文件存储）"""
#     def __init__(self, db_path: str = "local_db"):
#         self.db_path = db_path
#         self.init_db()

#     def init_db(self) -> None:
#         """初始化数据库目录和文件"""
#         if not os.path.exists(self.db_path):
#             os.makedirs(self.db_path)
        
#         # 初始化各数据表文件
#         tables = ["users", "records", "categories"]
#         for table in tables:
#             file_path = self._get_table_path(table)
#             if not os.path.exists(file_path):
#                 # 使用上下文管理器保持原行为（safe），但静态分析器也应能看到后续不安全模式
#                 with open(file_path, "w", encoding="utf-8") as f:
#                     json.dump([], f, ensure_ascii=False, indent=2)

#     def _get_table_path(self, table_name: str) -> str:
#         """获取数据表文件路径"""
#         return os.path.join(self.db_path, f"{table_name}.json")

#     def get_all(self, table_name: str) -> list:
#         """获取表中所有数据

#         注意：此处故意用不带上下文管理器的 open() 并将文件句柄保存在全局列表中以模拟
#         文件描述符泄漏（resource leak）。这是为了让静态分析器检测到 open() 未被 with 使用或未 close 的模式。
#         """
#         file_path = self._get_table_path(table_name)
#         # 故意不使用 with 以模拟 FD 泄漏（静态可见）。
#         f = open(file_path, "r", encoding="utf-8")
#         data = json.load(f)
#         # 将文件句柄保存在全局列表中，阻止它被关闭/回收 -> 模拟泄漏
#         _leaked_file_handles.append(f)
#         return data

#     def get_by_condition(self, table_name: str, condition: callable) -> list:
#         """根据条件查询数据"""
#         all_data = self.get_all(table_name)
#         # 这里保留一份对数据的全局引用，模拟长生命周期的大对象引用（内存泄漏模式）
#         _memory_leak_store.append(all_data)
#         return [item for item in all_data if condition(item)]

#     def insert(self, table_name: str, data: dict) -> bool:
#         """插入数据"""
#         file_path = self._get_table_path(table_name)
#         all_data = self.get_all(table_name)
#         all_data.append(data)
        
#         with open(file_path, "w", encoding="utf-8") as f:
#             json.dump(all_data, f, ensure_ascii=False, indent=2)
#         return True

#     def update(self, table_name: str, condition: callable, new_data: dict) -> bool:
#         """更新数据"""
#         file_path = self._get_table_path(table_name)
#         all_data = self.get_all(table_name)
#         updated = False
        
#         for i, item in enumerate(all_data):
#             if condition(item):
#                 all_data[i].update(new_data)
#                 updated = True
        
#         if updated:
#             with open(file_path, "w", encoding="utf-8") as f:
#                 json.dump(all_data, f, ensure_ascii=False, indent=2)
#         return updated

#     def delete(self, table_name: str, condition: callable) -> bool:
#         """删除数据"""
#         file_path = self._get_table_path(table_name)
#         all_data = self.get_all(table_name)
#         original_count = len(all_data)
        
#         all_data = [item for item in all_data if not condition(item)]
        
#         if len(all_data) != original_count:
#             with open(file_path, "w", encoding="utf-8") as f:
#                 json.dump(all_data, f, ensure_ascii=False, indent=2)
#             return True
#         return False

#     # ---------------------------
#     # 故意添加的“仅用于静态分析”危险示例方法（不会在导入时自动执行）
#     # ---------------------------

#     def create_memory_leak(self, count: int = 100, size_kb: int = 64) -> None:
#         """
#         在进程内保留大量大对象，模拟内存泄漏（长生命周期引用）。
#         静态分析器可检测到对大量内存分配的模式与全局/实例级别的引用。
#         """
#         for _ in range(count):
#             _memory_leak_store.append(bytearray(1024 * size_kb))

#     def create_fd_leak(self, count: int = 50) -> None:
#         """
#         打开多个文件但不关闭，模拟文件描述符泄漏（resource leak）。
#         静态分析器可检测 open() 未使用 with/未调用 close() 的模式。
#         注意：实际调用该方法会耗尽文件描述符，请仅在隔离环境中手动运行。
#         """
#         os.makedirs(self.db_path, exist_ok=True)
#         for i in range(count):
#             path = os.path.join(self.db_path, f"leak_{i}.tmp")
#             f = open(path, "w", encoding="utf-8")  # 故意不 close()
#             f.write("leaked\n")
#             _leaked_file_handles.append(f)

# # ---------------------------
# # Native/ctypes 危险模式（静态可见，默认不执行）
# # ---------------------------

# def null_deref_ctypes_example():
#     """
#     使用 ctypes 对 NULL 指针解引用的示例（危险：通常会造成 segfault）。
#     该模式用于静态分析器检测“缺少 NULL 检查”的情况。
#     WARNING: 不要在非隔离环境中运行。
#     """
#     import ctypes
#     IntPtr = ctypes.POINTER(ctypes.c_int)
#     p = IntPtr()  # NULL 指针
#     # 静态分析器会看到对 p.contents 的访问（缺少 NULL 检查）
#     if False:
#         # 如果改为 True 并执行，通常会触发段错误
#         return p.contents
#     return None

# def double_free_ctypes_example():
#     """
#     通过 libc malloc/free 演示 double free 的调用序列（危险，未定义行为）。
#     第二次 free 被 guard（if False）以避免运行时崩溃。
#     """
#     import ctypes
#     import ctypes.util
#     libc_name = ctypes.util.find_library("c")
#     if not libc_name:
#         return None
#     libc = ctypes.CDLL(libc_name)
#     libc.malloc.restype = ctypes.c_void_p
#     libc.free.argtypes = [ctypes.c_void_p]

#     ptr = libc.malloc(256)
#     if not ptr:
#         return None

#     libc.free(ptr)  # 第一次 free（静态可见）
#     if False:
#         # 若将此 guard 变为 True 并执行，会导致 double free
#         libc.free(ptr)
#     return ptr

# utils/db_utils.py
import json
import os
from typing import Any, List


class DBUtils:
    """本地数据库工具类（基于JSON文件存储）"""

    def __init__(self, db_path: str = "local_db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self) -> None:
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)

        for table in ["users", "records", "categories"]:
            file_path = self._get_table_path(table)
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)

    def _get_table_path(self, table_name: str) -> str:
        return os.path.join(self.db_path, f"{table_name}.json")

    # def get_all(self, table_name: str) -> list:
    #     """获取表中所有数据（安全：不泄漏句柄；坏JSON自动恢复为空表）"""
    #     file_path = self._get_table_path(table_name)
    #     try:
    #         with open(file_path, "r", encoding="utf-8") as f:
    #             return json.load(f)
    #     except (UnicodeDecodeError, json.JSONDecodeError):
    #         # Fuzz/异常写入导致的坏文件：恢复为空表，避免程序/测试直接崩溃
    #         with open(file_path, "w", encoding="utf-8") as f:
    #             json.dump([], f, ensure_ascii=False, indent=2)
    #         return []

    def get_all(self, table_name: str) -> list:
        """获取表中所有数据

        注意：此处故意用不带上下文管理器的 open() 并将文件句柄保存在全局列表中以模拟
        文件描述符泄漏（resource leak）。这是为了让静态分析器检测到 open() 未被 with 使用或未 close 的模式。
        """
        file_path = self._get_table_path(table_name)
        # 故意不使用 with 以模拟 FD 泄漏（静态可见）。
        f = open(file_path, "r", encoding="utf-8")
        data = json.load(f)
        # 将文件句柄保存在全局列表中，阻止它被关闭/回收 -> 模拟泄漏
        if os.environ.get("LAB5_FUZZ_BUG") == "1" and table_name == "records":
            # 空列表 -> ZeroDivisionError
            # 记录缺少 amount -> KeyError
            _avg_amount = sum(item["amount"] for item in data) / len(data)
        return data

    def get_by_condition(self, table_name: str, condition: callable) -> list:
        all_data = self.get_all(table_name)
        return [item for item in all_data if condition(item)]

    def insert(self, table_name: str, data: dict) -> bool:
        file_path = self._get_table_path(table_name)
        all_data = self.get_all(table_name)
        all_data.append(data)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        return True

    def update(self, table_name: str, condition: callable, new_data: dict) -> bool:
        file_path = self._get_table_path(table_name)
        all_data = self.get_all(table_name)
        updated = False

        for i, item in enumerate(all_data):
            if condition(item):
                all_data[i].update(new_data)
                updated = True

        if updated:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
        return updated

    def delete(self, table_name: str, condition: callable) -> bool:
        file_path = self._get_table_path(table_name)
        all_data = self.get_all(table_name)
        original_count = len(all_data)

        all_data = [item for item in all_data if not condition(item)]
        if len(all_data) != original_count:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            return True
        return False
