from fastapi import APIRouter

from app.api.v1.auth.routes import router as auth_router
from app.api.v1.genres.routes import router as genres_router
from app.api.v1.movies.routes import router as movies_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(movies_router)
api_router.include_router(genres_router)
