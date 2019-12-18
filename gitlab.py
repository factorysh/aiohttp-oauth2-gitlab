from aioauth_client import OAuth2Client


class GitlabClient(OAuth2Client):
    base_url = "https://gitlab.com"
    access_token_url = "/oauth/token"
    authorize_url =  "/oauth/authorize"
    name = "gitlab"
    user_info_url = "/api/v4/user"
    access_token_key = "access_token"
