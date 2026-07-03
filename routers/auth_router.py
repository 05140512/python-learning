from fastapi import Depends
from fastapi import APIRouter
from sqlalchemy.orm import Session
from dependencies.database import get_db
from schemas.auth_schema import LoginRequest, LoginResponse, PermissionCodesResponse
from services.auth_service import login as login_service, get_user_permissions as get_user_permissions_service
from dependencies.auth_dependency import get_current_user
from models.user import User

router = APIRouter(
  prefix="/auth", # 路由前缀
  tags=["auth"], # 路由标签
)

@router.post("/login", response_model=LoginResponse)
def login_api(
  login_data: LoginRequest,
  db: Session = Depends(get_db)
):
  return login_service(
    db,
    login_data.username,
    login_data.password
  )

@router.get("/me")
def get_me(
  current_user: User = Depends(get_current_user)
):
  return {
    "id": current_user.id,
    "username": current_user.username,
    "email": current_user.email,
  }

@router.get("/permissions", response_model=PermissionCodesResponse)
def get_permissions(
  current_user: User = Depends(get_current_user),
):
  permissions = get_user_permissions_service(current_user)
  return {
    "permissions": permissions,
  }