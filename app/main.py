from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import user
from alembic import command
from alembic.config import Config


# Initialize FastAPI app
app = FastAPI()


# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

# Include user router
app.include_router(user.router)
