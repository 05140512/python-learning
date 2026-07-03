from schemas.auth_schema import LoginResponse
from repositories.user_repository import get_by_username
from core.security import create_access_token
from core.security import verify_password
from fastapi import HTTPException
from repositories.user_repository import get_by_id
from models.user import User

def login(
  db,
  username: str,
  password: str
):
  user = get_by_username(db, username)
  if not user:
    raise HTTPException(status_code=401, detail="用户不存在")
  if not verify_password(password, user.password):
    raise HTTPException(status_code=401, detail="用户名或密码错误")
  
  # 生成token
  token = create_access_token({
    "sub": str(user.id)
  })
  return LoginResponse(
    access_token=token
  )

def get_user_roles(
  db,
  user_id: int
):
  # 直接查询user,users里已经关联上了role的信息
  user = get_by_id(db, user_id)
  return user.user_roles

def get_user_permissions(current_user: User) -> list[str]:
  user_roles = current_user.user_roles

  permissions_codes= []
  for user_role in user_roles:

    role = user_role.role

    for role_permission in role.role_permissions:

      permission = role_permission.permission

      permissions_codes.append(permission.code)

  return list(set(permissions_codes)) # 去重
