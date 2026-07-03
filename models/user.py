from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from models.base_model import BaseModel
from sqlalchemy.orm import relationship
from models.user_role import UserRole

# 继承 BaseModel 告诉SQLAlchemy 这是数据库模型
class User(BaseModel):
    __tablename__ = "users" # 表名
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    user_roles: Mapped[list[UserRole]] = relationship("UserRole", back_populates="user")