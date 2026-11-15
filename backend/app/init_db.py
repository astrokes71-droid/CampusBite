"""
Initialize CampusBite database tables.

Run only against the intended database.
This creates missing tables but does not seed data.
"""

from app.database import Base, engine
import app.models  # Register SQLAlchemy models


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("CampusBite database tables initialized.")


if __name__ == "__main__":
    initialize_database()
