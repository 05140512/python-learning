from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from schemas.user_schema import (
  UserCreate,
  UserResponse,
  UserUpdate
)

from services import user_role_service
from services.user_service import (
  create_user,
  get_user_list,
  get_user_by_id,
  update_user,
  delete_user as delete_user_service
)

from dependencies.database import (
  get_db
)

from dependencies.auth_dependency import PermissionChecker

from core.permission_codes import PermissionCodes

from schemas.role_schema import RoleResponse

router = APIRouter(
  prefix="/users",
  tags=["Users"]
)

@router.get(
  "/list",
  response_model=list[UserResponse],
  dependencies=[Depends(PermissionChecker(PermissionCodes.USER_VIEW))]
)
def get_user_list_api(
  db: Session = Depends(get_db)
):
  return get_user_list(db)

@router.post(
  "/create",
  response_model=UserResponse,
  dependencies=[Depends(PermissionChecker(PermissionCodes.USER_CREATE))]
)
def create_user_api(
  user_data: UserCreate,
  db: Session = Depends(get_db)
):
  return create_user(db, user_data)


@router.get(
  "/{user_id}",
  response_model=UserResponse, #将数据库模型转换为Pydantic模型(Schema 对象)
  dependencies=[Depends(PermissionChecker(PermissionCodes.USER_VIEW))]
)
def get_user_by_id_api(
  user_id: int,
  db: Session = Depends(get_db)
):
  return get_user_by_id(db, user_id)

@router.put(
    "/{user_id}",
    dependencies=[Depends(PermissionChecker(PermissionCodes.USER_UPDATE))]
)
def update_user_api(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    return update_user(
        db,
        user_id,
        user_data
    )

@router.delete(
    "/{user_id}",
    dependencies=[Depends(PermissionChecker(PermissionCodes.USER_DELETE))]
)
def delete_user_api(
    user_id: int,
    db: Session = Depends(get_db)
):
    return delete_user_service(db, user_id)

@router.get("/{user_id}/roles", response_model=list[RoleResponse])
def get_user_roles_api(db: Session = Depends(get_db), user_id: int = Depends(PermissionChecker(PermissionCodes.USER_VIEW))):
  return user_role_service.get_user_roles(db, user_id)