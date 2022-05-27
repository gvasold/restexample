import pytest
import math

from cities import crud
from cities import schemas

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import sqlalchemy_utils
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy import text
from cities.database import Base
from cities.main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()


@pytest.fixture(scope="session")
def db_engine():
    """Create a database engine with empty tables.

    If necessary, all tables will be created.

    This engine will be used during the whole test session.
    """
    # make sure sqlite has activated foreign key constraint
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON') 
        
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    event.listen(engine, 'connect', _fk_pragma_on_connect)
    if not sqlalchemy_utils.database_exists:
        sqlalchemy_utils.create_database(engine.url)

    Base.metadata.create_all(bind=engine)
    yield engine



@pytest.fixture(scope="function")
def db(db_engine):
    """Yield auto-rollback database session.

    The returned database session auotmatically opens a
    transaction and rolles it back afterwards.
    This keeps the database in a consistent state which
    avoids side effects during testing.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = Session(bind=connection)
    #db.execute('PRAGMA foreign_keys=ON')
    #äconnection = db.connection()
    #cursor = connection.cursor()
    #print(type(connection))
    #con = db.connection()
    #cursor = con.cursor()
    #cursor.execute("PRAGMA foreign_keys=ON")
    #cursor.close()
    yield db

    db.rollback()
    # transaction.commit()
    connection.close()



@pytest.fixture(scope="function")
def client(db):
    "Return a test client for app."
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def countries(db: Session) -> None:
    "Populate the countries table with 110 entries."
    for i in range(1, 111):
        crud.create_country(
            db, schemas.CountryCreate(name=f"Country {i}", id=i)
        )

@pytest.fixture(scope="function")
def counties(db: Session, countries) -> None:
    "Populate the counties table with 110 entries."
    for i in range(1, 111):
        crud.create_county(
            db, schemas.CountyCreate(name=f"County {i}", country_id=(i//10+1), id=i)
        )

@pytest.fixture(scope="function")
def cities(db: Session, counties) -> None:
    "Populate the cities table with 110 entries."
    for i in range(1, 111):
        crud.create_city(
            db, schemas.CityCreate(name=f"City {i}", population=i*10, county_id=(i//10+1), id=i)
        )