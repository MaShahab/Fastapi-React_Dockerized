import os
os.environ["ENV"] = "test"

from fastapi.testclient import TestClient
from sqlalchemy import StaticPool
from core.database import Base, create_engine, sessionmaker, get_db
from main import app
import pytest
from faker import Faker
from users.models import UserModel
from tasks.models import TaskModel

from auth.jwt_auth import generate_access_token

fake = Faker()

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def override_dependencies(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="session", autouse=True)
def tear_up_and_down_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def anon_client():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="function")
def auth_client(db_session):
    client = TestClient(app)
    user = db_session.query(UserModel).filter_by(username = "admin").one()
    access_token = generate_access_token(user.id)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client

@pytest.fixture(scope="module", autouse=True)
def generate_mock_data(db_session):
    user = UserModel(username="admin")
    user.set_password("admin")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    print(f"User created with Username: {user.username} and ID: {user.id}")

    tasks_list = []
    for _ in range(10):
        tasks_list.append(TaskModel(
            user_id = user.id,
            title = fake.sentence(nb_words=6),
            description=fake.text(),
            is_completed=fake.boolean()
        ))
    db_session.add_all(tasks_list)
    db_session.commit()
    print(f"Added 10 tasks for user id {user.id}")
