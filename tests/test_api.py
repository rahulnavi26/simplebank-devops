from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def new_account(owner="Test User"):
    response = client.post("/accounts", json={"owner": owner})
    assert response.status_code == 201
    return response.json()["id"]


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_reports_env_and_git_sha():
    response = client.get("/version")
    assert response.status_code == 200
    assert set(response.json()) == {"env", "git_sha"}


def test_create_account_starts_with_zero_balance():
    response = client.post("/accounts", json={"owner": "Rahul"})
    assert response.status_code == 201
    body = response.json()
    assert body["owner"] == "Rahul"
    assert body["balance_paise"] == 0


def test_create_account_rejects_empty_owner():
    response = client.post("/accounts", json={"owner": ""})
    assert response.status_code == 422


def test_get_unknown_account_returns_404():
    response = client.get("/accounts/999999")
    assert response.status_code == 404


def test_deposit_adds_to_balance():
    account_id = new_account()
    first = client.post(f"/accounts/{account_id}/deposit", json={"amount_paise": 50000})
    assert first.status_code == 200
    assert first.json()["balance_paise"] == 50000
    second = client.post(f"/accounts/{account_id}/deposit", json={"amount_paise": 2500})
    assert second.json()["balance_paise"] == 52500


def test_deposit_rejects_zero_and_negative_amounts():
    account_id = new_account()
    for bad_amount in (0, -5):
        response = client.post(
            f"/accounts/{account_id}/deposit", json={"amount_paise": bad_amount}
        )
        assert response.status_code == 422


def test_deposit_to_unknown_account_returns_404():
    response = client.post("/accounts/999999/deposit", json={"amount_paise": 100})
    assert response.status_code == 404
