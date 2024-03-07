from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as user_router
from .phone_keys import router as phone_key_router
from .categories import router as category_router
from .brands import router as brand_router
from .countries import router as county_router
from .manufacturers import router as manufacturer_router

router = APIRouter(prefix='/api')

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(phone_key_router)
router.include_router(category_router)
router.include_router(brand_router)
router.include_router(county_router)
router.include_router(manufacturer_router)
