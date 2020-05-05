import os
import pytest
import requests

from requests.exceptions import ConnectionError


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(
        str(pytestconfig.rootdir),
        "opsdroid_homeassistant",
        "tests",
        "docker-compose.yml",
    )


@pytest.fixture(scope="session")
def access_token():
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIzYzIwODIyN2MyNTE0OGU5YThhYzg4YTdhYTMxYzgwOCIsImlhdCI6MTU4ODcxNTA2OSwiZXhwIjoxOTA0MDc1MDY5fQ.oPhla3M9WFsEkOfLrNetkl8p7x96ogWrXHcusLxbwzI"


@pytest.fixture(scope="session")
def homeassistant(docker_ip, docker_services, access_token):
    """Ensure that Home Assistant is up and responsive."""

    def is_responsive(url, headers):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return True
        except ConnectionError:
            return False

    port = docker_services.port_for("homeassistant", 8123)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: is_responsive(url, {"Authorization": "Bearer " + access_token}),
    )
    return url
