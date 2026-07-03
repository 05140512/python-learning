from ast import If


def getSomeMessage():
  return {
    'message': 'Hello, World!',
    'code': 200
  }

message = getSomeMessage()
print('message =>', message)
print('message["message"] =>', message['message'])
print('message["code"] =>', message['code'])

print('type of message =>', type(message))
print(type(message['message']))
print(type(message['code']))

print(message)

def getSomeMessageWithParams(message='Hello, World!', code=200):
  print(f"message: {message}, code: {code}")

getSomeMessageWithParams('传入的message', 500)

def logicJudge(code):
  if code == 200:
    return {
      'message': 'success',
      'code': 200
    }
  else:
    return {
      'message': 'error',
      'code': 400
    }

result = logicJudge(100)
print('result =>', result)

print(type(result))
print(type(result['message']))
print(type(result['code']))
print(result)

# 函数参数和返回值的类型注解,做类型提示+IDE提示，不做强约束
def add(a: int, b: int) -> int:
  return a + b

print('add(1, 2) =>', add(1, 2))
print('add(1, 2) =>', add(1, 2))