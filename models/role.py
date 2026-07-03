from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from models.base_model import BaseModel

if TYPE_CHECKING:
  from models.user_role import UserRole
  from models.role_permission import RolePermission

class Role(BaseModel):
  __tablename__ = "roles"

  name: Mapped[str] = mapped_column(
    String(50),
    unique=True,
  )

  user_roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="role")
  role_permissions: Mapped[list["RolePermission"]] = relationship("RolePermission", back_populates="role")