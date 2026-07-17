import logging

from fastapi import APIRouter

from app.schemas.optimization import (
    CartonOptimizeRequest,
    CartonResultSchema,
    ContainerOptimizeRequest,
    ContainerResultSchema,
    PackageOptimizeRequest,
    PackageOptimizeResponse,
    PalletOptimizeRequest,
    PalletResultSchema,
)
from app.services import optimize_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/optimize", tags=["optimize"])


@router.post("/package", response_model=PackageOptimizeResponse)
def optimize_package(request: PackageOptimizeRequest) -> PackageOptimizeResponse:
    """Module 3 - AI Package Recommendation. Runs stage 1 of the pipeline in
    isolation: density -> volume -> candidate inner-pouch/tin dimensions."""
    best, alternatives = optimize_service.run_package_optimization(request)
    return PackageOptimizeResponse.model_validate({"best": best, "alternatives": alternatives}, from_attributes=True)


@router.post("/carton", response_model=CartonResultSchema)
def optimize_carton(request: CartonOptimizeRequest) -> CartonResultSchema:
    """Module 4 - Carton Optimization for a given package's dimensions."""
    carton = optimize_service.run_carton_optimization(request)
    return CartonResultSchema.model_validate(carton, from_attributes=True)


@router.post("/pallet", response_model=PalletResultSchema)
def optimize_pallet(request: PalletOptimizeRequest) -> PalletResultSchema:
    """Module 5 - Pallet Optimization for a given carton."""
    pallet = optimize_service.run_pallet_optimization(request)
    return PalletResultSchema.model_validate(pallet, from_attributes=True)


@router.post("/container", response_model=ContainerResultSchema)
def optimize_container(request: ContainerOptimizeRequest) -> ContainerResultSchema:
    """Module 6 - Container Optimization comparing 20GP / 40GP / 40HC."""
    container = optimize_service.run_container_optimization(request)
    return ContainerResultSchema.model_validate(container, from_attributes=True)
