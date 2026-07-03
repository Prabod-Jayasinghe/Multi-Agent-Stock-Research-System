"""
tests/test_health.py
Phase 1 smoke test — verifies the FastAPI app starts and /health responds.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_root_returns_service_info():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Multi-Agent Stock Research System"
    assert data["status"] == "running"


def test_research_stub_returns_501():
    response = client.post("/api/research", json={"ticker": "AAPL"})
    assert response.status_code == 501


def test_history_stub_returns_501():
    response = client.get("/api/history")
    assert response.status_code == 501
