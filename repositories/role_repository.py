from models.role import Role

def create(
  session,
  role: Role
) -> Role:
  session.add(role)
  session.commit()
  return role

def get_list(
  session
) -> list[Role]:
  return session.query(Role).all()

def get_by_id(
  session,
  role_id: int
) -> Role | None:
  return (
    session.query(Role)
    .filter(Role.id == role_id)
    .first()
  )