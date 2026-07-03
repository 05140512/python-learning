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


class UserManager:
  def __init__(self):
    self.users = []

  def add_user(self, user):
    self.users.append(user)
    print(f"add user {user.name} success")

  def remove_user(self, name):
    for user in self.users:
      if user.name == name:
        self.users.remove(user)
        print(f"remove user {name} success")
        break
    else:
      print(f"user {name} not found")

  def find_user(self, name):
      for user in self.users:
          if user.name == name:
              return user

      return None
  
  def show_all_users(self):
      for user in self.users:
          user.info()
  