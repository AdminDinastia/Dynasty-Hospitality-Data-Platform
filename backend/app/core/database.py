from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
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
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create a configured "Session" class
# Sessions are used to interact with the database (queries, inserts, updates, etc.)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Base class for all ORM
# All database tables will inherit from this class
# SQLAlchemy uses this metadata to generate tables and migrations
Base = declarative_base()


# Dependencies
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
