from __future__ import annotations
from typing import TYPE_CHECKING

from models.base_model import BaseModel
from sqlalchemy import (
  ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from models.role import Role
  from models.permission import Permission

class RolePermission(BaseModel):
  __tablename__ = "role_permissions"

  role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

  permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id"), nullable=False)

  role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")# type: ignore
  permission: Mapped["Permission"] = relationship("Permission", back_populates="role_permissions")# type: ignore