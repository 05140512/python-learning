from pydantic import BaseModel
from pydantic import ConfigDict
class LoginRequest(BaseModel):
  username: str
  password: str

class LoginResponse(BaseModel):
  access_token: str
  token_type: str = "bearer"

class PermissionCodesResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  
  permissions: list[str]