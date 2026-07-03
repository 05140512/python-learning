class User:
  def __init__(self, name, age, role):
        self.name = name
        self.age = age
        self.role = role
        self.is_login = False
  
  def login(self):
    self.is_login = True
    print(f"{self.name} login success")

  def logout(self):
    self.is_login = False
    print(f"{self.name} logout success")

  def is_login(self):
    return self.is_login

  def info(self):
        print(
            f"""
name: {self.name}
age: {self.age}
role: {self.role}
login: {self.is_login}
"""
        )
  