from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = ROOT / "Dockerfile"
DOCKER_COMPOSE = ROOT / "docker-compose.yml"


def test_dockerfile_includes_healthcheck_and_proxy_headers() -> None:
    content = DOCKERFILE.read_text(encoding="utf-8")

    assert "HEALTHCHECK" in content
    assert "http://127.0.0.1:8000/health" in content
    assert "--proxy-headers" in content
    assert "--forwarded-allow-ips" in content


def test_compose_includes_log_rotation_for_api() -> None:
    content = DOCKER_COMPOSE.read_text(encoding="utf-8")

    assert "logging:" in content
    assert "driver: json-file" in content
    assert 'max-size: "10m"' in content
    assert 'max-file: "5"' in content
