from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from the .env file into the application
load_dotenv()

# Retrieve the database connection string from environment variables
if os.getenv("ENV") == "docker":
    DATABASE_URL = os.getenv("DATABASE_URL_DOCKER")
elif os.getenv("ENV") == "local":
    DATABASE_URL = os.getenv("DATABASE_URL_LOCAL")


# Create the SQLAlchemy engine
# The engine is the core interface that manages connections to the database
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
# Sessions are used to interact with the database (queries, inserts, updates, etc.)
SessionLocal = sessionmaker(bind=engine)

# Base class for all ORM models
# All database tables will inherit from this class
# SQLAlchemy uses this metadata to generate tables and migrations
Base = declarative_base()
