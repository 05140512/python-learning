from database.session import SessionLocal

from models.role import Role
from models.permission import Permission
from models.role_permission import RolePermission
from models.user import User
from models.user_role import UserRole

def seed_role_admin():
  try:
    db = SessionLocal()

    role_admin = Role(name="admin")

    db.add(role_admin)
    db.commit()

    db.refresh(role_admin)

    print(f"Role admin created with id: {role_admin.id}")
  except Exception as e:
    print(f"Error creating role admin: {e}")
  finally:
    db.close()

def seed_permissions():
  try:
    db = SessionLocal()

    permissions = [
        Permission(
            name="管理员查看",
            code="admin:view",
            sort=1,
            description="管理员查看"
        ),
        Permission(
            name="管理员新增",
            code="admin:create",
            sort=2,
            description="管理员新增"
        ),
        Permission(
            name="管理员修改",
            code="admin:update",
            sort=3,
            description="管理员修改"
        ),
        Permission(
            name="管理员删除",
            code="admin:delete",
            sort=4,
            description="管理员删除"
        ),
        Permission(
            name="用户查看",
            code="user:view",
            sort=5,
            description="用户查看"
        ),
        Permission(
            name="用户新增",
            code="user:create",
            sort=6,
            description="用户新增"
        ),
        Permission(
            name="用户修改",
            code="user:update",
            sort=7,
            description="用户修改"
        ),
        Permission(
            name="用户删除",
            code="user:delete",
            sort=8,
            description="用户删除"
        )
    ]


    for permission in permissions:

      exists = (
          db.query(Permission)
          .filter(
              Permission.code == permission.code
          )
          .first()
      )

      if exists:
          continue

      db.add(permission)
    db.commit()

    print(f"Permissions created with ids: {permissions}")
  except Exception as e:
    print(f"Error creating permissions: {e}")
  finally:
    db.close()

def create_role_permissions():

    db = SessionLocal()

    try:

        admin_role = (
            db.query(Role)
            .filter(Role.name == "admin")
            .first()
        )

        if not admin_role:
            print("Admin role not found")
            return

        permissions = db.query(Permission).all()

        for permission in permissions:

            exists = (
                db.query(RolePermission)
                .filter(
                    RolePermission.role_id == admin_role.id,
                    RolePermission.permission_id == permission.id
                )
                .first()
            )

            if exists:
                continue

            role_permission = RolePermission(
                role_id=admin_role.id,
                permission_id=permission.id
            )

            db.add(role_permission)

        db.commit()

        print("role_permissions 创建完成")

    finally:
        db.close()

def create_user_roles():

    db = SessionLocal()

    try:

        admin_user = (
            db.query(User)
            .filter(User.username == "admin")
            .first()
        )

        admin_role = (
            db.query(Role)
            .filter(Role.name == "admin")
            .first()
        )

        if not admin_user or not admin_role:
            print("Admin user or admin role not found")
            return

        exists = (
            db.query(UserRole)
            .filter(
                UserRole.user_id == admin_user.id,
                UserRole.role_id == admin_role.id
            )
            .first()
        )

        if exists:
            print("user_role已存在")
            return

        user_role = UserRole(
            user_id=admin_user.id,
            role_id=admin_role.id
        )

        db.add(user_role)

        db.commit()

        print("user_role创建完成")

    finally:
        db.close()

# seed_permissions()
# create_role_permissions()
create_user_roles()