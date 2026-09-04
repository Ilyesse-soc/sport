from tests.conftest import auth_headers


def register(client, email: str):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "pass1234!!", "first_name": "User"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_add_meal_updates_daily_summary(client):
    user = register(client, "nutri@sport.app")

    add = client.post(
        "/api/v1/nutrition/meals",
        headers=auth_headers(user["access_token"]),
        json={
            "meal_type": "dejeuner",
            "title": "Riz Poulet",
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

    summary = client.get(
        "/api/v1/nutrition/daily-summary?day=2026-09-04",
        headers=auth_headers(user["access_token"]),
    )
    assert summary.status_code == 200, summary.text
    payload = summary.json()
    assert round(payload["calories"], 1) == 215
    assert round(payload["protein_g"], 1) == 4.2
