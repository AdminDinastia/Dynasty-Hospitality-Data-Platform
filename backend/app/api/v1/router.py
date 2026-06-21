from fastapi import APIRouter

from app.api.v1 import auth, accommodations

router = APIRouter()

router.include_router(auth.router)
router.include_router(accommodations.router)
