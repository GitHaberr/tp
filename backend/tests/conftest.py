import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import User
from security import hash_password

from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///:memory:", 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_db():

    Base.metadata.create_all(bind=engine)
    

    db = TestingSessionLocal()
    boss = User(full_name="Иванов Иван", email="boss@firma.ru",
                password_hash=hash_password("1234"), role="boss")
    db.add(boss)
    db.commit()
    db.refresh(boss)

    db.add_all([
        User(full_name="Петров Алексей", email="petrov@firma.ru",
             password_hash=hash_password("1234"), role="employee", manager_id=boss.id),
        User(full_name="Сидорова Мария", email="sidorova@firma.ru",
             password_hash=hash_password("1234"), role="employee", manager_id=boss.id),
    ])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def boss_token(client):
    r = client.post("/auth/login", json={"email": "boss@firma.ru", "password": "1234"})
    return r.json()["access_token"]

@pytest.fixture
def petrov_token(client):
    r = client.post("/auth/login", json={"email": "petrov@firma.ru", "password": "1234"})
    return r.json()["access_token"]

@pytest.fixture
def sidorova_token(client):
    r = client.post("/auth/login", json={"email": "sidorova@firma.ru", "password": "1234"})
    return r.json()["access_token"]
