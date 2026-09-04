from datetime import timedelta

from app.core.security import create_access_token
from tests.conftest import auth_headers


def register(client, email: str):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "pass1234!!", "first_name": "User"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_expired_token_rejected(client):
    user = register(client, "expired@sport.app")
    token = create_access_token(user["user_id"], expires_delta=timedelta(minutes=-1))
    response = client.get("/api/v1/profile", headers=auth_headers(token))
    assert response.status_code == 401


def test_idor_meal_blocked(client):
    u1 = register(client, "idor1@sport.app")
    u2 = register(client, "idor2@sport.app")

    add = client.post(
        "/api/v1/nutrition/meals",
        headers=auth_headers(u1["access_token"]),
        json={
            "meal_type": "dejeuner",
            "title": "Test",
            "consumed_at": "2026-09-04T12:30:00Z",
            "items": [
                {
                    "food_name": "Riz basmati cru",
                    "weight_g": 60,
                    "weight_state": "RAW",
                    "calories": 215,
                    "protein_g": 4.2,
                    "carbs_g": 46.8,
                    "fats_g": 0.5,
                    "fiber_g": 0.7,
                }
            ],
        },
    )
    assert add.status_code == 200, add.text
    meal_id = add.json()["id"]

    forbidden = client.get(f"/api/v1/nutrition/meals/{meal_id}", headers=auth_headers(u2["access_token"]))
    assert forbidden.status_code == 404


def test_upload_exe_rejected(client):
    user = register(client, "uploadexe@sport.app")
    response = client.post(
        "/api/v1/coach/analyze-plate",
        headers=auth_headers(user["access_token"]),
        files={"image": ("x.exe", b"MZ\x00\x01", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_upload_fake_jpeg_rejected(client):
    user = register(client, "fakejpeg@sport.app")
    response = client.post(
        "/api/v1/coach/analyze-plate",
        headers=auth_headers(user["access_token"]),
        files={"image": ("x.jpg", b"not-a-real-image", "image/jpeg")},
    )
    assert response.status_code == 400


def test_upload_too_large_rejected(client):
    user = register(client, "bigimg@sport.app")
    payload = b"\x00" * (11 * 1024 * 1024)
    response = client.post(
        "/api/v1/coach/analyze-plate",
        headers=auth_headers(user["access_token"]),
        files={"image": ("x.webp", payload, "image/webp")},
    )
    assert response.status_code in {400, 413}


def test_private_ai_endpoint_requires_auth(client):
    response = client.post("/api/v1/coach/chat", json={"message": "hello"})
    assert response.status_code == 401


def test_rate_limit_on_auth(client):
    import os
    os.environ["TESTING"] = "0"
    for i in range(5):
        client.post(
            "/api/v1/auth/login",
            json={"email": f"nouser{i}@sport.app", "password": "invalid-pass"},
        )
    blocked = client.post(
        "/api/v1/auth/login",
        json={"email": "nouser@sport.app", "password": "invalid-pass"},
    )
    assert blocked.status_code == 429
    os.environ["TESTING"] = "1"


def test_sql_injection_input_is_inert(client):
    user = register(client, "sqlsafe@sport.app")
    response = client.get(
        "/api/v1/nutrition/foods?q=' OR 1=1 --",
        headers=auth_headers(user["access_token"]),
    )
    assert response.status_code == 200


def test_xss_content_echo_is_escaped_by_json_boundary(client):
    user = register(client, "xss@sport.app")
    payload = {
        "meal_type": "snack",
        "title": "<script>alert(1)</script>",
        "consumed_at": "2026-09-04T10:00:00Z",
        "items": [
            {
                "food_name": "<img src=x onerror=alert(1)>",
                "weight_g": 30,
                "weight_state": "RAW",
                "calories": 110,
                "protein_g": 2,
                "carbs_g": 20,
                "fats_g": 2,
                "fiber_g": 2,
            }
        ],
    }
    add = client.post("/api/v1/nutrition/meals", headers=auth_headers(user["access_token"]), json=payload)
    assert add.status_code == 200
    list_resp = client.get("/api/v1/nutrition/meals?day=2026-09-04", headers=auth_headers(user["access_token"]))
    assert list_resp.status_code == 200
