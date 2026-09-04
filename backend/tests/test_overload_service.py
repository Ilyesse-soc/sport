from app.services.overload_service import recommend_overload


def test_recommend_overload_increase_weight():
    msg = recommend_overload(
        target_sets=4,
        rep_min=6,
        rep_max=10,
        sets=[{"reps": 10}, {"reps": 10}, {"reps": 10}, {"reps": 10}],
        current_weight=30,
    )
    assert "32.0" in msg


def test_recommend_overload_keep_weight():
    msg = recommend_overload(
        target_sets=4,
        rep_min=6,
        rep_max=10,
        sets=[{"reps": 8}, {"reps": 8}, {"reps": 7}, {"reps": 6}],
        current_weight=30,
    )
    assert "Continue" in msg
