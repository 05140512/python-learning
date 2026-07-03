r"""
第 2 课实测:覆盖索引 / Index Only Scan。

运行: venv\Scripts\python.exe -m scripts.lesson03_explain
作用: 在 30 万行的 device_telemetry 上,实跑 4 组 EXPLAIN,对比:
      - 普通 Index Scan(命中索引但要「回表」拿 value)
      - Index Only Scan(查的列全在索引里,不回表)
      - 用 INCLUDE 做「覆盖索引」,让回表的查询也变成 Index Only Scan
      - Heap Fetches 与 VACUUM 的关系(可见性图谱的坑)

为避免 echo=True 刷屏,这里单独建一个安静的 engine。
"""
from sqlalchemy import create_engine, text

from core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)

# 实验固定参数:确保 device_id/metric 在数据里真实存在
DEVICE_ID = 7
METRIC = "temperature"


def explain(conn, title: str, sql: str, params: dict) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("-" * 70)
    plan = conn.execute(
        text("EXPLAIN (ANALYZE, BUFFERS) " + sql), params
    ).fetchall()
    for (line,) in plan:
        print(line)


def main() -> None:
    # 时间范围:最近 30 天
    rng = "recorded_at BETWEEN now() - interval '30 days' AND now()"
    where = f"device_id = :did AND metric = :m AND {rng}"
    params = {"did": DEVICE_ID, "m": METRIC}

    # AUTOCOMMIT:VACUUM 不能在事务块里跑,所以这里不用 begin() 开事务,
    # 改用自动提交的连接;EXPLAIN/CREATE INDEX 在自动提交下同样正常。
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        # 关键前置:VACUUM 刷新「可见性图谱」。
        # Index Only Scan 要靠它判断「这一页全部行都可见」,从而跳过回表。
        # 刚灌完数据没 VACUUM 时,Heap Fetches 会很大,Index Only Scan 名不副实。
        conn.execute(text("VACUUM ANALYZE device_telemetry;"))

        # --- A. 回表:SELECT value(value 不在组合索引里,必须回表拿)---
        explain(
            conn,
            "A. SELECT value —— value 不在索引中 → Index Scan + 回表",
            f"SELECT value FROM device_telemetry WHERE {where} ORDER BY recorded_at;",
            params,
        )

        # --- B. Index Only Scan:只查索引里有的列 ---
        explain(
            conn,
            "B. SELECT recorded_at —— 列全在索引里 → Index Only Scan(不回表)",
            f"SELECT recorded_at FROM device_telemetry WHERE {where} ORDER BY recorded_at;",
            params,
        )

        # --- C. 覆盖索引:把 value 用 INCLUDE 塞进索引叶子 ---
        # INCLUDE 的列不参与排序/最左匹配,只是「附带存一份」,专为免回表。
        conn.execute(text("DROP INDEX IF EXISTS idx_dt_covering;"))
        conn.execute(
            text(
                "CREATE INDEX idx_dt_covering ON device_telemetry "
                "(device_id, metric, recorded_at) INCLUDE (value);"
            )
        )
        conn.execute(text("VACUUM ANALYZE device_telemetry;"))
        explain(
            conn,
            "C. 同样 SELECT value,但有了 INCLUDE(value) 覆盖索引 → Index Only Scan",
            f"SELECT value FROM device_telemetry WHERE {where} ORDER BY recorded_at;",
            params,
        )

        # --- D. 反例:SELECT *(还要 created_at 等一堆列)→ 覆盖不了,回表 ---
        explain(
            conn,
            "D. SELECT * —— 要的列覆盖索引装不下 → 退回普通 Index Scan + 回表",
            f"SELECT * FROM device_telemetry WHERE {where} ORDER BY recorded_at;",
            params,
        )


if __name__ == "__main__":
    main()
