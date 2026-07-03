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