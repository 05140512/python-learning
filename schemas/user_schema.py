from pydantic import BaseModel
from pydantic import ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    role_id: int | None = None

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None

class UserResponse(BaseModel):
    # UserResponse是Pydantic对象，Pydantic只认识dict
    # from_attributes=True 表示从数据库模型中自动生成Pydantic模型,不需要手动定义每个字段(ORM类型的结构python不认识，需要转换成python类型)
    # from_attributes=True代表ORM对象->schema对象
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str