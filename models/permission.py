from __future__ import annotations
from typing import TYPE_CHECKING

from models.base_model import BaseModel
from sqlalchemy import (
  String,
  ForeignKey,
  Integer,
)
from sqlalchemy.orm import Mapped, mapped_column,relationship

if TYPE_CHECKING:
  from models.role_permission import RolePermission

class Permission(BaseModel):
  __tablename__ = "permissions"

  name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

  code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

  parent_id: Mapped[int | None] = mapped_column(ForeignKey("permissions.id"), nullable=True)

  description: Mapped[str] = mapped_column(String(255), nullable=True)

  sort: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


  """
  remote_side的作用,告诉SQLAlchemy，自关联时，当前relationship关联的Permission引用远端的Permission的主键
  当访问 parent 时：
  1. 拿当前记录的 parent_id
  2. 去匹配另一条 Permission 的 id
  """
  parent = relationship(
    "Permission",
    remote_side="Permission.id",
    back_populates="children"
  )

  children = relationship(
    "Permission",
    back_populates="parent"
  )

  role_permissions: Mapped[list["RolePermission"]] = relationship("RolePermission", back_populates="permission")