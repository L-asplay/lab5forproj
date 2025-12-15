from enum import Enum
from views.stat_view import StatView
from views.search_view import SearchView
from services.record_service import RecordService

class ViewMode(Enum):
    """视图模式枚举"""
    MAIN = "主界面"
    EDIT = "编辑模式"
    STAT = "统计模式"
    SEARCH = "搜索模式"

class MainView:
    """主界面"""
    def __init__(self, current_user):
        self.current_user = current_user
        self.current_mode = ViewMode.MAIN
        self.record_service = RecordService()
        self.stat_view = StatView(current_user)
        self.search_view = SearchView(current_user)

    def show_menu(self) -> None:
        """显示主菜单"""
        while True:
            print("\n" + "="*50)
            print(f"欢迎 {self.current_user.username} | 当前模式：{self.current_mode.value}")
            print("="*50)
            
            if self.current_mode == ViewMode.MAIN:
                self._show_main_menu()
            elif self.current_mode == ViewMode.EDIT:
                self._show_edit_menu()
            elif self.current_mode == ViewMode.STAT:
                self.stat_view.show_stat_menu()
                self.current_mode = ViewMode.MAIN  # 统计完成返回主界面
            elif self.current_mode == ViewMode.SEARCH:
                self.search_view.show_search_menu()
                self.current_mode = ViewMode.MAIN  # 搜索完成返回主界面

    def _show_main_menu(self) -> None:
        """主菜单选项"""
        menu = [
            "1. 记录收支",
            "2. 统计分析",
            "3. 搜索记录",
            "4. 管理分类",
            "5. 退出程序"
        ]
        for item in menu:
            print(item)
        
        choice = input("\n请输入操作编号：")
        if choice == "1":
            self.current_mode = ViewMode.EDIT
        elif choice == "2":
            self.current_mode = ViewMode.STAT
        elif choice == "3":
            self.current_mode = ViewMode.SEARCH
        elif choice == "4":
            self._manage_categories()
        elif choice == "5":
            print("感谢使用，再见！")
            exit()
        else:
            print("输入无效，请重新选择！")

    def _show_edit_menu(self) -> None:
        """编辑模式菜单（记录收支）"""
        print("\n--- 记录收支 ---")
        try:
            # 选择收支类型
            type_choice = input("请选择类型（1-收入 / 2-支出）：")
            record_type = "收入" if type_choice == "1" else "支出"
            
            # 选择分类
            categories = self.record_service.db.get_by_condition(
                "categories",
                lambda c: c["user_id"] == self.current_user.id and c["type"] == record_type
            )
            print(f"\n{record_type}分类：")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat['name']}")
            
            cat_choice = int(input(f"请选择{record_type}分类（编号）：")) - 1
            category_name = categories[cat_choice]["name"]
            
            # 输入金额和描述
            amount = float(input("请输入金额："))
            description = input("请输入描述（可选）：") or "无"
            
            # 创建记录
            record = self.record_service.create_record(
                user_id=self.current_user.id,
                amount=amount,
                record_type=record_type,
                category_name=category_name,
                description=description
            )
            print(f"\n✅ 记录创建成功！记录ID：{record.id}")
        
        except (ValueError, IndexError) as e:
            print(f"❌ 记录失败：{str(e)}")
        
        # 返回主界面
        input("\n按回车键返回主菜单...")
        self.current_mode = ViewMode.MAIN

    def _manage_categories(self) -> None:
        """分类管理"""
        print("\n--- 分类管理 ---")
        menu = ["1. 新增分类", "2. 删除分类", "3. 查看所有分类"]
        for item in menu:
            print(item)
        
        choice = input("\n请输入操作编号：")
        if choice == "1":
            self._add_category()
        elif choice == "2":
            self._delete_category()
        elif choice == "3":
            self._list_categories()
        else:
            print("输入无效！")

    def _add_category(self) -> None:
        """新增分类"""
        try:
            name = input("请输入分类名称：")
            type_choice = input("请选择关联类型（1-收入 / 2-支出）：")
            type_ = "收入" if type_choice == "1" else "支出"
            
            self.record_service.create_category(
                user_id=self.current_user.id,
                name=name,
                type_=type_
            )
            print(f"✅ 分类 {name} 新增成功！")
        except ValueError as e:
            print(f"❌ 新增失败：{str(e)}")

    def _delete_category(self) -> None:
        """删除分类"""
        try:
            # 选择类型
            type_choice = input("请选择分类类型（1-收入 / 2-支出）：")
            type_ = "收入" if type_choice == "1" else "支出"
            
            # 列出分类
            categories = self.record_service.db.get_by_condition(
                "categories",
                lambda c: c["user_id"] == self.current_user.id and c["type"] == type_
            )
            if not categories:
                print("暂无该类型分类！")
                return
            
            print(f"\n{type_}分类：")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat['name']}")
            
            # 选择删除
            cat_choice = int(input(f"请选择要删除的{type_}分类（编号）：")) - 1
            category = categories[cat_choice]
            
            # 验证是否有关联记录
            records = self.record_service.get_records(
                user_id=self.current_user.id,
                type=type_,
                category=category["name"]
            )
            if records:
                confirm = input(f"该分类下有{len(records)}条记录，确定删除？（y/n）：")
                if confirm.lower() != "y":
                    print("删除取消！")
                    return
            
            # 执行删除
            self.record_service.db.delete(
                "categories",
                lambda c: c["id"] == category["id"]
            )
            print(f"✅ 分类 {category['name']} 删除成功！")
        except (ValueError, IndexError) as e:
            print(f"❌ 删除失败：{str(e)}")

    def _list_categories(self) -> None:
        """查看所有分类"""
        print("\n--- 所有分类 ---")
        for type_ in ["收入", "支出"]:
            categories = self.record_service.db.get_by_condition(
                "categories",
                lambda c: c["user_id"] == self.current_user.id and c["type"] == type_
            )
            print(f"\n{type_}类：")
            if categories:
                for cat in categories:
                    print(f"- {cat['name']}（创建时间：{cat['create_time']}）")
            else:
                print("- 暂无分类")
        input("\n按回车键返回主菜单...")