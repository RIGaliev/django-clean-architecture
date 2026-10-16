import logging
import os

from aiomisc.service.uvicorn import UvicornApplication, UvicornService
from dishka import make_container
from django.conf import settings
from django.core.asgi import get_asgi_application

from library.adapters.database.di import DatabaseProvider
from library.domains.di import DomainProvider
from library.presentors.rest.application import RestApplication

log = logging.getLogger(__name__)


class RestService(UvicornService):
    settings_module: str = "library.presentors.rest.settings"
    lifespan = "off"
    app: RestApplication | None = None

    async def create_application(self) -> UvicornApplication:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", self.settings_module)
        app = RestApplication(get_asgi_application())
        self.set_dependencies(app)
        self.app = app

        log.info("REST service app configured")
        return app

    def set_dependencies(self, app: RestApplication) -> None:
        app.container = make_container(
            DatabaseProvider(debug=settings.DEBUG), DomainProvider()
        )

    async def stop(self, exception: Exception | None = None) -> None:
        try:
            if hasattr(self, "serve_task"):
                await super().stop(exception)
        finally:
            if self.app is not None:
                self.app.close(exception)
                self.app = None
