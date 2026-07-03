name: str = 'John'
age = 30
is_student = True

x = 10
print(x)
x = 'hello x'
print(x)
x = True
print(x)

objectVar = {
  'name': 'John',
  'age': 30,
  'is_student': True,
  'english': False
}
print('objectVar =>', objectVar)
print(objectVar['name'])
print(objectVar['age'])
print(objectVar['is_student'])  

print(type(objectVar))
print(type(objectVar['name']))
print(type(objectVar['age']))
print(type(objectVar['is_student']))

a, b, c, = 1, 2, 3
print('a, b, c =>', a, b, c)

print(f"My name is {name} and I am {age} years old")

print(name)
print(age)
print(is_student)

print(type(name))
print(type(x))
print(type(age))
print(type(is_student))