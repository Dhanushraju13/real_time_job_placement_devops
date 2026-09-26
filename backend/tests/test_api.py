from fastapi.testclient import TestClient
from app.main import app
from app.seed import seed_database
from app.database import Base, engine

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "UP"

def test_jobs():
    Base.metadata.create_all(bind=engine)
    seed_database()
    with TestClient(app) as client:
        response = client.get("/jobs")
        assert response.status_code == 200
        assert len(response.json()) >= 1
