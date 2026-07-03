"""
JWT 常见字段说明：
- sub(subject)：主体，一般表示用户 ID。
- exp(expiration time)：过期时间。
- iat(issued at)：签发时间。
- nbf(not before)：生效时间。
- jti(JWT ID)：令牌唯一标识。
"""

from datetime import (
  datetime, # 日期时间库
  timedelta, # 时间差库
  timezone, # 时区库
)

from jose import jwt
from passlib.context import CryptContext
# passlib 密码加密库
# jose JWT库

from core.config import (
  SECRET_KEY,
  ALGORITHM,
  ACCESS_TOKEN_EXPIRE_MINUTES,
)

pwd_context = CryptContext(
  schemes=["bcrypt"], # 使用bcrypt算法加密密码
  deprecated="auto" # 自动使用更安全的算法
)

def get_password_hash(password: str) -> str:
  """
  密码加密
  """
  return pwd_context.hash(password)

def verify_password(
  plain_password: str,
  hashed_password: str
) -> bool:
  """
  密码验证
  """
  return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
  """
  创建JWT
  """
  # 复制数据
  to_encode = data.copy()

  # 获取当前UTC时间
  utc_now = datetime.now(timezone.utc)

  # 获取过期时间
  time_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

  # 计算过期时间
  expire = utc_now + time_delta

  # 更新数据
  to_encode.update({
    "exp": expire, # 过期时间
  })

  # 编码JWT
  encoded_jwt = jwt.encode(
    to_encode, # 数据
    SECRET_KEY, # 签名密钥
    algorithm=ALGORITHM # 算法
  )

  # 返回JWT
  return encoded_jwt

def decode_access_token(
  token: str
) -> dict:
  """
  解码JWT
  """

  payload = jwt.decode(
    token, # JWT
    SECRET_KEY, # 签名密钥
    algorithms=[ALGORITHM] # 算法
  )

  return payload