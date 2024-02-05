from fastapi import APIRouter

from .auth import router as auth_router
from .user import router as user_router
from .phone_key import router as phone_key_router
from .category import router as category_router
from .brand import router as brand_router

router = APIRouter(prefix='/api')

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(phone_key_router)
router.include_router(category_router)
router.include_router(brand_router)
