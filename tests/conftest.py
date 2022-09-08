import os
from typing import Any

import pytest
import requests
from requests.exceptions import ConnectionError


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: Any) -> str:
    """Override default location of docker-compose.yml file."""
    return os.path.join(str(pytestconfig.rootdir), "./", "docker-compose.yml")


@pytest.fixture(scope="session")
def service(docker_ip: str, docker_services: Any) -> str:
    """Ensure that service is up and responsive."""
    port = docker_services.port_for("rdf-diff-store", 80)
    url = f"http://{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=30, pause=0.1, check=lambda: is_ok(f"{url}/readyz", 200)
    )
    return url


def is_ok(url: str, code: int = 200) -> bool:
    """Check if service returns correct status."""
    try:
        response = requests.get(url)
        return response.status_code == code
    except ConnectionError:
        return False
