import base64
import logging

from aiohttp import web, ClientSession
from cryptography import fernet
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from aiohttp_oauth2_gitlab.middleware import add_gitlab_oauth


logging.basicConfig(level=logging.DEBUG)

routes = web.RouteTableDef()


@routes.get("/")
async def hello(request):
    session = await get_session(request)
    return web.Response(text="Hello, %s" % session.get("name"))


def make_app(client_id, client_secret, base_url):
    app = web.Application()  # plain old aiohttp application
    # secret_key must be 32 url-safe base64-encoded bytes
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))  # add session
    add_gitlab_oauth(
        app, client_id=client_id, client_secret=client_secret, base_url=base_url
    )  # add oauth2 gitlab middleware
    # oauth middleware must be after session middleware
    return app


if __name__ == "__main__":
    import os

    app = make_app(
        client_id=os.getenv("GITLAB_ID"),
        client_secret=os.getenv("GITLAB_SECRET"),
        base_url=os.getenv("GITLAB_URL"),
    )
    app.add_routes(routes)  # just the hello handler

    web.run_app(
        app, host="localhost", port=5000,
    )
