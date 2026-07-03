from core.security import (
  create_access_token,
  decode_access_token,
)

data = {
  "sub": "1",
}

token = create_access_token(data)

print('token:', token)

payload = decode_access_token(token)

print('payload:', payload)