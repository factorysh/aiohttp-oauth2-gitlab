# AIOhttp OAuth2 Gitlab demo

Authenticate aiohttp application with a middleware and Gitlab.

You need :

- [aiohttp](https://docs.aiohttp.org/)
- [aioauth-client](https://github.com/klen/aioauth-client)
- [aiohttp-session](https://github.com/aio-libs/aiohttp-session)


```python
from aiohttp import web

app = web.Application()
# now, add a session middleware
# ...

# then, add the aioauth gitlab middleware
add_gitlab_oauth(
app, client_id=client_id, client_secret=client_secret, base_url=base_url
)

```

## Example

Add an application to your Gitlab, with just `read_user`.

Set few environments vars : GITLAB_ID, GITLAB_SECRET, GITLAB_URL


    python3 -m venv venv
    ./venv/bin/activate
    pip install .
    python example/server.py

Go to http://localhost:5000

## Licence

3 terms BSD licence, ©2019 Mathieu Lecarme
