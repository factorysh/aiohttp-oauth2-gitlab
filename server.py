import uuid
import base64
import logging

from aioauth_client import OAuth2Client

from aiohttp import web, ClientSession
from cryptography import fernet
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage


logging.basicConfig(level=logging.DEBUG)


routes = web.RouteTableDef()

@web.middleware
async def gitlab_oauth_middleware(request, handler):
    # No middlware for path /redirected
    if request.path == '/redirected':
        return await handler(request)

    session = await get_session(request)
    g = request.app['gitlab']
    token = session.get('access_token')
    if token is None:
        t = uuid.uuid4().hex
        session['oauth_token'] = t
        session['my_url'] = str(request.url)
        raise web.HTTPFound("".join([g.base_url,
                                     g.get_authorize_url(scope="read_user",
                                                         state=t,
                                                         redirect_uri="http://localhost:5000/redirected")]))
    name = session.get('name')
    print("name", name)
    if name is None:
        me = await request.app['gitlab'].request('GET', '/api/v4/user', access_token=token)
        print("me", me)
        session['name'] = me['name']
    resp = await handler(request)
    return resp


@routes.get('/redirected')
async def redirected(request):
    """
    The user came from gitlab authentification page, he is authenticated
    """
    session = await get_session(request)
    t = session['oauth_token']
    if t is None:
        raise web.HTTPBadRequest()
    if request.query['state'] != t:
        # OMG, the redirected call is forged
        raise web.HTTPBadRequest()
    my_url = session['my_url']
    if my_url is None: # It should not happen
        raise web.HTTPFound("/")

    code = request.query['code']
    print("code", code)
    token, data = await request.app['gitlab'].get_access_token(code,
                                                               redirect_uri="http://localhost:5000/redirected")
    print("token", token)
    print("data", data)
    session['refresh_token'] = data['refresh_token']
    session['access_token'] = token
    async with ClientSession() as session:
        async with session.get('%s/api/v4/user?access_token=%s' % (request.app['gitlab'].base_url, token)) as resp:
            print(resp.status)
            print(await resp.text())
    raise web.HTTPFound(my_url)


@routes.get('/')
async def hello(request):
    session = await get_session(request)
    return web.Response(text="Hello, %s" % session.get('name'))


def make_app(client_id, client_secret, base_url):
    app = web.Application()
    app['gitlab'] = GitlabClient(client_id=client_id,
                                 client_secret=client_secret,
                                 base_url=base_url)
    # secret_key must be 32 url-safe base64-encoded bytes
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup(app, EncryptedCookieStorage(secret_key))
    # oauth middleware must be after session middleware
    app.middlewares.append(gitlab_oauth_middleware)
    app.add_routes(routes)
    return app


class GitlabClient(OAuth2Client):
    base_url = "https://gitlab.com"
    access_token_url = "/oauth/token"
    authorize_url =  "/oauth/authorize"
    name = "gitlab"
    user_info_url = "/api/v4/user"
    access_token_key = "access_token"


if __name__ == "__main__":
    import os
    web.run_app(make_app(client_id=os.getenv('GITLAB_ID'),
                         client_secret=os.getenv('GITLAB_SECRET'),
                         base_url=os.getenv('GITLAB_URL')),
                host='localhost', port=5000)
