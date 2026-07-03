# 创建数据库连接配置
from sqlalchemy import create_engine

# sessionmaker 创建会话
from sqlalchemy.orm import sessionmaker

# 数据库连接串统一来自 core/config.py(唯一来源,换库只改那里 / .env)
from core.config import DATABASE_URL

# 创建数据库连接 echo=True 打印SQL语句
engine = create_engine(DATABASE_URL, echo=True)

# 创建Session工厂
SessionLocal = sessionmaker(
    bind=engine
)
