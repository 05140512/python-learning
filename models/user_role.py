from __future__ import annotations
from typing import TYPE_CHECKING

from models.base_model import BaseModel
from sqlalchemy import (
  ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
  from models.user import User
  from models.role import Role

class UserRole(BaseModel):
  __tablename__ = "user_roles"

  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
  role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

  user: Mapped["User"] = relationship("User", back_populates="user_roles")
  role: Mapped["Role"] = relationship("Role", back_populates="user_roles")