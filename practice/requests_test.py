import json

import requests

response = requests.get(
    "https://jsonplaceholder.typicode.com/todos/1"
)

print('response.status_code =>', response.status_code)
# print('response.headers =>', json.dumps(response.headers.json(), indent=2, ensure_ascii=False))
# indent 缩进格式化，ensure_ascii=False 保留中文等非 ASCII 字符
print('json.dumps(response.json(), indent=2, ensure_ascii=False) =>', json.dumps(response.json(), indent=2, ensure_ascii=False))