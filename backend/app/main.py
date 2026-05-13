from app.core.database import Base
from app.core.database import get_db
import app.models
from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends


app = FastAPI(title="Dynasty", version="0.1.0")


@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"status": "ok"}
