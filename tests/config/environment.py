"""
Environment Configuration Module for StreamEMI Test Automation
Supports multi-environment execution (LOCAL, STAGING, PROD) with configurable endpoints.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class TestEnvironment:
    name: str
    base_url: str
    api_url: str
    headless: bool
    slow_mo: int
    timeout: int


ENVIRONMENTS = {
    "local": TestEnvironment(
        name="local",
        base_url=os.getenv("BASE_URL", "http://127.0.0.1:5001"),
        api_url=os.getenv("API_URL", "http://127.0.0.1:5001/api"),
        headless=os.getenv("HEADLESS", "true").lower() == "true",
        slow_mo=int(os.getenv("SLOW_MO", "0")),
        timeout=int(os.getenv("TEST_TIMEOUT", "30000")),
    ),
    "staging": TestEnvironment(
        name="staging",
        base_url=os.getenv("STAGING_BASE_URL", "https://staging.streamemi.streamhub.internal"),
        api_url=os.getenv("STAGING_API_URL", "https://staging.streamemi.streamhub.internal/api"),
        headless=True,
        slow_mo=0,
        timeout=45000,
    ),
    "prod": TestEnvironment(
        name="prod",
        base_url=os.getenv("PROD_BASE_URL", "https://streamemi.streamhub.internal"),
        api_url=os.getenv("PROD_API_URL", "https://streamemi.streamhub.internal/api"),
        headless=True,
        slow_mo=0,
        timeout=60000,
    ),
}


def get_current_environment() -> TestEnvironment:
    env_name = os.getenv("TEST_ENV", "local").lower()
    return ENVIRONMENTS.get(env_name, ENVIRONMENTS["local"])
