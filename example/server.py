import base64
import logging

from aiohttp import web, ClientSession
from cryptography import fernet
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from aio_http_oauth2_gitlab.middleware import add_gitlab_oauth


logging.basicConfig(level=logging.DEBUG)

routes = web.RouteTableDef()


@routes.get("/")
async def hello(request):
    session = await get_session(request)
    return web.Response(text="Hello, %s" % session.get("name"))


def make_app(client_id, client_secret, base_url):
    app = web.Application()
    # secret_key must be 32 url-safe base64-encoded bytes
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))
    add_gitlab_oauth(
        app, client_id=client_id, client_secret=client_secret, base_url=base_url
    )
    # oauth middleware must be after session middleware
    app.add_routes(routes)
    return app


if __name__ == "__main__":
    import os

    web.run_app(
        make_app(
            client_id=os.getenv("GITLAB_ID"),
            client_secret=os.getenv("GITLAB_SECRET"),
            base_url=os.getenv("GITLAB_URL"),
        ),
        host="localhost",
        port=5000,
    )
