__all__ = [
    "FromDishka",
    "inject",
]

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from dishka import FromDishka
from dishka.integrations.base import wrap_injection
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.request import Request

T = TypeVar("T")
P = ParamSpec("P")


def inject(func: Callable[P, T]) -> Callable[[Request, P.args, P.kwargs], T]:
    @wraps(func)
    def wrapper(request: Request, *args: P.args, **kwargs: P.kwargs) -> T:
        dishka_container = request.dishka_container
        with dishka_container() as container:
            injected_func = wrap_injection(
                func=func,
                container_getter=lambda _, p: container,
                is_async=False,
            )
            return injected_func(request, *args, **kwargs)

    return wrapper


class ContainerMiddleware(MiddlewareMixin):
    async_capable = False

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: Request) -> HttpResponse:
        # ASGI uses scope; WSGI test clients pass the container in environ.
        container = getattr(request, "scope", request.META).get("dishka_container")
        if container is None:
            raise ImproperlyConfigured(
                "Dishka container is missing. Initialize dependencies through "
                "RestService.set_dependencies(app) and pass the container "
                "in the request scope or WSGI environ."
            )
        request.dishka_container = container
        return self.get_response(request)
