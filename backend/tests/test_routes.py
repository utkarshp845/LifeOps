import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth import get_password_hash
from database import Base, get_db
from main import app
from models.user import User
import models  # noqa: F401
import routes.markets as markets_routes


def _client():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        db.add(User(username="test", password_hash=get_password_hash("password")))
        db.commit()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"username": "test", "password": "password"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_workout(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/workouts",
        headers=headers,
        json={
            "date": "2026-04-29",
            "notes": "Heavy pulls",
            "exercises": [{"name": "Deadlift", "sets": 3, "reps": 5, "weight_lbs": 315}],
        },
    )
    assert response.status_code == 201
    return response.json()


def create_book(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/books",
        headers=headers,
        json={"title": "Fear and Trembling", "author": "Soren Kierkegaard"},
    )
    assert response.status_code == 201
    return response.json()


def create_decision(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/decisions",
        headers=headers,
        json={
            "date": "2026-04-29",
            "title": "Decline a project",
            "context": "The work was misaligned.",
            "reasoning": "Capacity and direction both argued against it.",
            "expected_outcome": "More space for current commitments.",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_capture(client: TestClient, headers: dict[str, str], raw_text: str = "bench 185 5x5") -> dict:
    response = client.post("/captures", headers=headers, json={"raw_text": raw_text})
    assert response.status_code == 201
    return response.json()


def create_stock(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/markets/stocks",
        headers=headers,
        json={
            "ticker": "aapl",
            "company_name": "Apple Inc.",
            "shares": 5,
            "average_cost": 150,
            "thesis": "Durable ecosystem.",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_build_project(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/build/projects",
        headers=headers,
        json={
            "name": "Life OS",
            "description": "Personal operating system.",
            "status": "shipped",
            "shipped_at": "2026-04-29",
            "url": "https://example.com",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_wealth_snapshot(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/wealth/snapshots",
        headers=headers,
        json={
            "date": "2026-04-29",
            "cash": 10000,
            "investments": 50000,
            "retirement": 40000,
            "crypto": 5000,
            "other_assets": 15000,
            "debt": 20000,
            "annual_expenses": 50000,
            "financial_freedom_number": 1250000,
            "notes": "Baseline.",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_area(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/goals/areas",
        headers=headers,
        json={"name": "Health", "description": "Body, sleep, and energy.", "position": 1},
    )
    assert response.status_code == 201
    return response.json()


def create_goal(client: TestClient, headers: dict[str, str]) -> dict:
    area = create_area(client, headers)
    response = client.post(
        "/goals",
        headers=headers,
        json={
            "area_id": area["id"],
            "title": "Sleep 7 hours consistently",
            "why": "Energy drives everything else.",
            "target_date": "2026-05-15",
            "metric_name": "Average sleep",
            "target_value": 7,
            "current_value": 6,
            "unit": "hours",
        },
    )
    assert response.status_code == 201
    return response.json()


def create_review(client: TestClient, headers: dict[str, str]) -> dict:
    goal = create_goal(client, headers)
    response = client.post(
        "/reviews",
        headers=headers,
        json={
            "kind": "weekly",
            "date": "2026-04-29",
            "goal_id": goal["id"],
            "wins": "Protected mornings.",
            "friction": "Late screens.",
            "lessons": "Environment beats willpower.",
            "next_actions": "Phone outside bedroom.",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_auth_login_route():
    for client in _client():
        response = client.post("/auth/login", json={"username": "test", "password": "password"})
        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"


def test_protected_routes_require_jwt():
    for client in _client():
        response = client.get("/workouts")
        assert response.status_code == 401


def test_get_captures_route():
    for client in _client():
        response = client.get("/captures", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_captures_route():
    for client in _client():
        capture = create_capture(client, auth_headers(client), "Decision: keep the week quiet")
        assert capture["raw_text"] == "Decision: keep the week quiet"
        assert capture["status"] == "open"


def test_patch_captures_route_archives_and_reopens():
    for client in _client():
        headers = auth_headers(client)
        capture = create_capture(client, headers)

        archived = client.patch(f"/captures/{capture['id']}", headers=headers, json={"status": "archived"})
        assert archived.status_code == 200
        assert archived.json()["status"] == "archived"

        reopened = client.patch(f"/captures/{capture['id']}", headers=headers, json={"status": "open"})
        assert reopened.status_code == 200
        assert reopened.json()["status"] == "open"


def test_post_capture_convert_route_creates_real_target():
    for client in _client():
        headers = auth_headers(client)
        capture = create_capture(client, headers, "Slept 6.5, weight 181")
        response = client.post(
            f"/captures/{capture['id']}/convert",
            headers=headers,
            json={
                "target_type": "metric",
                "payload": {
                    "date": "2026-04-29",
                    "weight_lbs": 181.0,
                    "sleep_hours": 6.5,
                    "notes": "Slept 6.5, weight 181",
                },
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "converted"
        assert response.json()["target_type"] == "metric"

        metrics = client.get("/metrics", headers=headers)
        assert metrics.status_code == 200
        assert metrics.json()[0]["weight_lbs"] == 181.0


def test_capture_convert_route_rejects_repeat_conversion():
    for client in _client():
        headers = auth_headers(client)
        capture = create_capture(client, headers, "Kierkegaard unsettled me")
        payload = {
            "target_type": "philosophy",
            "payload": {
                "thinker": "Kierkegaard",
                "source": None,
                "disturbance": "Kierkegaard unsettled me",
                "date": "2026-04-29",
            },
        }
        first = client.post(f"/captures/{capture['id']}/convert", headers=headers, json=payload)
        assert first.status_code == 200

        second = client.post(f"/captures/{capture['id']}/convert", headers=headers, json=payload)
        assert second.status_code == 400


def test_capture_convert_route_supports_build_project():
    for client in _client():
        headers = auth_headers(client)
        capture = create_capture(client, headers, "Ship Life OS")
        response = client.post(
            f"/captures/{capture['id']}/convert",
            headers=headers,
            json={
                "target_type": "build_project",
                "payload": {
                    "name": "Life OS",
                    "description": "Ship Life OS",
                    "status": "shipped",
                    "shipped_at": "2026-04-29",
                },
            },
        )
        assert response.status_code == 200
        assert response.json()["target_type"] == "build_project"


def test_capture_convert_route_supports_goal():
    for client in _client():
        headers = auth_headers(client)
        capture = create_capture(client, headers, "Reach financial freedom")
        response = client.post(
            f"/captures/{capture['id']}/convert",
            headers=headers,
            json={
                "target_type": "goal",
                "payload": {
                    "title": "Reach financial freedom",
                    "why": "Own my time.",
                    "metric_name": "Net worth",
                    "target_value": 1250000,
                    "current_value": 100000,
                    "unit": "USD",
                },
            },
        )
        assert response.status_code == 200
        assert response.json()["target_type"] == "goal"


def test_get_goal_areas_route():
    for client in _client():
        response = client.get("/goals/areas", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_goal_areas_route():
    for client in _client():
        area = create_area(client, auth_headers(client))
        assert area["name"] == "Health"


def test_patch_goal_area_route():
    for client in _client():
        headers = auth_headers(client)
        area = create_area(client, headers)
        response = client.patch(f"/goals/areas/{area['id']}", headers=headers, json={"position": 2})
        assert response.status_code == 200
        assert response.json()["position"] == 2


def test_get_goals_route():
    for client in _client():
        response = client.get("/goals", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_goals_route():
    for client in _client():
        goal = create_goal(client, auth_headers(client))
        assert goal["title"] == "Sleep 7 hours consistently"
        assert round(goal["progress_pct"], 2) == 85.71


def test_get_goal_by_id_route():
    for client in _client():
        headers = auth_headers(client)
        goal = create_goal(client, headers)
        response = client.get(f"/goals/{goal['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["area"]["name"] == "Health"


def test_patch_goal_route():
    for client in _client():
        headers = auth_headers(client)
        goal = create_goal(client, headers)
        response = client.patch(f"/goals/{goal['id']}", headers=headers, json={"current_value": 7, "status": "achieved"})
        assert response.status_code == 200
        assert response.json()["status"] == "achieved"
        assert response.json()["progress_pct"] == 100.0


def test_get_goals_summary_route():
    for client in _client():
        headers = auth_headers(client)
        create_goal(client, headers)
        response = client.get("/goals/summary", headers=headers)
        assert response.status_code == 200
        assert response.json()["active_count"] == 1
        assert response.json()["due_soon_count"] == 1


def test_get_reviews_route():
    for client in _client():
        response = client.get("/reviews", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_reviews_route():
    for client in _client():
        review = create_review(client, auth_headers(client))
        assert review["kind"] == "weekly"
        assert review["goal"]["title"] == "Sleep 7 hours consistently"


def test_get_review_by_id_route():
    for client in _client():
        headers = auth_headers(client)
        review = create_review(client, headers)
        response = client.get(f"/reviews/{review['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["wins"] == "Protected mornings."


def test_patch_review_route():
    for client in _client():
        headers = auth_headers(client)
        review = create_review(client, headers)
        response = client.patch(f"/reviews/{review['id']}", headers=headers, json={"lessons": "Earlier shutdown matters."})
        assert response.status_code == 200
        assert response.json()["lessons"] == "Earlier shutdown matters."


def test_get_reviews_due_route():
    for client in _client():
        response = client.get("/reviews/due", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json()["daily_done"] is False


def test_get_market_stocks_route():
    for client in _client():
        response = client.get("/markets/stocks", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_market_stocks_route():
    for client in _client():
        stock = create_stock(client, auth_headers(client))
        assert stock["ticker"] == "AAPL"
        assert stock["shares"] == 5.0


def test_get_market_stock_by_id_route():
    for client in _client():
        headers = auth_headers(client)
        stock = create_stock(client, headers)
        response = client.get(f"/markets/stocks/{stock['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["company_name"] == "Apple Inc."


def test_patch_market_stock_route():
    for client in _client():
        headers = auth_headers(client)
        stock = create_stock(client, headers)
        response = client.patch(f"/markets/stocks/{stock['id']}", headers=headers, json={"watchlist": True, "shares": 6})
        assert response.status_code == 200
        assert response.json()["watchlist"] is True
        assert response.json()["shares"] == 6.0


def test_get_market_stock_quote_route(monkeypatch):
    for client in _client():
        headers = auth_headers(client)
        stock = create_stock(client, headers)

        def fake_quote(ticker):
            return {
                "ticker": ticker,
                "price": 210.5,
                "change_amount": 1.2,
                "change_percent": 0.57,
                "currency": "USD",
                "provider": "alphavantage",
            }

        monkeypatch.setattr(markets_routes, "fetch_quote_from_provider", fake_quote)
        response = client.get(f"/markets/stocks/{stock['id']}/quote", headers=headers)
        assert response.status_code == 200
        assert response.json()["price"] == 210.5


def test_get_build_projects_route():
    for client in _client():
        response = client.get("/build/projects", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_build_projects_route():
    for client in _client():
        project = create_build_project(client, auth_headers(client))
        assert project["name"] == "Life OS"
        assert project["status"] == "shipped"


def test_get_build_project_by_id_route():
    for client in _client():
        headers = auth_headers(client)
        project = create_build_project(client, headers)
        response = client.get(f"/build/projects/{project['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["description"] == "Personal operating system."


def test_patch_build_project_route():
    for client in _client():
        headers = auth_headers(client)
        project = create_build_project(client, headers)
        response = client.patch(f"/build/projects/{project['id']}", headers=headers, json={"status": "maintained"})
        assert response.status_code == 200
        assert response.json()["status"] == "maintained"


def test_get_wealth_snapshots_route():
    for client in _client():
        response = client.get("/wealth/snapshots", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_wealth_snapshots_route():
    for client in _client():
        snapshot = create_wealth_snapshot(client, auth_headers(client))
        assert snapshot["net_worth"] == 100000.0
        assert snapshot["progress_pct"] == 8.0


def test_get_wealth_summary_route():
    for client in _client():
        headers = auth_headers(client)
        create_wealth_snapshot(client, headers)
        response = client.get("/wealth/summary", headers=headers)
        assert response.status_code == 200
        assert response.json()["net_worth"] == 100000.0
        assert response.json()["runway_years"] == 2.0


def test_get_workouts_route():
    for client in _client():
        response = client.get("/workouts", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_workouts_route():
    for client in _client():
        workout = create_workout(client, auth_headers(client))
        assert workout["notes"] == "Heavy pulls"
        assert workout["exercises"][0]["name"] == "Deadlift"


def test_get_workout_by_id_route():
    for client in _client():
        headers = auth_headers(client)
        workout = create_workout(client, headers)
        response = client.get(f"/workouts/{workout['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == workout["id"]


def test_post_workout_exercises_route():
    for client in _client():
        headers = auth_headers(client)
        workout = create_workout(client, headers)
        response = client.post(
            f"/workouts/{workout['id']}/exercises",
            headers=headers,
            json={"name": "Row", "sets": 4, "reps": 8, "weight_lbs": 135},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Row"


def test_get_workouts_history_route():
    for client in _client():
        headers = auth_headers(client)
        create_workout(client, headers)
        response = client.get("/workouts/history", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) == 1


def test_get_golf_route():
    for client in _client():
        response = client.get("/golf", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_golf_route():
    for client in _client():
        response = client.post(
            "/golf",
            headers=auth_headers(client),
            json={"date": "2026-04-29", "course": "Bethpage Black", "score": 88, "notes": "Windy"},
        )
        assert response.status_code == 201
        assert response.json()["course"] == "Bethpage Black"


def test_get_metrics_route():
    for client in _client():
        response = client.get("/metrics", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_metrics_route():
    for client in _client():
        headers = auth_headers(client)
        response = client.post(
            "/metrics",
            headers=headers,
            json={"date": "2026-04-29", "weight_lbs": 180.5, "sleep_hours": 7.2, "notes": "Solid"},
        )
        assert response.status_code == 201
        assert response.json()["sleep_hours"] == 7.2

        second = client.post(
            "/metrics",
            headers=headers,
            json={"date": "2026-04-29", "weight_lbs": 181.0, "sleep_hours": 6.8, "notes": "Updated"},
        )
        assert second.status_code == 201
        assert second.json()["weight_lbs"] == 181.0


def test_get_books_route():
    for client in _client():
        response = client.get("/books", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_books_route():
    for client in _client():
        book = create_book(client, auth_headers(client))
        assert book["title"] == "Fear and Trembling"


def test_get_book_by_id_route():
    for client in _client():
        headers = auth_headers(client)
        book = create_book(client, headers)
        response = client.get(f"/books/{book['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["author"] == "Soren Kierkegaard"


def test_patch_book_route_only_allows_finished_date_and_reaction():
    for client in _client():
        headers = auth_headers(client)
        book = create_book(client, headers)
        response = client.patch(
            f"/books/{book['id']}",
            headers=headers,
            json={"date_finished": "2026-04-29", "my_reaction": "It unsettled me."},
        )
        assert response.status_code == 200
        assert response.json()["my_reaction"] == "It unsettled me."

        rejected = client.patch(f"/books/{book['id']}", headers=headers, json={"title": "Changed"})
        assert rejected.status_code == 422


def test_get_philosophy_route():
    for client in _client():
        response = client.get("/philosophy", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_philosophy_route():
    for client in _client():
        response = client.post(
            "/philosophy",
            headers=auth_headers(client),
            json={
                "thinker": "Kierkegaard",
                "source": "The Sickness Unto Death",
                "disturbance": "It challenged my evasions.",
                "date": "2026-04-29",
            },
        )
        assert response.status_code == 201
        assert response.json()["disturbance"] == "It challenged my evasions."


def test_philosophy_notes_have_no_patch_route():
    for client in _client():
        response = client.patch("/philosophy/not-a-real-note", headers=auth_headers(client), json={"disturbance": "edit"})
        assert response.status_code == 404


def test_get_decisions_route():
    for client in _client():
        response = client.get("/decisions", headers=auth_headers(client))
        assert response.status_code == 200
        assert response.json() == []


def test_post_decisions_route():
    for client in _client():
        decision = create_decision(client, auth_headers(client))
        assert decision["title"] == "Decline a project"


def test_get_decision_by_id_route():
    for client in _client():
        headers = auth_headers(client)
        decision = create_decision(client, headers)
        response = client.get(f"/decisions/{decision['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == decision["id"]


def test_patch_decision_route_only_updates_actual_outcome_and_reviewed_at():
    for client in _client():
        headers = auth_headers(client)
        decision = create_decision(client, headers)
        response = client.patch(
            f"/decisions/{decision['id']}",
            headers=headers,
            json={"actual_outcome": "The space mattered.", "reviewed_at": "2026-05-10"},
        )
        assert response.status_code == 200
        assert response.json()["actual_outcome"] == "The space mattered."

        rejected = client.patch(f"/decisions/{decision['id']}", headers=headers, json={"title": "Changed"})
        assert rejected.status_code == 422
