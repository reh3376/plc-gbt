import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parent.parent))

from api.cli_api_bridge import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"


def test_convert_l5x_to_json(tmp_path: Path, fixtures_dir: Path, client: TestClient) -> None:
    source = fixtures_dir / "minimal_controller.l5x"
    target = tmp_path / "out.json"

    response = client.post(
        "/api/v1/conversion/convert",
        json={
            "input_path": str(source),
            "output_path": str(target),
            "target_format": "json",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert Path(body["data"]["output"]).exists()


def test_validate_l5x(fixtures_dir: Path, client: TestClient) -> None:
    source = fixtures_dir / "minimal_controller.l5x"
    response = client.post(
        "/api/v1/conversion/validate",
        json={"file_path": str(source)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"], body
    assert body["data"]["controller"] == "TestController"


def test_inspect_l5x(fixtures_dir: Path, client: TestClient) -> None:
    source = fixtures_dir / "minimal_controller.l5x"
    response = client.get(
        "/api/v1/conversion/inspect",
        params={"path": str(source)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"]
    assert body["data"]["controller"] == "TestController"

