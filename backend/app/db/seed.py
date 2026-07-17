"""Seeds the reference lookup tables (tea density profiles, packaging
materials) with illustrative starting data. Run with:

    python -m app.db.seed
"""
from app.db.session import SessionLocal
from app.models.reference import PackagingMaterialRef, TeaDensityProfile
from app.optimization.constants import MATERIAL_PROPERTIES

TEA_PROFILES = [
    ("Green Tea (Loose Leaf)", 0.35, "Whole/rolled green tea leaves, light and airy."),
    ("Black Tea - CTC", 0.60, "Crush-Tear-Curl processed black tea, denser granules."),
    ("Black Tea - Orthodox (Loose Leaf)", 0.40, "Traditionally processed whole-leaf black tea."),
    ("White Tea (Loose Leaf)", 0.25, "Minimally processed buds/leaves, very light."),
    ("Tea Bags (Boxed, Cut Tea)", 0.28, "Fine cut/fannings tea as used in bag cut, boxed."),
    ("Instant/Powdered Tea", 0.55, "Fine soluble powder, denser than leaf tea."),
]


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(TeaDensityProfile).count() == 0:
            for name, density, description in TEA_PROFILES:
                db.add(TeaDensityProfile(name=name, density_g_cm3=density, description=description))

        if db.query(PackagingMaterialRef).count() == 0:
            for name, props in MATERIAL_PROPERTIES.items():
                db.add(PackagingMaterialRef(
                    name=name,
                    cost_per_sqm=props["cost_per_sqm"],
                    thickness_mm=props["thickness_mm"],
                    density_g_cm3=props["density_g_cm3"],
                ))

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
