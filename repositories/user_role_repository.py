from models.user_role import UserRole
from datetime import datetime

# 查询用户已有角色
def get_by_user_id(
  session,
  user_id: int
) -> list[UserRole]:
  return session.query(UserRole).filter(
    UserRole.user_id == user_id,  
    UserRole.is_deleted == False,
    UserRole.deleted_at == None
  ).all()

# 查询用户某个角色（包括被删除的）
def get_by_user_role(session, user_id: int, role_id: int) -> UserRole | None:
  return session.query(UserRole).filter(
    UserRole.user_id == user_id,
    UserRole.role_id == role_id,
  ).first()

# 创建用户角色
def create(
  session,
  user_id: int,
  role_id: int
) -> UserRole | None:
  user_role = UserRole(
    user_id=user_id,
    role_id=role_id
  )
  session.add(user_role)
  return user_role

# 删除用户角色
def delete(
  session,
  user_id: int,
  role_id: int
) -> bool:
  user_role = session.query(UserRole).filter(
    UserRole.user_id == user_id,
    UserRole.role_id == role_id,
    UserRole.is_deleted == False,
    UserRole.deleted_at == None
  ).first()
  if user_role:
    user_role.is_deleted = True
    user_role.deleted_at = datetime.now()
    return True
  return False

# 恢复用户角色
def restore(
  session,
  user_id: int,
  role_id: int
) -> bool:
  user_role = session.query(UserRole).filter(
    UserRole.user_id == user_id,
    UserRole.role_id == role_id,
  ).first()
  if user_role:
    user_role.is_deleted = False
    user_role.deleted_at = None
    session.refresh(user_role)
    return True
  return False