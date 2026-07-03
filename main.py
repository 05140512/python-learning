from database.base import Base
from database.session import engine

from fastapi import FastAPI
from routers.user_router import router as user_router
from routers.auth_router import router as auth_router

app = FastAPI()

app.include_router(user_router)
app.include_router(auth_router)

Base.metadata.create_all(bind=engine)
