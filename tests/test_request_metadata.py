from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from src.infrastructure.fastapi.request_metadata import get_client_ip, get_x_forwarded_for


def _build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/meta")
    async def meta(request: Request) -> dict[str, str]:
        return {
            "client_ip": get_client_ip(request),
            "x_forwarded_for": get_x_forwarded_for(request),
        }

    return app


def test_get_client_ip_prefers_first_x_forwarded_for_hop() -> None:
    app = _build_app()
    with TestClient(app) as client:
        response = client.get("/meta", headers={"X-Forwarded-For": "198.51.100.10, 10.0.0.1"})

    assert response.status_code == 200
    body = response.json()
    assert body["client_ip"] == "198.51.100.10"
    assert body["x_forwarded_for"] == "198.51.100.10, 10.0.0.1"


def test_get_client_ip_uses_x_real_ip_when_forwarded_for_is_absent() -> None:
    app = _build_app()
    with TestClient(app) as client:
        response = client.get("/meta", headers={"X-Real-IP": "203.0.113.22"})

    assert response.status_code == 200
    assert response.json()["client_ip"] == "203.0.113.22"


def test_get_client_ip_falls_back_to_request_client_host() -> None:
    app = _build_app()
    with TestClient(app) as client:
        response = client.get("/meta")

    assert response.status_code == 200
    assert response.json()["client_ip"] != "unknown"
