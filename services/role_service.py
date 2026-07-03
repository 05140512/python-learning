from models.role import Role
from repositories.role_repository import create as create_role_repository
from repositories.role_repository import get_list as get_list_role_repository
from repositories.role_repository import get_by_id as get_by_id_role_repository

def create(
  db,
  role: Role
) -> Role:
  return create_role_repository(db, role)

def get_list(
  db
) -> list[Role]:
  return get_list_role_repository(db)

def get_by_id(
  db,
  role_id: int
) -> Role | None:
  return get_by_id_role_repository(db, role_id)