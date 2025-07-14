
from invenio_oauthclient.contrib.settings import OAuthSettingsHelper
from invenio_oauthclient.errors import OAuthRejectedRequestError

from flask import current_app, redirect, url_for
from invenio_oauthclient.handlers import authorized_signup_handler
from invenio_oauthclient.utils import create_csrf_disabled_registrationform
# from invenio_oauthclient.contrib import get_dict_from_response



def get_dict_from_response(response):
    """Prepare new mapping with 'Value's grouped by 'Type'."""
    result = {}
    if getattr(response, "_resp") and response._resp.code > 400:
        return result

    for key, value in response.data.items():
        result.setdefault(key, value)
    return result



class DexOAuthSettingsHelper(OAuthSettingsHelper):
    def __init__(self):
        super().__init__(
            title="Dex OAuth2",
            description="Login via University of Pinar del Río's Dex IdP",
            base_url="https://idp.upr.edu.cu/",
            app_key="DEX_APP_CREDENTIALS",
            access_token_url="https://idp.upr.edu.cu/token",
            authorize_url="https://idp.upr.edu.cu/auth",
            userinfo_url="https://idp.upr.edu.cu/userinfo",
            jwks_url="https://idp.upr.edu.cu/keys",
            # Dex supports these token endpoint auth methods
            token_endpoint_auth_methods_supported=["client_secret_basic", "client_secret_post"],
        )

    def get_handlers(self):
        """Return Dex auth handlers."""
        return dict(
            authorized_handler='invenio_oauthclient.handlers:authorized_signup_handler',
            disconnect_handler=dex_disconnect_handler,
            signup_handler=dict(
                info=dex_account_info,
                setup=dex_account_setup,
                view='invenio_oauthclient.handlers:signup_handler',
            )
        )

    def get_rest_handlers(self):
        """Return Dex REST auth handlers."""
        return dict(
            authorized_handler='invenio_oauthclient.handlers.rest:authorized_signup_handler',
            disconnect_handler=dex_disconnect_handler,
            signup_handler=dict(
                info=dex_account_info,
                setup=dex_account_setup,
                view='invenio_oauthclient.handlers.rest:signup_handler',
            ),
            response_handler='invenio_oauthclient.handlers.rest:default_remote_response_handler',
            authorized_redirect_url='/',
            disconnect_redirect_url='/',
            signup_redirect_url='/',
            error_redirect_url='/'
        )



def dex_account_info(remote, resp):
    """Retrieve remote account information used to find local user."""
    user_info = remote.get('userinfo').data
    
    # Map Dex response to Invenio account info
    return dict(
        user=dict(
            email=user_info.get('email'),
            profile=dict(
                username=user_info.get('preferred_username'),
                full_name=user_info.get('name'),
            ),
        ),
        external_id=user_info.get('sub'),
        external_method='dex',
        active=True
    )

def dex_account_setup(remote, token, resp):
    """Perform additional setup after user have been logged in."""
    user_info = remote.get('userinfo').data
    
    # Set extra data on the account
    with current_app.security.datastore.commit_nested():
        user = token.remote_account.user
        if user_info.get('email'):
            user.email = user_info.get('email')
        if user_info.get('name'):
            user.user_profile.full_name = user_info.get('name')
        if user_info.get('preferred_username'):
            user.username = user_info.get('preferred_username')
        
        current_app.security.datastore.commit()

def dex_disconnect_handler(remote, *args, **kwargs):
    """Handle unlinking of remote account."""
    if not current_app.config['DEX_ALLOW_REMOVE_EXTERNAL_ACCOUNT']:
        raise OAuthRejectedRequestError('External account cannot be unlinked.')
    
    # Perform default disconnect
    from invenio_oauthclient.handlers import disconnect_handler
    return disconnect_handler(remote, *args, **kwargs)
