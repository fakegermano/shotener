from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_url_shortener():
    response = client.get("/test")
    assert response.status_code == 200
    assert len(response.content.decode().replace(client.base_url + "/", "")) == 10