from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_task_response_200(anon_client):
    response = client.get("/tasks/tasks")
    assert response.status_code == 200

def test_task_response_200(auth_client):
    print(auth_client)
    response = client.get("/tasks/tasks")
    assert response.status_code == 200
    assert len(response.json()) > 0
