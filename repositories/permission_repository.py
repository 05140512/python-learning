from models.permission import Permission

def get_by_id(
  session,
  permission_id: int
) -> Permission | None:
  return (
    session.query(Permission)
    .filter(Permission.id == permission_id)
    .first()
  )