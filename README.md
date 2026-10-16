# Django clean architecture

Example REST web service for internet library with:

- clean architecture with interfaces, layers and entities
- Dependency Injection with [dishka](https://github.com/reagento/dishka)
- auto tests with [pytest](https://docs.pytest.org/en/stable/)
- formatting and linting with [ruff](https://github.com/astral-sh/ruff) and [mypy](https://github.com/python/mypy)
- Dockerfile with best practices
- CI/CD with Github Workflows with separated actions
- [pre-commit](https://github.com/pre-commit/pre-commit) features

## Working with repos

### How to install dependencies?

Creating new venv in project folder and install all dependencies with poetry:

```bash
make develop
```

### How to run dev containers for testing?

Start postgres container described in `docker-compose.dev.yaml` from scratch:

```bash
make local
```

### How to run the REST service?

Start the Django ASGI application with aiomisc and Uvicorn:

```bash
.venv/bin/python -m library
```

The service listens on port 8000 and is available locally at
`http://127.0.0.1:8000`. Django routes and middleware are configured in
`library/presentors/rest/settings.py`. `RestService.set_dependencies(app)` attaches
a Dishka container to the ASGI `RestApplication` wrapper, which passes it to Django
through the request scope. The service closes the container after the HTTP server
stops. The Django test client fixture initializes dependencies through the same
service method and passes the container in WSGI environ. Other entry points must
explicitly initialize and pass a container; middleware does not create one.

### How to run tests?

The tests must be run after the dependencies are installed and when the `make local` process is running separately:

```bash
pytest -vx ./tests
```
