from fastapi import APIRouter

from app.api.v1 import auth, accommodations, events

router = APIRouter()

router.include_router(auth.router)
router.include_router(accommodations.router)
router.include_router(events.router)
