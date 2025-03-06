import pytest
from backend import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_handle_message(client):
    payload = {
        "command": "Hey, I'm serious",
        "context": {"private": True, "mode": "casual"}
    }
    response = client.post("/message", json=payload)
    data = response.get_json()
    assert "final_response" in data
    assert "agent_responses" in data
