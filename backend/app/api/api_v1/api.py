from fastapi import APIRouter
from .endpoints import auth, users, projects, images, classes, segmentations, annotations

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"]) 
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
api_router.include_router(segmentations.router, prefix="/segmentations", tags=["segmentations"])
api_router.include_router(annotations.router, prefix="/annotations", tags=["annotations"])