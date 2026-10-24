#!/usr/bin/env python3
"""Reset and seed fictional demo community data."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rentrakshak.config import default_db_path
from rentrakshak.db.database import init_db
from rentrakshak.models.schemas import AnonymousExperienceInput, VacatingPostInput
from rentrakshak.services.community import create_anonymous_experience
from rentrakshak.services.vacating import create_vacating_post


def main() -> None:
    db = default_db_path()
    if db.exists():
        db.unlink()
    init_db(db)

    create_anonymous_experience(
        AnonymousExperienceInput(
            locality="Koramangala",
            property_type="apartment",
            category="Deposit and refund",
            sentiment="negative",
            experience_text="Deposit refund took 6 weeks; keep WhatsApp receipts and agreement copy safe.",
            rent_band="35k-45k",
        ),
        db_path=db,
    )
    create_vacating_post(
        VacatingPostInput(
            locality="Whitefield",
            property_type="apartment",
            room_type="private room",
            monthly_rent_inr=16000,
            availability_date=date.today() + timedelta(days=21),
            post_kind="room_takeover",
            description="Vacating furnished private room in 3BHK near ITPL road. Flatmates are quiet.",
            contact_method="demo-poster-contact",
            owner_permission_ack=True,
        ),
        publish=True,
        db_path=db,
    )
    print(f"Seeded demo data at {db}")


if __name__ == "__main__":
    main()
