from aiomisc import entrypoint

from library.presentors.rest.service import RestService


def main() -> None:
    service = RestService(host="0.0.0.0", port=8000)

    with entrypoint(service) as loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
