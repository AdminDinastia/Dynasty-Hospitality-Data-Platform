from contextlib import asynccontextmanager

from pydantic import BaseModel
from sqlalchemy.orm import Session

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, Response

import app.models
from app.core.database import Base
from app.core.database import get_db
from app.scripts.init_s3 import init_buckets
from app.core.config import settings
from app.core.dependencies import verify_token, get_current_user
from app.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing S3 buckets...")
    init_buckets()
    print("S3 buckets ready!")
    yield

    print("Shutting down")


app = FastAPI(title="Plozeus", version="0.1.0", lifespan=lifespan)
app.include_router(v1_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
