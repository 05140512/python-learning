"""
认证依赖
权限依赖
Current User依赖
"""
from fastapi import (
  Depends,
  HTTPException,
  status
)

from core.deps import oauth2_scheme
from core.security import decode_access_token

from dependencies.database import get_db

from sqlalchemy.orm import Session

from models.user import User
from services.user_service import get_user_by_id
from services.auth_service import get_user_permissions as get_user_permissions_service

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
  """
  获取当前用户
  """

  try:
    print('token', token)
    payload = decode_access_token(token)
    print('payload', payload)
    user_id = payload.get("sub")
    print('user_id', user_id)
    if user_id is None:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的token"
      )
    return get_user_by_id(db, user_id)
  except Exception as e:
    print("JWT ERROR =", e)

    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="无效的token"
    )

class PermissionChecker:
  """
  权限检查器（AND 语义：需同时具备全部 required 权限）

  用法:
    dependencies=[Depends(PermissionChecker(["user:view"]))]
    或
    current_user: User = Depends(PermissionChecker("user:view"))
  """
  def __init__(self, permission_codes: str | list[str]):
    if isinstance(permission_codes, str):
      self.permission_codes = [permission_codes]
    else:
      self.permission_codes = permission_codes

  def __call__(self, current_user: User = Depends(get_current_user)) -> User:
    user_permissions = set(get_user_permissions_service(current_user))
    required_permissions = set(self.permission_codes)
    missing_permissions = required_permissions - user_permissions

    if missing_permissions:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"缺少权限: {', '.join(sorted(missing_permissions))}"
      )

    return current_user