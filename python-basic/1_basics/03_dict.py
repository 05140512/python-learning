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

user_name = user.get('name')
print('user_name =>', user_name)

user['age'] = 31
print('user_age =>', user.get('age'))

user['gender'] = 'male'
print('user_gender =>', user.get('gender'))

del user['address']['city']

user_items = user.items()
print('user_items =>', user_items)

for key, value in user.items():
  print(f"{key}: {value}")

print(type(user))