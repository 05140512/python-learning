from services.user_service import create_user
from schemas.user_schema import UserCreate

from database.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_add_user():
  db = next(get_db())
  user_data = UserCreate(
    username="admin",
    password="123456",
    email="admin@example.com",
  )
  create_user(db, user_data)

test_add_user()
