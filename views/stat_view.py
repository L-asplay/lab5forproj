from services.statistics_engine import StatisticsEngine

class StatView:
    """统计视图"""
    def __init__(self, current_user):
        self.current_user = current_user
        self.stat_engine = StatisticsEngine()

    def show_stat_menu(self) -> None:
        """显示统计菜单"""
        print("\n--- 统计分析 ---")
        menu = [
            "1. 按分类统计",
            "2. 收支排行分析",
            "3. 按时间周期统计",
            "4. 返回主界面"
        ]
        for item in menu:
            print(item)
        
        choice = input("\n请输入操作编号：")
        if choice == "1":
            self._category_stat()
        elif choice == "2":
            self._rank_stat()
        elif choice == "3":
            self._time_period_stat()
        elif choice == "4":
            return
        else:
            print("输入无效，请重新选择！")
            self.show_stat_menu()

    def _category_stat(self) -> None:
        """按分类统计"""
        print("\n--- 按分类统计 ---")
        try:
            # 输入查询条件
            type_choice = input("请选择类型（1-收入 / 2-支出）：")
            record_type = "收入" if type_choice == "1" else "支出"
            month = input("请输入查询月份（格式：YYYY-MM）：")
            
            # 执行统计
            stat_result, total = self.stat_engine.category_statistics(
                user_id=self.current_user.id,
                month=month,
                record_type=record_type
            )
            
            # 显示结果
            print(f"\n📊 {month} {record_type}分类统计结果（总计：{total:.2f}元）")
            print("-" * 40)
            for category, amount in stat_result.items():
                percentage = (amount / total) * 100 if total != 0 else 0
                print(f"{category:>10}：{amount:>8.2f}元（{percentage:>5.1f}%）")
            
            # 模拟饼图展示（文字版）
            print("\n文字版饼图：")
            for category, amount in stat_result.items():
                if total == 0:
                    bar = ""
                else:
                    bar_length = int((amount / total) * 50)
                    bar = "■" * bar_length
                print(f"{category:>10}：{bar}")
        
        except Exception as e:
            print(f"❌ 统计失败：{str(e)}")
        
        input("\n按回车键返回...")

    def _rank_stat(self) -> None:
        """收支排行分析"""
        print("\n--- 收支排行分析 ---")
        try:
            type_choice = input("请选择类型（1-收入 / 2-支出）：")
            record_type = "收入" if type_choice == "1" else "支出"
            month = input("请输入查询月份（格式：YYYY-MM）：")
            
            # 执行排行统计
            rank_list = self.stat_engine.rank_statistics(
                user_id=self.current_user.id,
                month=month,
                record_type=record_type,
                top_n=5
            )
            
            # 显示结果
            print(f"\n🏆 {month} {record_type}TOP5排行")
            print("-" * 30)
            if rank_list:
                for i, (category, amount) in enumerate(rank_list, 1):
                    print(f"第{i:>1}名：{category:>8}（{amount:.2f}元）")
            else:
                print("暂无数据")
        except Exception as e:
            print(f"❌ 统计失败：{str(e)}")
        
        input("\n按回车键返回...")

    def _time_period_stat(self) -> None:
        """按时间周期统计"""
        print("\n--- 按时间周期统计 ---")
        try:
            type_choice = input("请选择类型（1-收入 / 2-支出）：")
            record_type = "收入" if type_choice == "1" else "支出"
            year = input("请输入查询年份（格式：YYYY）：")
            
            # 执行统计
            stat_result = self.stat_engine.time_period_statistics(
                user_id=self.current_user.id,
                year=year,
                record_type=record_type
            )
            
            # 显示结果
            print(f"\n📅 {year}年{record_type}月度统计")
            print("-" * 30)
            total = 0.0
            for month, amount in stat_result.items():
                print(f"{month:>10}：{amount:>8.2f}元")
                total += amount
            print("-" * 30)
            print(f"{'年度总计'}：{total:>8.2f}元")
        except Exception as e:
            print(f"❌ 统计失败：{str(e)}")
        
        input("\n按回车键返回...")