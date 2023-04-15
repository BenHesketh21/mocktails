from mocktails import create_app
from mocktails import rules

import pytest

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True
    })
    yield app


def test_rule_exists():
    pass