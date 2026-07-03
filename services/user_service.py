from models import User
from schemas.user_schema import (
    UserUpdate
)
from core.security import get_password_hash

from repositories import user_repository

def create_user(db, user_data):
    try:
        #检查邮箱是否存在，用户名是否存在
        exists_user = db.query(User).filter(User.email == user_data.email).first()
        if exists_user:
            raise ValueError(f"邮箱 {user_data.email} 已存在")

        exists_user = db.query(User).filter(User.username == user_data.username).first()
        if exists_user:
            raise ValueError(f"用户名 {user_data.username} 已存在")

        user = User(
            username=user_data.username,
            email=user_data.email,
            password=get_password_hash(user_data.password),
        )

        result = user_repository.create(db, user)

        return result
    except Exception:
        # 回滚事务,恢复Session可用状态
        db.rollback() # 回滚事务，取消所有数据库操作, 不做回滚那么下一个操作比如session.query会继续报错
        raise # 重新抛出异常，让调用者处理

def get_user_by_id(db, user_id):
    result = user_repository.get_by_id(db, user_id)
    if not result:
        raise ValueError(f"用户 {user_id} 不存在")
    return result

def get_user_by_email(db, email):
    return db.query(User).filter(User.email == email).first()

def get_user_list(db):
    # 使用joinedload预加载角色信息(提前把关联对象一次性查出来)
    # 减少N+1查询问题（加入3个用户分别是三个不同的角色，
    # 1次sql查询users,3次sql从role里查询不同的role_id,
    # 用了joinedload预加载，只用1次查询users,1次sql去查询role）
    return user_repository.get_list(db)

def update_user(
    db,
    user_id,
    user_data: UserUpdate
):
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise ValueError(f"用户 {user_id} 不存在")
    
    update_data = user_data.model_dump( # schema对象转换成dict
        exclude_unset=True # 排除未设置的值
    )

    for key, value in update_data.items():

        setattr(user, key, value)

    user_repository.update_user(db, user)
    return user

def delete_user(db, user_id):
    user = user_repository.get_by_id(db, user_id)
    if not user:
        raise ValueError(f"用户 {user_id} 不存在")

    user_repository.delete(db, user)
    return True