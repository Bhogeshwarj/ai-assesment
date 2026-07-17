from fastapi import APIRouter

from app.api.v1 import optimize, simulations

api_router = APIRouter()
api_router.include_router(simulations.router)
api_router.include_router(optimize.router)
