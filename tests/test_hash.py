from core.security import get_password_hash, verify_password

plain_password = "123456"
hashed_password = get_password_hash(plain_password)

print('hashed_password:', hashed_password)

print('verify_password:', verify_password(plain_password, hashed_password))