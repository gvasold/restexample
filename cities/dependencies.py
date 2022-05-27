from . database import SessionLocal, engine


def get_db():
    "Function used for dependency injection of db connection."
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

