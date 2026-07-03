# dataclass：本质是“业务数据模型”,就是在定义数据结构类型
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union

names: List[str] = []
cityDict: Dict[str, str] = {
  'beijing': '北京',
  'shanghai': '上海',
  '广州': '广州',
  '深圳': '深圳',
  '成都': '成都',
  '重庆': '重庆',
  '西安': '西安',
  '武汉': '武汉',
  '南京': '南京',
}
anyVar: Union[int, str, bool, List[str], Dict[str, str], Any] = None

@dataclass
class User:
  name: Optional[str] = None
  age: Optional[int] = 18
  role: Optional[str] = 'admin'
  is_login: Optional[bool] = False

user = User('John', 20, 'admin', True)

print(user)
