from pydantic import BaseModel
from pydantic import ConfigDict

class RoleResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  
  name: str