from contextlib import asynccontextmanager
from app.core.database import Base
from app.core.database import get_db
import app.models
from app.scripts.init_s3 import init_buckets
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing S3 buckets...")
    init_buckets()
    print("S3 buckets ready!")
    yield

    print("Shutting down")


app = FastAPI(title="Plozeus", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok"}
