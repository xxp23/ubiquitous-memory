# 年度花销规划与统计工具

一个基于命令行的个人财务管理工具，帮助你：

1. **规划全年预算** —— 按月份和消费类别设置计划花销
2. **记录实际消费** —— 随时记录每笔支出
3. **生成收支报告** —— 月度/全年预算对比、超支预警

---

## 默认消费类别

| 类别 | 说明 |
|------|------|
| 住房 | 房租、物业、水电气等 |
| 餐饮 | 餐厅、外卖、食材等 |
| 交通 | 地铁、公交、打车、油费等 |
| 医疗健康 | 看诊、药品、体检等 |
| 教育 | 课程、书籍、培训等 |
| 娱乐 | 电影、演唱会、游戏等 |
| 服装 | 衣物、鞋包等 |
| 日用品 | 生活日用消耗品 |
| 旅行 | 旅游、出行等 |
| 其他 | 其余支出 |

> 类别可自定义，传入任意字符串即可。

---

## 快速开始

### 安装依赖（仅需一次）

```bash
pip install -e .
```

### 查看所有命令

```bash
expense-tracker --help
# 或
python main.py --help
```

---

## 命令参考

### 1. 设置预算

```bash
# 为全年某类别设置每月预算（共 12 个月）
expense-tracker set-budget --year 2026 --category 餐饮 --amount 1500

# 单独设置某月的预算
expense-tracker set-budget --year 2026 --month 6 --category 旅行 --amount 5000
```

### 2. 记录消费

```bash
# 记录今天的消费
expense-tracker add-expense --category 餐饮 --amount 45 --description "午餐"

# 指定日期
expense-tracker add-expense --year 2026 --month 3 --day 15 --category 娱乐 --amount 200 --description "电影"
```

### 3. 查看消费记录

```bash
# 查看全年记录
expense-tracker list-expenses --year 2026

# 按月份筛选
expense-tracker list-expenses --year 2026 --month 3

# 按类别筛选
expense-tracker list-expenses --year 2026 --category 餐饮
```

### 4. 删除消费记录

```bash
expense-tracker delete-expense --id 5
```

### 5. 月度收支报告

```bash
expense-tracker monthly-report --year 2026 --month 3
```

示例输出：

```
============================================================
  2026年三月 收支报告
============================================================
    类别              预算          实际          差额  进度
------------------------------------------------------------
    交通         ¥500.00     ¥320.00    ¥-180.00  [############--------]
    住房       ¥3,000.00   ¥3,200.00    +¥200.00  [####################]
    娱乐         ¥800.00   ¥1,200.00    +¥400.00  [####################]
    餐饮       ¥1,500.00   ¥1,250.00    ¥-250.00  [################----]
------------------------------------------------------------
    合计       ¥5,800.00   ¥5,970.00    +¥170.00

预算使用率：102.9%  超支 ⚠️
```

### 6. 全年收支报告

```bash
expense-tracker annual-report --year 2026
```

---

## 数据存储

默认数据保存在当前目录的 `data/` 文件夹下：

- `data/budget.json` —— 预算计划
- `data/expenses.json` —— 消费记录

通过 `--data-dir` 可指定其他目录：

```bash
expense-tracker --data-dir ~/finance annual-report --year 2026
```

---

## 运行测试

```bash
pip install pytest
python -m pytest tests/ -v
```
