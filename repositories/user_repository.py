from models.user import User
from models.user_role import UserRole
from sqlalchemy.orm import joinedload

def create(
  session,
  user: User
):
  session.add(user)
  session.commit()
  session.refresh(user)
  return user

def delete(
  session,
  user: User
):
  session.delete(user)
  session.commit()
  return True

def update_user(
  session,
  user: User
):
  session.commit()
  session.refresh(user)
  return user

def get_by_id(
  session,
  user_id: int
):
  return session.query(User).filter(
    User.id == user_id
  ).first()

# 查询用户的所有角色
def get_by_id_with_roles(
  session,
  user_id: int
):
  return session.query(User).filter(
    User.id == user_id
  ).options(joinedload(User.user_roles).joinedload(UserRole.role)).first()

def get_list(
  session
):
  return (
    session.query(User)
    .options(joinedload(User.user_roles).joinedload(UserRole.role))  # 防止N+1 sql查询问题
    .all()
  )

def get_by_username(
  session,
  username: str
):
  return session.query(User).filter(
    User.username == username
  ).first()