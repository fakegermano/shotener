from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_url_shortener():
    response = client.get("/google.com")
    assert response.status_code == 200
    print(response.content)
    assert len(response.content.decode().replace(client.base_url + "/", "")) == 8

def test_url_expander():
    response = client.get("/bing.com")
    key = response.content.decode().replace(client.base_url + "/", "")
    response = client.get(f"{key}", allow_redirects=False)
    assert response.status_code == 302
