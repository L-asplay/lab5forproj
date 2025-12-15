# from models.user import User
# from views.main_view import MainView
# from utils.db_utils import DBUtils

# # 注：以下为有意植入的“测试用缺陷/示例”，仅供静态分析使用。
# #       - 包含 Python 层的引用/资源泄漏模式（memory leak, file descriptor leak）
# #       - 包含 ctypes 层面的危险模式（NULL 解引用、double free），但这些 native 调用被保护为默认不执行以避免运行时崩溃
# # 切勿在生产或未隔离的环境中执行这些示例（尤其是未注释掉的危险调用）。

# import os
# from typing import List

# # ====== 注入的全局变量/容器（用于制造泄漏模式） ======
# # 全局保留大对象以模拟引用导致的内存泄漏
# _injected_leak_store: List[object] = []

# # 全局保存打开的文件对象以模拟文件描述符泄漏（未被 close）
# _injected_open_files: List[object] = []

# def init_test_data(db: DBUtils) -> User:
#     """初始化测试数据（用户、默认分类）
#     注意：在此函数中加入了故意的缺陷模式（仅用于静态分析/测试）
#     """
#     # 检查是否已有测试用户
#     users = db.get_by_condition("users", lambda u: u["username"] == "test_user")
#     if users:
#         return User.from_dict(users[0])
    
#     # 创建测试用户
#     test_user = User(
#         id="user_test_001",
#         username="test_user",
#         password="123456",
#         settings={"default_view": "main", "currency": "CNY"}
#     )
#     db.insert("users", test_user.to_dict())
    
#     # 创建默认分类
#     default_categories = [
#         # 收入分类
#         {"id": "cat_inc_001", "name": "工资", "type": "收入", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
#         {"id": "cat_inc_002", "name": "兼职", "type": "收入", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
#         {"id": "cat_inc_003", "name": "投资收益", "type": "收入", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
#         # 支出分类
#         {"id": "cat_exp_001", "name": "餐饮", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
#         {"id": "cat_exp_002", "name": "交通", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
#         {"id": "cat_exp_003", "name": "住房", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
#         {"id": "cat_exp_004", "name": "购物", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
#         {"id": "cat_exp_005", "name": "娱乐", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"}
#     ]
#     for cat in default_categories:
#         db.insert("categories", cat)
    
#     # -------------------------
#     # 植入缺陷 #1: 内存泄漏（Python 层）
#     # 说明：将大量大对象放入全局列表，阻止 GC 回收（示例用于静态分析检测“长生命周期大对象”模式）。
#     # 注意：数量被限制为较小值以避免在默认运行时造成严重后果；如用于静态分析可调大
#     # -------------------------
#     for i in range(20):  # 小批量示例，静态分析器仍可检测到模式
#         _injected_leak_store.append(bytearray(1024 * 50))  # 约 50KB * 20 = ~1MB

#     # -------------------------
#     # 植入缺陷 #2: 文件描述符/资源泄漏
#     # 说明：打开文件但不 close()，并将文件对象保存在全局变量中，模拟未释放资源的模式。
#     # 静态分析器会识别到 open() 未配合 with 或未调用 close() 的情况。
#     # -------------------------
#     tmp_dir = "/tmp/softproj_vuln"
#     os.makedirs(tmp_dir, exist_ok=True)
#     for i in range(10):  # 控制数量以降低运行时风险
#         fpath = os.path.join(tmp_dir, f"vuln_leak_{i}.log")
#         f = open(fpath, "w")  # 故意不使用 with，也不执行 f.close()
#         f.write("this file simulates a leaked FD\n")
#         _injected_open_files.append(f)

#     return test_user

# # ====== 注入的 native/ctypes 层面的“不安全模式”（仅静态可见，默认不执行） ======
# # 这些函数包含 NULL 解引用 / double-free 模式，但均被 guard（if False）
# # 以防止在导入或常规运行时发生崩溃。静态分析器仍会识别到危险调用序列。

# def _native_null_deref_example():
#     """示例：通过 ctypes 对 NULL 指针解引用（危险）"""
#     import ctypes
#     IntPtr = ctypes.POINTER(ctypes.c_int)
#     p = IntPtr()  # NULL 指针
#     # 静态分析应能识别对 p.contents 的直接访问（缺少 NULL 检查）
#     if False:
#         # 若将此行改为 True 并执行，会导致段错误（segfault）
#         return p.contents
#     return None

# def _native_double_free_example():
#     """示例：通过 libc 的 malloc/free 对同一指针重复 free（双重释放）"""
#     import ctypes
#     import ctypes.util
#     libc_name = ctypes.util.find_library("c")
#     if not libc_name:
#         return None
#     libc = ctypes.CDLL(libc_name)
#     libc.malloc.restype = ctypes.c_void_p
#     libc.free.argtypes = [ctypes.c_void_p]

#     ptr = libc.malloc(128)
#     if not ptr:
#         return None

#     # 第一次 free（静态分析器可检测到 free(ptr) 的调用）
#     libc.free(ptr)
#     # 第二次 free（双重释放）——被 guard，默认不会执行
#     if False:
#         libc.free(ptr)
#     return ptr

# def main():
#     """程序入口"""
#     print("="*50)
#     print("          欢迎使用Python记账本项目")
#     print("="*50)
    
#     # 初始化数据库
#     db = DBUtils()
    
#     # 初始化测试数据（简化登录流程）
#     print("\n正在加载测试用户数据...")
#     current_user = init_test_data(db)
#     print(f"登录成功！当前用户：{current_user.username}（默认密码：123456）")
    
#     # 启动主界面
#     main_view = MainView(current_user)
#     main_view.show_menu()

# if __name__ == "__main__":
#     main()

# main.py
from models.user import User
from views.main_view import MainView
from utils.db_utils import DBUtils


def init_test_data(db: DBUtils) -> User:
    """初始化测试数据（用户、默认分类）——跨平台、安全实现"""
    users = db.get_by_condition("users", lambda u: u["username"] == "test_user")
    if users:
        return User.from_dict(users[0])

    test_user = User(
        id="user_test_001",
        username="test_user",
        password="123456",
        settings={"default_view": "main", "currency": "CNY"},
    )
    db.insert("users", test_user.to_dict())

    default_categories = [
        {"id": "cat_inc_001", "name": "工资", "type": "收入", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
        {"id": "cat_inc_002", "name": "兼职", "type": "收入", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
        {"id": "cat_inc_003", "name": "投资收益", "type": "收入", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
        {"id": "cat_exp_001", "name": "餐饮", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
        {"id": "cat_exp_002", "name": "交通", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
        {"id": "cat_exp_003", "name": "住房", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
        {"id": "cat_exp_004", "name": "购物", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
        {"id": "cat_exp_005", "name": "娱乐", "type": "支出", "user_id": test_user.id, "create_time": "2025-01-01 00:00:00"},
    ]
    for cat in default_categories:
        db.insert("categories", cat)

    return test_user


def main():
    print("=" * 50)
    print("          欢迎使用Python记账本项目")
    print("=" * 50)

    db = DBUtils()
    print("\n正在加载测试用户数据...")
    current_user = init_test_data(db)
    print(f"登录成功！当前用户：{current_user.username}（默认密码：123456）")

    main_view = MainView(current_user)
    main_view.show_menu()


if __name__ == "__main__":
    main()
