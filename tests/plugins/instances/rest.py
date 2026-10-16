from collections.abc import Iterator

import pytest
from django.core.asgi import get_asgi_application
from django.test import Client

from library.presentors.rest.application import RestApplication
from library.presentors.rest.service import RestService


@pytest.fixture
def client(db) -> Iterator[Client]:
    app = RestApplication(get_asgi_application())
    RestService().set_dependencies(app)
    try:
        yield Client(dishka_container=app.container)
    finally:
        app.close()
