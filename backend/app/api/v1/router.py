from fastapi import APIRouter

from app.api.v1 import auth, accommodations, events, uploads, datasets

router = APIRouter()

router.include_router(auth.router)
router.include_router(accommodations.router)
router.include_router(events.router)
router.include_router(uploads.router)
router.include_router(datasets.router)
