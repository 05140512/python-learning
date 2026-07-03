import os
from datetime import timedelta

# load_dotenv() 会读取项目根目录的 .env 文件,把里面的 KEY=VALUE 注入到环境变量
# python-dotenv 已在 requirements.txt 中
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "123456789abcdefg" # JWT签名密钥,绝不能提交到 Git。以后会放：.env文件中。

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============ 数据库配置 ============
# 整个项目唯一的数据库连接来源。换库 = 只改这里(或改 .env),代码零改动。
# os.getenv("KEY", 默认值): 环境变量里有就用环境变量,没有就用默认值(回退到 SQLite,保证不配置也能跑)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///database/app.db",
)