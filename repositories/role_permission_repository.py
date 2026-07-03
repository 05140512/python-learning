from models.role_permission import RolePermission

# 角色绑定权限

# 角色解除权限

# 查询角色权限

def get_by_role_id(
  session,
  role_id: int
) -> list[RolePermission]:
  return session.query(RolePermission).filter(
    RolePermission.role_id == role_id
  ).all()

# 查询指定关系，包括历史关系（包含软删除的）
def get_by_role_and_permission(
  session,
  role_id: int,
  permission_id: int
) -> RolePermission | None:
  return session.query(RolePermission).filter(
    RolePermission.role_id == role_id,
    RolePermission.permission_id == permission_id
  ).first()

# 创建关系
def create(
  session,
  role_id: int,
  permission_id: int
) -> RolePermission:
  role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
  session.add(role_permission)
  session.commit()
  session.refresh(role_permission)
  return role_permission

# 软删除关系
def soft_delete(
  session,
  role_id: int,
  permission_id: int
) -> bool:
  role_permission = session.query(RolePermission).filter(
    RolePermission.role_id == role_id,
    RolePermission.permission_id == permission_id
  ).first()
  if role_permission:
    role_permission.is_deleted = True
    session.commit()
    return True
  return False

# 恢复被软删除的关系
def restore(
  session,
  role_id: int,
  permission_id: int
) -> bool:
  role_permission = session.query(RolePermission).filter(
    RolePermission.role_id == role_id,
    RolePermission.permission_id == permission_id
  ).first()
  if role_permission:
    role_permission.is_deleted = False
    role_permission.deleted_at = None
    role_permission.deleted_by = None
    session.commit()
    return True
  return False