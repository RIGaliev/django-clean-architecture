from typing import cast

from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGISendCallable,
    Scope,
)
from dishka import Container


class RestApplication:
    def __init__(self, app: ASGI3Application) -> None:
        self.app = app
        self.container: Container | None = None

    async def __call__(
        self,
        scope: Scope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
    ) -> None:
        if self.container is None:
            raise RuntimeError("REST application dependencies are not configured")

        request_scope = cast(Scope, {**scope, "dishka_container": self.container})
        await self.app(request_scope, receive, send)

    def close(self, exception: BaseException | None = None) -> None:
        container = self.container
        self.container = None
        if container is not None:
            container.close(exception=exception)
