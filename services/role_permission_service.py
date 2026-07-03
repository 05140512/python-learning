from models.role_permission import RolePermission

from repositories import (
  role_permission_repository,
  role_repository,
  permission_repository,
)

# 角色绑定权限

# 角色解除权限

# 查询角色权限

def bind_role_permission(db, role_id: int, permission_id: int) -> RolePermission:
  # 检查角色存在
  # 检查permission存在
  # 检查历史关系
  exists_role = role_repository.get_by_id(db, role_id)
  if not exists_role:
    raise ValueError("角色不存在")
  exists_permission = permission_repository.get_by_id(db, permission_id)
  if not exists_permission:
    raise ValueError("权限不存在")
  history_role_permission = role_permission_repository.get_by_role_and_permission(db, role_id, permission_id)
  if history_role_permission:
    if history_role_permission.is_deleted:
      role_permission_repository.restore(db, role_id, permission_id)
      return history_role_permission
    else:
      raise ValueError("角色权限已存在")
  else:
    return role_permission_repository.create(db, role_id, permission_id)


def get_role_permissions(db, role_id: int) -> list[RolePermission]:
  return role_permission_repository.get_by_role_id(db, role_id)


def unbind_role_permission(db, role_id: int, permission_id: int) -> bool:
  return role_permission_repository.soft_delete(db, role_id, permission_id)

def restore_role_permission(db, role_id: int, permission_id: int) -> bool:
  return role_permission_repository.restore(db, role_id, permission_id)