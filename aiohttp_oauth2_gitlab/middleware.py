import uuid

from aiohttp import web
from aiohttp_session import get_session

from aiohttp_oauth2_gitlab.gitlab import GitlabClient

REDIRECTED = "/redirected"


def base_url(request):
    b = request.app.get("base_url")
    if b is not None:
        return b
    b = "%s://%s" % (request.url.scheme, request.url.host)
    p = request.url.port
    if (request.url.scheme == "https" and p != 443) or (p != 80):
        return "%s:%s" % (b, str(p))
    return b


def redirected_url(request):
    return "".join([base_url(request), REDIRECTED])


async def redirected(request):
    """
    The user came from gitlab authentification page, he is authenticated
    """
    session = await get_session(request)
    t = session["oauth_state"]
    if t is None:
        raise web.HTTPBadRequest()
    if request.query["state"] != t:
        # OMG, the redirected call is forged
        raise web.HTTPBadRequest()
    my_url = session["my_url"]
    if my_url is None:  # It should not happen
        raise web.HTTPFound("/")

    code = request.query["code"]
    token, data = await request.app["gitlab"].get_access_token(
        code, redirect_uri=redirected_url(request)
    )
    session["refresh_token"] = data["refresh_token"]
    session["access_token"] = token
    raise web.HTTPFound(my_url)


@web.middleware
async def gitlab_oauth_middleware(request, handler):
    # No middlware for path /redirected
    if request.path == REDIRECTED:
        return await handler(request)

    session = await get_session(request)
    g = request.app["gitlab"]
    token = session.get("access_token")
    if token is None:
        t = uuid.uuid4().hex
        session["oauth_state"] = t
        session["my_url"] = str(request.url)
        raise web.HTTPFound(
            "".join(
                [
                    g.base_url,
                    g.get_authorize_url(
                        scope="read_user",
                        state=t,
                        redirect_uri=redirected_url(request),
                    ),
                ]
            )
        )
    name = session.get("name")
    if name is None:
        me = await request.app["gitlab"].request(
            "GET", "/api/v4/user", access_token=token
        )
        # print("me", me)
        session["name"] = me["name"]
    resp = await handler(request)
    return resp


def add_gitlab_oauth(app, client_id, client_secret, base_url):
    app["gitlab"] = GitlabClient(
        client_id=client_id, client_secret=client_secret, base_url=base_url
    )
    app.middlewares.append(gitlab_oauth_middleware)
    app.add_routes([web.get(REDIRECTED, redirected)])
