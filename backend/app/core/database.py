from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from the .env file into the application
load_dotenv()

# Retrieve the database connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")


# Create the SQLAlchemy engine
# The engine is the core interface that manages connections to the database
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
# Sessions are used to interact with the database (queries, inserts, updates, etc.)
SessionLocal = sessionmaker(bind=engine)


# Base class for all ORM
# All database tables will inherit from this class
# SQLAlchemy uses this metadata to generate tables and migrations
Base = declarative_base()


# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
