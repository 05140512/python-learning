r"""
第 2 课实验数据:给 device_telemetry 灌入数十万条遥测数据。

运行: venv\Scripts\python.exe -m scripts.seed_telemetry
作用:
  1. 按 models/telemetry.py 里的模型,在 PostgreSQL 建 device_telemetry 表
     (顺便建上模型里定义的组合索引 idx_device_telemetry_device_id_metric_recorded_at)
  2. 用 PostgreSQL 的 generate_series 在「服务端」一次性造 30 万行
     —— 比用 Python 循环 INSERT 快几个数量级(数据不出库)
  3. 跑 ANALYZE 更新统计信息,让执行计划准确

为什么不用 ORM 一行行插:
  ORM insert 要把 30 万个对象在 Python 端构造、再逐条发往数据库,慢且占内存。
  造「测试数据」这种一次性活,直接让数据库自己用 SQL 生成最划算。
"""
from sqlalchemy import text

from database.session import engine
from models.telemetry import DeviceTelemetry

# 想造多少行(改这里即可)。30 万足够让 Index Only Scan 和回表的差距显形。
ROW_COUNT = 300_000


def main() -> None:
    # ---- 1. 建表(先删后建,保证可重复运行)----
    # DeviceTelemetry.__table__ 拿到这张表的元数据;drop/create 只针对这一张表,
    # 不碰 users / roles 等其它表。checkfirst=True:表不存在时 drop 不报错。
    DeviceTelemetry.__table__.drop(engine, checkfirst=True)
    DeviceTelemetry.__table__.create(engine)
    print(f"已建表 device_telemetry(含组合索引)")

    # ---- 2. 服务端批量造数据 ----
    # generate_series(1, N) 生成 N 行;每行用 random() 派生各列。
    # 注意:created_at / updated_at / is_deleted 在模型里是 Python 端默认值,
    #       纯 SQL 插入不会自动填,所以这里显式给。
    insert_sql = text(
        """
        INSERT INTO device_telemetry
            (device_id, metric, value, recorded_at,
             created_at, updated_at, is_deleted)
        SELECT
            -- 50 台设备:1~50
            (random() * 49)::int + 1,
            -- 5 种测点
            (ARRAY['temperature','pressure','voltage','current','humidity'])
                [(random() * 4)::int + 1],
            -- 数值 0~100,保留 4 位
            (random() * 100)::numeric(12, 4),
            -- 采集时间:最近 90 天内随机
            now() - ((random() * 90 * 24 * 3600)::int || ' seconds')::interval,
            now(),
            now(),
            false
        FROM generate_series(1, :n);
        """
    )

    with engine.begin() as conn:  # begin(): 进事务,块结束自动 commit
        conn.execute(insert_sql, {"n": ROW_COUNT})

    # VACUUM ANALYZE:整理表 + 刷新统计信息,让后面的执行计划准确、可直接观察。
    # (这是数据库的日常维护命令,细节是进阶专题,这里当成"灌完数据后的收尾"即可。)
    # VACUUM 不能在事务块里跑,所以单独用一个自动提交的连接执行。
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text("VACUUM ANALYZE device_telemetry;"))
        total = conn.execute(text("SELECT count(*) FROM device_telemetry;")).scalar()

    print(f"灌入完成,当前行数 = {total}")


if __name__ == "__main__":
    main()
