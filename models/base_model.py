from datetime import datetime

from sqlalchemy import (
  Integer,
  DateTime,
  Boolean
)

from sqlalchemy.orm import (
  Mapped,
  mapped_column
)

from database.base import Base

class BaseModel(Base):
  """
  所有模型的基类
  """

  # __abstract__ = True 表示这是一个抽象基类，不会被创建为数据库表(不要创建表)
  __abstract__ = True

  # 主键 id
  id: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    autoincrement=True,
    comment="主键"
  )

  # 创建时间 created_at
  created_at: Mapped[datetime] = mapped_column(
    DateTime,
    default=datetime.now,
    comment="创建时间"
  )

  # 更新时间 updated_at（插入用 default，更新用 onupdate）
  updated_at: Mapped[datetime] = mapped_column(
    DateTime,
    default=datetime.now,
    onupdate=datetime.now,
    comment="更新时间"
  )

  # 是否删除 is_deleted
  is_deleted: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    comment="是否删除"
  )

  # 删除时间 deleted_at
  deleted_at: Mapped[datetime | None] = mapped_column(
    DateTime,
    nullable=True,
    default=datetime.now,
    onupdate=datetime.now,
    comment="删除时间"
  )

  # 删除人 deleted_by
  deleted_by: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    comment="删除人"
  )

  # __repr__是Python中的魔法方法，用于定义对象的打印输出
  def __repr__(self):
    return (
      f"BaseModel("
      f"id={self.id}, "
      f"created_at={self.created_at}, "
      f"updated_at={self.updated_at}, "
      f"is_deleted={self.is_deleted}, "
      f"deleted_at={self.deleted_at}, "
      f"deleted_by={self.deleted_by}"
    )