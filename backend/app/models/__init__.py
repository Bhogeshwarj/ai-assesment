"""Import every model module so Base.metadata is fully populated for Alembic
autogenerate and for create_all() in tests."""
from app.models.packaging import Carton, Container, PackageType, Pallet  # noqa: F401
from app.models.reference import PackagingMaterialRef, TeaDensityProfile  # noqa: F401
from app.models.result import Result  # noqa: F401
from app.models.simulation import Simulation  # noqa: F401
from app.models.user import User  # noqa: F401
