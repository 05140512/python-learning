r"""
第 3 课实测:隔离级别 —— 亲眼看"不可重复读",以及"升一级就挡住"。

运行: venv\Scripts\python.exe -m scripts.isolation_demo
（Windows 控制台若中文/emoji 报错,前面加 PYTHONIOENCODING=utf-8 PYTHONUTF8=1）

演示什么:
  同一个事务 A 里读两次同一行余额,中间事务 B 改了它并提交。
    - READ COMMITTED(PG 默认):A 第二次读会看到 B 的新值 → 不可重复读
    - REPEATABLE READ          :A 两次读一样(快照锁定开头那一刻)→ 被挡住

为什么不演示"脏读":PostgreSQL 不支持"读未提交",它把读未提交当读已提交处理,
                  所以脏读在 PG 上根本演不出来 —— 这本身就是个知识点。

注意:这是「演示脚本」,请你自己跑。它只动一张临时表 demo_account,不碰你的练习表。
"""
from sqlalchemy import create_engine, text

from core.config import DATABASE_URL

# 单独建一个安静的 engine(不刷 SQL 日志)
engine = create_engine(DATABASE_URL, echo=False)


def setup() -> None:
    """造一张只有一行的临时账户表,balance=100。"""
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as c:
        c.execute(text("DROP TABLE IF EXISTS demo_account;"))
        c.execute(text("CREATE TABLE demo_account (id int primary key, balance int);"))
        c.execute(text("INSERT INTO demo_account VALUES (1, 100);"))


def reset_balance() -> None:
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as c:
        c.execute(text("UPDATE demo_account SET balance = 100 WHERE id = 1;"))


def run_scenario(level: str) -> None:
    print(f"\n===== 隔离级别 = {level} =====")

    # 两条独立连接 = 两个真正并发的事务 A、B
    # execution_options(isolation_level=...) 在事务开始前设好级别
    a = engine.connect().execution_options(isolation_level=level)
    b = engine.connect().execution_options(isolation_level=level)

    ta = a.begin()  # 事务 A 开始(REPEATABLE READ 的"快照"从这之后第一次读那刻锁定)

    v1 = a.execute(text("SELECT balance FROM demo_account WHERE id = 1")).scalar()
    print(f"  A 第一次读 balance = {v1}")

    # 事务 B:把余额改成 200 并提交
    tb = b.begin()
    b.execute(text("UPDATE demo_account SET balance = 200 WHERE id = 1"))
    tb.commit()
    print("  B 已把 balance 改成 200 并 commit")

    # 事务 A 还在同一个事务里,第二次读
    v2 = a.execute(text("SELECT balance FROM demo_account WHERE id = 1")).scalar()
    verdict = "不一样 → 不可重复读!" if v2 != v1 else "一样 → 被快照挡住了 ✅"
    print(f"  A 第二次读 balance = {v2}   ← 和第一次 {verdict}")

    ta.commit()
    a.close()
    b.close()
    reset_balance()


def main() -> None:
    setup()
    run_scenario("READ COMMITTED")   # PG 默认级别
    run_scenario("REPEATABLE READ")  # 升一级
    print("\n看出区别了吗:同样的并发场景,只因为 A 的隔离级别不同,第二次读的结果就不同。")


if __name__ == "__main__":
    main()
