from models.user_role import UserRole

from repositories import user_repository

from repositories import role_repository

from repositories import user_role_repository

def assign_role_to_user(db, user_id: int, role_id: int) -> UserRole | None:
  """
  检查用户是否存在
      ↓
  检查角色是否存在
      ↓
  检查历史关系
      ↓
  不存在则创建-create
      ↓
  已存在且有效则报错
      ↓
  已存在但绑定关系标记为删除则恢复
      ↓
  restore
      ↓
  保存
  """

  with db.begin():

    exists_user = user_repository.get_by_id(db, user_id)
    if not exists_user:
      raise ValueError("用户不存在")

    exists_role = role_repository.get_by_id(db, role_id)
    if not exists_role:
      raise ValueError("角色不存在")

    history_user_role = user_role_repository.get_by_user_role(db, user_id, role_id)

    if history_user_role:
      if history_user_role.is_deleted:
        user_role_repository.restore(db, user_id, role_id)
        return history_user_role
      else:
        raise ValueError("用户已经有这个角色")
    else:
      user_role = user_role_repository.create(db, user_id, role_id)
      return user_role

def remove_role_from_user(db, user_id: int, role_id: int) -> bool:
  """
  检查用户是否存在
      ↓
  检查角色是否存在
      ↓
  检查是否已经绑定
      ↓
  删除UserRole
      ↓
  保存
  """
  exists_user = user_repository.get_by_id(db, user_id)
  if not exists_user:
    raise ValueError("用户不存在")

  exists_role = role_repository.get_by_id(db, role_id)
  if not exists_role:
    raise ValueError("角色不存在")

  exists_user_roles = user_role_repository.get_by_user_id(db, user_id)
  exists_role_ids = {user_role.role_id for user_role in exists_user_roles}
  if role_id not in exists_role_ids:
    raise ValueError("用户没有这个角色")

  user_role_repository.delete(db, user_id, role_id)
  return True

def get_user_roles(db, user_id: int) -> list[UserRole]:
  """
  查询用户
      ↓
  查询用户所有角色
      ↓
  返回角色列表
  """
  user = user_repository.get_by_id_with_roles(db, user_id)
  if not user:
    raise ValueError("用户不存在")
  
  roles = []

  for user_role in user.user_roles:
    
    if user_role.is_deleted:
      continue

    roles.append(user_role.role)

  return roles