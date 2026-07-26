from fastapi import APIRouter

from app.api.v1 import (
    auth,
    accommodations,
    events,
    uploads,
    datasets,
    products,
    entitlements,
    points,
    webhooks,
)

router = APIRouter()

router.include_router(auth.router)
router.include_router(accommodations.router)
router.include_router(events.router)
router.include_router(uploads.router)
router.include_router(datasets.router)
router.include_router(products.router)
router.include_router(entitlements.router)
router.include_router(points.router)
router.include_router(webhooks.router)
