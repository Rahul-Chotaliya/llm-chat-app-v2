import requests
from app.main import get_response
import pytest # type: ignore
from app.main import ChatRequest # type: ignore

def test_dummy():
    assert True


def test_health_check():
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
