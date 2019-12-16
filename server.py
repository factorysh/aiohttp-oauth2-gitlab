from aioauth_client import OAuth2Client


class GitlabClient(OAuth2Client):
    base_url = "https://gitlab.com"
    access_token_url = "/oauth/token"
    authorize_url =  "/oauth/authorize"
    name = "gitlab"


if __name__ == "__main__":
    import os
    g = GitlabClient(client_id=os.getenv('GITLAB_ID'),
                     client_secret=os.getenv('GITLAB_SECRET'),
                     base_url=os.getenv('GITLAB_URL'))
    print("".join([g.base_url, g.get_authorize_url(scope="read_user",
                                                   redirect_uri="http://localhost:5000/redirect")]))
