from tests.conftest import auth_headers


def register(client, email: str, password: str = "pass1234!!"):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "first_name": "User"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_measurement_is_scoped_by_user(client):
    u1 = register(client, "u1@sport.app")
    u2 = register(client, "u2@sport.app")

    add = client.post(
        "/api/v1/progression/measurements",
        headers=auth_headers(u1["access_token"]),
        json={
            "day": "2026-09-04",
            "weight_kg": 97,
            "waist_cm": 91,
            "chest_cm": 108,
            "shoulders_cm": 126,
            "arms_cm": 40,
            "thighs_cm": 63,
            "hips_cm": 100,
            "body_fat_pct": 22,
            "muscle_mass_kg": 40,
            "body_water_pct": 52,
        },
    )
    assert add.status_code == 200, add.text

    list_u2 = client.get("/api/v1/progression/measurements", headers=auth_headers(u2["access_token"]))
    assert list_u2.status_code == 200
    assert list_u2.json() == []


def test_private_endpoint_rejects_missing_token(client):
    response = client.get("/api/v1/progression/measurements")
    assert response.status_code == 401


def test_private_endpoint_rejects_invalid_token(client):
    response = client.get(
        "/api/v1/progression/measurements",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert response.status_code == 401
