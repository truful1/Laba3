import time
from locust import HttpUser, task, between
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["username"] == "string"

def test_create_user():
    response = client.post(
    "/register/",

    json={"username": "testuser", "email": "testuser@example.com",
    "full_name": "Test User", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

def test_successful_registration():
    response = client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

def test_duplicate_registration():
    client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    response = client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    assert response.status_code == 400

def test_successful_authentication():
    client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_failed_authentication():
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_expired_token():
    client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]
    time.sleep(3600)
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "username" in data[0]
    assert "email" in data[0]

def test_get_current_user():
    client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"

def test_update_user():
    client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]
    response = client.put(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated User"

def test_update_user_invalid_data():
    client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]
    response = client.put(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": ""}
    )
    assert response.status_code == 422

def test_update_user_without_token():
    response = client.put(
        "/users/1",
        json={"full_name": "Updated User"}
    )
    assert response.status_code == 401
def test_delete_user():
    client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]
    response = client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_delete_user_again():
    client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"}
    )
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]
    client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    response = client.delete(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

def test_cors():
    response = client.options("/users/")
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert response.headers["Access-Control-Allow-Origin"] == "*"

def test_cors_unsupported_domain():
    response = client.options("/users/", headers={"Origin": "http://localhost:8000"})
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers
def test_missing_fields():
    response = client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "password": "password123"}
    )
    assert response.status_code == 422

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def register_user(self):
        self.client.post("/register/", json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"})

def test_unauthorized_access():
    response = client.get("/users/me")
    assert response.status_code == 401

def test_invalid_token():
    response = client.get("/users/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
