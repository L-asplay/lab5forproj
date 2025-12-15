from services.search_engine import SearchEngine

class SearchView:
    """搜索视图"""
    def __init__(self, current_user):
        self.current_user = current_user
        self.search_engine = SearchEngine()

    def show_search_menu(self) -> None:
        """显示搜索菜单"""
        print("\n--- 搜索记录 ---")
        menu = [
            "1. 关键词模糊搜索",
            "2. 高级搜索（多条件）",
            "3. 返回主界面"
        ]
        for item in menu:
            print(item)
        
        choice = input("\n请输入操作编号：")
        if choice == "1":
            self._fuzzy_search()
        elif choice == "2":
            self._advanced_search()
        elif choice == "3":
            return
        else:
            print("输入无效，请重新选择！")
            self.show_search_menu()

    def _fuzzy_search(self) -> None:
        """关键词模糊搜索"""
        print("\n--- 关键词模糊搜索 ---")
        keyword = input("请输入搜索关键词（描述/分类）：")
        records = self.search_engine.fuzzy_search(
            user_id=self.current_user.id,
            keyword=keyword
        )
        
        self._show_search_results(records, f"关键词：{keyword}")

    def _advanced_search(self) -> None:
        """高级搜索"""
        print("\n--- 高级搜索 ---")
        filters = {}
        
        # 收支类型筛选
        type_choice = input("是否按类型筛选？（1-是 / 2-否）：")
        if type_choice == "1":
            type_val = input("请选择类型（1-收入 / 2-支出）：")
            filters["type"] = "收入" if type_val == "1" else "支出"
        
        # 时间筛选
        time_choice = input("是否按月份筛选？（1-是 / 2-否）：")
        if time_choice == "1":
            filters["month"] = input("请输入月份（格式：YYYY-MM）：")
        
        # 金额范围筛选
        amount_choice = input("是否按金额范围筛选？（1-是 / 2-否）：")
        if amount_choice == "1":
            filters["min_amount"] = float(input("请输入最小金额："))
            filters["max_amount"] = float(input("请输入最大金额："))
        
        # 执行搜索
        records = self.search_engine.advanced_search(
            user_id=self.current_user.id,
            **filters
        )
        
        # 构建筛选条件描述
        cond_desc = []
        if "type" in filters:
            cond_desc.append(f"类型：{filters['type']}")
        if "month" in filters:
            cond_desc.append(f"月份：{filters['month']}")
        if "min_amount" in filters and "max_amount" in filters:
            cond_desc.append(f"金额：{filters['min_amount']}-{filters['max_amount']}元")
        cond_text = "、".join(cond_desc) if cond_desc else "无筛选条件"
        
        self._show_search_results(records, f"筛选条件：{cond_text}")

    def _show_search_results(self, records: list, condition: str) -> None:
        """显示搜索结果"""
        print(f"\n🔍 搜索结果（{condition}）")
        print("-" * 80)
        if not records:
            print("暂无匹配记录")
            input("\n按回车键返回...")
            return
        
        # 表头
        print(f"{'ID':<20} {'时间':<20} {'类型':<6} {'分类':<8} {'金额':<10} {'描述'}")
        print("-" * 80)
        
        # 数据行
        for record in records:
            print(
                f"{record.id:<20} "
                f"{record.create_time.strftime('%Y-%m-%d %H:%M'):<20} "
                f"{record.type.value:<6} "
                f"{record.category:<8} "
                f"{record.amount:<10.2f} "
                f"{record.description}"
            )
        
        print("-" * 80)
        print(f"共找到 {len(records)} 条记录")
        input("\n按回车键返回...")