from fastapi import APIRouter
from app.api.endpoints import auth, users, swagger, agents

api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# Include user management routes
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Include swagger management routes
api_router.include_router(
    swagger.router,
    prefix="/swagger",
    tags=["swagger"]
)

# Include agent management routes
api_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["agents"]
)