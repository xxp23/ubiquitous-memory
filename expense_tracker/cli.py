"""Command-line interface for the annual expense tracker."""

import argparse
import sys
from datetime import date

from .models import MONTH_NAMES_CN
from .tracker import ExpenseTracker


def _fmt(amount: float) -> str:
    return f"¥{amount:,.2f}"


def _bar(actual: float, budget: float, width: int = 20) -> str:
    """Simple ASCII progress bar showing actual vs budget."""
    if budget <= 0:
        filled = width if actual > 0 else 0
    else:
        ratio = min(actual / budget, 1.0)
        filled = int(ratio * width)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}]"


def cmd_set_budget(args: argparse.Namespace, tracker: ExpenseTracker) -> None:
    year, month, category, amount = args.year, args.month, args.category, args.amount
    if month:
        tracker.set_budget(year, month, category, amount)
        print(f"✓ 已设置预算：{year}年{MONTH_NAMES_CN[month-1]} {category} {_fmt(amount)}")
    else:
        tracker.set_annual_budget(year, category, amount)
        print(f"✓ 已设置全年预算：{year}年 {category} 每月 {_fmt(amount)}")


def cmd_add_expense(args: argparse.Namespace, tracker: ExpenseTracker) -> None:
    today = date.today()
    year = args.year or today.year
    month = args.month or today.month
    day = args.day or today.day
    try:
        date(year, month, day)  # validate the date combination
    except ValueError as exc:
        print(f"✗ 无效日期：{year}-{month:02d}-{day:02d}（{exc}）", file=sys.stderr)
        sys.exit(1)
    expense = tracker.add_expense(
        year=year,
        month=month,
        day=day,
        category=args.category,
        amount=args.amount,
        description=args.description or "",
    )
    print(
        f"✓ 已记录消费 #{expense.id}：{year}年{MONTH_NAMES_CN[month-1]}{day}日 "
        f"{expense.category} {_fmt(expense.amount)}"
        + (f"  ({expense.description})" if expense.description else "")
    )


def cmd_delete_expense(args: argparse.Namespace, tracker: ExpenseTracker) -> None:
    if tracker.delete_expense(args.id):
        print(f"✓ 已删除消费记录 #{args.id}")
    else:
        print(f"✗ 未找到消费记录 #{args.id}", file=sys.stderr)
        sys.exit(1)


def cmd_list_expenses(args: argparse.Namespace, tracker: ExpenseTracker) -> None:
    expenses = tracker.get_expenses(args.year, month=args.month, category=args.category)
    if not expenses:
        print("暂无消费记录")
        return
    print(f"\n{'ID':>4}  {'日期':^12}  {'类别':^10}  {'金额':>10}  描述")
    print("-" * 60)
    for e in sorted(expenses, key=lambda x: (x.month, x.day, x.id or 0)):
        date_str = f"{e.year}-{e.month:02d}-{e.day:02d}"
        print(f"{e.id or '':>4}  {date_str:^12}  {e.category:^10}  {_fmt(e.amount):>10}  {e.description}")
    total = sum(e.amount for e in expenses)
    print("-" * 60)
    print(f"{'合计':>38}  {_fmt(total):>10}")


def cmd_monthly_report(args: argparse.Namespace, tracker: ExpenseTracker) -> None:
    year, month = args.year, args.month
    summary = tracker.monthly_summary(year, month)
    title = f"{year}年{MONTH_NAMES_CN[month-1]} 收支报告"
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"{'类别':^10}  {'预算':>10}  {'实际':>10}  {'差额':>10}  进度")
    print("-" * 60)
    total_budget = total_actual = 0.0
    for cat, vals in summary.items():
        b, a, d = vals["budget"], vals["actual"], vals["difference"]
        total_budget += b
        total_actual += a
        diff_str = (f"+{_fmt(d)}" if d > 0 else _fmt(d))
        print(
            f"{cat:^10}  {_fmt(b):>10}  {_fmt(a):>10}  {diff_str:>10}  "
            f"{_bar(a, b)}"
        )
    print("-" * 60)
    diff = total_actual - total_budget
    diff_str = (f"+{_fmt(diff)}" if diff > 0 else _fmt(diff))
    print(f"{'合计':^10}  {_fmt(total_budget):>10}  {_fmt(total_actual):>10}  {diff_str:>10}")
    if total_budget > 0:
        pct = total_actual / total_budget * 100
        status = "超支 ⚠️" if total_actual > total_budget else "节余 ✓"
        print(f"\n预算使用率：{pct:.1f}%  {status}")


def cmd_annual_report(args: argparse.Namespace, tracker: ExpenseTracker) -> None:
    year = args.year
    summary = tracker.annual_summary(year)
    title = f"{year}年 全年收支报告"
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"{'类别':^10}  {'全年预算':>12}  {'实际花销':>12}  {'差额':>12}")
    print("-" * 60)
    total_budget = total_actual = 0.0
    for cat, vals in summary.items():
        b, a, d = vals["budget"], vals["actual"], vals["difference"]
        total_budget += b
        total_actual += a
        diff_str = (f"+{_fmt(d)}" if d > 0 else _fmt(d))
        print(f"{cat:^10}  {_fmt(b):>12}  {_fmt(a):>12}  {diff_str:>12}")
    print("-" * 60)
    diff = total_actual - total_budget
    diff_str = (f"+{_fmt(diff)}" if diff > 0 else _fmt(diff))
    print(f"{'合计':^10}  {_fmt(total_budget):>12}  {_fmt(total_actual):>12}  {diff_str:>12}")

    # Month-by-month breakdown
    print(f"\n{'月份':<6}  {'预算':>10}  {'实际':>10}  {'差额':>10}  进度")
    print("-" * 60)
    for month, b, a in tracker.monthly_totals(year):
        d = a - b
        diff_str = (f"+{_fmt(d)}" if d > 0 else _fmt(d))
        print(
            f"{MONTH_NAMES_CN[month-1]:<6}  {_fmt(b):>10}  {_fmt(a):>10}  "
            f"{diff_str:>10}  {_bar(a, b)}"
        )


def cmd_categories(args: argparse.Namespace, tracker: ExpenseTracker) -> None:
    print("\n默认消费类别：")
    for cat in tracker.categories():
        print(f"  • {cat}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="年度花销规划与统计工具",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="数据目录（默认：data）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # set-budget
    p_budget = sub.add_parser("set-budget", help="设置类别预算")
    p_budget.add_argument("--year", type=int, required=True, help="年份")
    p_budget.add_argument("--month", type=int, choices=range(1, 13), metavar="1-12", help="月份（不填则全年）")
    p_budget.add_argument("--category", required=True, help="消费类别")
    p_budget.add_argument("--amount", type=float, required=True, help="预算金额（元）")
    p_budget.set_defaults(func=cmd_set_budget)

    # add-expense
    p_add = sub.add_parser("add-expense", help="记录实际消费")
    p_add.add_argument("--year", type=int, help="年份（默认今年）")
    p_add.add_argument("--month", type=int, choices=range(1, 13), metavar="1-12", help="月份（默认今月）")
    p_add.add_argument("--day", type=int, help="日期（默认今日）")
    p_add.add_argument("--category", required=True, help="消费类别")
    p_add.add_argument("--amount", type=float, required=True, help="消费金额（元）")
    p_add.add_argument("--description", help="备注说明")
    p_add.set_defaults(func=cmd_add_expense)

    # delete-expense
    p_del = sub.add_parser("delete-expense", help="删除消费记录")
    p_del.add_argument("--id", type=int, required=True, help="消费记录ID")
    p_del.set_defaults(func=cmd_delete_expense)

    # list-expenses
    p_list = sub.add_parser("list-expenses", help="查看消费记录")
    p_list.add_argument("--year", type=int, required=True, help="年份")
    p_list.add_argument("--month", type=int, choices=range(1, 13), metavar="1-12", help="月份（不填则全年）")
    p_list.add_argument("--category", help="消费类别筛选")
    p_list.set_defaults(func=cmd_list_expenses)

    # monthly-report
    p_month = sub.add_parser("monthly-report", help="月度收支报告")
    p_month.add_argument("--year", type=int, required=True, help="年份")
    p_month.add_argument("--month", type=int, choices=range(1, 13), metavar="1-12", required=True, help="月份")
    p_month.set_defaults(func=cmd_monthly_report)

    # annual-report
    p_annual = sub.add_parser("annual-report", help="全年收支报告")
    p_annual.add_argument("--year", type=int, required=True, help="年份")
    p_annual.set_defaults(func=cmd_annual_report)

    # categories
    p_cat = sub.add_parser("categories", help="列出默认消费类别")
    p_cat.set_defaults(func=cmd_categories)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    tracker = ExpenseTracker(data_dir=args.data_dir)
    args.func(args, tracker)


if __name__ == "__main__":
    main()
