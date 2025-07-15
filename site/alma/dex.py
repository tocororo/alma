from email.mime import base
from flask import current_app
from invenio_db import db

from invenio_oauthclient.contrib.settings import OAuthSettingsHelper

class DexOAuthSettingsHelper(OAuthSettingsHelper):
    """Default configuration for ORCID OAuth provider."""

    def __init__(
        self,
        title="Dex OpenID",
        description="Connecting to Dex OpenID", 
        icon= "fa fa-graduation",
        base_url='http://127.0.0.1:5556',
    ):
        super().__init__(
            title=title,
            description=description,
            icon=icon,
            base_url=base_url,
            app_key="DEX_APP_CREDENTIALS",
            access_token_url=f"{base_url}/token",
            authorize_url=f"{base_url}/auth",
            access_token_method="POST",
            request_token_params={'scope': 'openid email profile'},
            request_token_url=None,
            precedence_mask=None,
            signup_options=None,
            logout_url=None,
            hide_when=False,
        )
        self._handlers = dict(
            authorized_handler="invenio_oauthclient.handlers:authorized_signup_handler",
            disconnect_handler="invenio_oauthclient.handlers:disconnect_handler",
            signup_handler=dict(
                info=dex_account_info,
                info_serializer=dex_account_info_serializer,
                setup=dex_account_setup,
                view="invenio_oauthclient.handlers:signup_handler",
            ),
        )
        self._rest_handlers = dict(
            authorized_handler="invenio_oauthclient.handlers.rest"
            ":authorized_signup_handler",
            disconnect_handler="invenio_oauthclient.handlers.rest"
            ":disconnect_handler",
            signup_handler=dict(
                info=dex_account_info,
                info_serializer=dex_account_info_serializer,
                setup=dex_account_setup,
                view="invenio_oauthclient.handlers.rest:signup_handler",
            ),
            response_handler="invenio_oauthclient.handlers.rest"
            ":default_remote_response_handler",
            authorized_redirect_url="/",
            disconnect_redirect_url="/",
            signup_redirect_url="/",
            error_redirect_url="/",
        )

    def get_handlers(self):
        """Return GitHub auth handlers."""
        return self._handlers

    def get_rest_handlers(self):
        """Return GitHub auth REST handlers."""
        return self._rest_handlers
    



# upr = DexOAuthSettingsHelper(
#     title="Dex OpenID",
#     description="Connecting to Dex OpenID", 
#     icon= "fa fa-graduation",
#     base_url='http://127.0.0.1:5556',
# )

# BASE_APP = upr.base_app
# REMOTE_APP = upr.remote_app

DEX_ID_AFF = {
    'localhost-alma': 'Universidad de Pinar del Río "Hermanos Saíz Montes de Oca"',
    'upr-alma':  'Universidad de Pinar del Río "Hermanos Saíz Montes de Oca"',
}

def dex_account_info(remote, resp):
    """Retrieve remote account information used to find local user."""
    
    user_info = remote.get('userinfo').data
    
    email=user_info.get('email')
    username = email.split('@')[0]
    aud = user_info.get('aud')
    aff = DEX_ID_AFF[aud] if aud  in DEX_ID_AFF else ''

    

    # Map Dex response to Invenio account info
    return dict(
        user=dict(
            email=user_info.get('email'),
            profile=dict(
                username=username,
                full_name=user_info.get('name'),
                affiliations=aff,
            ),
        ),
        external_id=user_info.get('sub'),
        external_method='dex',
        active=True
    )

def dex_account_info_serializer(remote, resp, **kwargs):
    """Serialize the account info response object.

    :param remote: The remote application.
    :param resp: The response of the `authorized` endpoint.
    :returns: A dictionary with serialized user information.
    """
    return {
        "external_id": resp.get("orcid"),
        "external_method": remote.name,
        "user": {
            "profile": {
                "full_name": resp.get("name"),
            },
        },
    }

def dex_account_setup(remote, token, resp):
    """Perform additional setup after user have been logged in."""
    # TODO: ver con un ldap real como es, si realmente necesito hacer algo mas.., porque por el momento no... 

    
    print(remote)
    print('--------------------')
    print(token)
    print('-----------------')
    print(resp)
    print('-----------------')
    user_info = remote.get('userinfo').data
    print(user_info)
    
    # Set extra data on the account
    # with db.session.begin_nested():
    # with current_app.security.datastore.commit_nested():
    #     user = token.remote_account.user
    #     if user_info.get('email'):
    #         user.email = user_info.get('email')
    #     if user_info.get('name'):
    #         user.user_profile.full_name = user_info.get('name')
    #     if user_info.get('preferred_username'):
    #         user.username = user_info.get('preferred_username')
        
    #     current_app.security.datastore.commit()



# DEX_OPENID_CONFIG = dict(
#     title="Dex OpenID",
#     description="Connecting to Dex OpenID", 
#     icon= "fa fa-university",
#     base_url='http://127.0.0.1:5556',
#     credentials = dict(
#         consumer_key='localhost-alma',  # Client ID from Dex
#         consumer_secret='your_strong_secret_here',  # Secret from Dex
#     )
# )

# DEX_CONFIG = current_app.config.get("DEX_OPENID_CONFIG", DEX_OPENID_CONFIG)

#     # logout_url="https://auth.cern.ch/auth/realms/cern/protocol/"   "openid-connect/logout",

# BASE_APP = dict(
#     title=DEX_CONFIG["title"],
#     description=DEX_CONFIG["description"],
#     icon=DEX_CONFIG["icon"],
#     signup_options={
#         "auto_confirm": True,
#         "send_register_msg": False,
#     },
#     params=dict(
#         base_url=DEX_CONFIG['base_url'],
#         request_token_params={'scope': 'openid email profile'},
#         access_token_url=f"{DEX_CONFIG['base_url']}/token",
#         authorize_url=f"{DEX_CONFIG['base_url']}/auth",
#         access_token_method="POST",
#         app_key= DEX_CONFIG['credentials'],
#         content_type="application/json",
#     ),
# )