r"""
数据库连接自检脚本。
运行: venv\Scripts\python.exe -m scripts.check_db
作用: 用 core/config.py 里的 DATABASE_URL 连一次库,打印版本,确认连通。
"""
# text(): 把字符串包成可执行的 SQL 语句对象(SQLAlchemy 2.0 要求显式声明)
from sqlalchemy import text

# 复用项目唯一的 engine,不重新创建连接,保证和正式代码走同一条连接配置
from database.session import engine
from core.config import DATABASE_URL


def main() -> None:
    print(f"当前 DATABASE_URL = {DATABASE_URL}")

    # engine.connect() 借一条连接,with 块结束自动归还
    with engine.connect() as conn:
        # version() 是 PostgreSQL 的内置函数,返回数据库版本;能查出来 = 连通成功
        result = conn.execute(text("SELECT version();"))
        print("连接成功 ✅")
        print(result.scalar())


if __name__ == "__main__":
    main()
