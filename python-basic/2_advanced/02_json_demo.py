import json
import os

user = {
  'name': 'John',
  'age': 30,
  'is_student': True,
  'english': False,
  'address': {
    'street': '123 Main St',
    'city': 'Anytown',
    'state': 'CA',
    'zip': '12345'
  }
}

user_json = json.dumps(user)
#  dumps 和 dump区别
#  dumps 是将字典转换为字符串
#  dump 是将字典转换为字符串并写入文件
#  定义一个方法向fileCenter中写入测试的json文件
#  文件名称为test_json.json

projectBasePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fileBasePath = os.path.join(projectBasePath, 'fileCenter')

def getFilePath(fileName):
  return os.path.join(fileBasePath, fileName)

def writeJsonToFile(fileName, jsonData):
  """将 JSON 数据按可读格式写入文件。"""
  filePath = getFilePath(fileName)
  with open(filePath, 'w', encoding='utf-8') as file:
    json.dump(jsonData, file, ensure_ascii=False, indent=2)

writeJsonToFile('test_json.json', user)

class setUserJson:
  """用户数据对象。"""

  def __init__(self, name, age):
    self.name = name
    self.age = age
  
  def toDict(self):
    """将对象转换为字典。"""
    
    return {
      'name': self.name,
      'age': self.age
    }

uJson1 = setUserJson('John', 30)
uJson2 = setUserJson('Jane', 25)

def appendUserToUsersJson(user):
  """向 users.json 的最外层数组中追加一个用户。"""

  filePath = getFilePath('users.json')

  # 读取已有数据，确保最终是列表结构
  users = []
  if os.path.exists(filePath):
    with open(filePath, 'r', encoding='utf-8') as file:
      content = file.read().strip()
      if content:
        try:
          jsonData = json.loads(content)
          if isinstance(jsonData, list):
            users = jsonData
          else:
            users = [jsonData]
        except json.JSONDecodeError:
          users = []

  users.append(user.toDict())

  # 整体写回，保持合法 JSON 数组格式
  with open(filePath, 'w', encoding='utf-8') as file:
    json.dump(users, file, ensure_ascii=False, indent=2)

appendUserToUsersJson(uJson1)
appendUserToUsersJson(uJson2)