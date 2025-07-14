# invenio.cfg

from invenio_oauthclient.contrib.settings import OAuthSettingsHelper
from invenio_oauthclient.handlers.rest import default_remote_response_handler
from invenio_oauthclient.handlers import authorized_signup_handler, disconnect_handler
from invenio_records_rest.utils import deny_all

#
# Handler functions to map Dex user info to Invenio user
#
def upr_account_info(remote, resp):
    """
    Retrieves information from the Dex userinfo endpoint.

    The user's information is fetched from the `userinfo_endpoint`
    (https://idp.upr.edu.cu/userinfo) provided in your Dex config.
    """
    # Make a request to the userinfo endpoint to get user details
    user_info = remote.get('userinfo').json()

    # Map Dex claims to the Invenio user data model
    # 'sub' (subject) is a unique, stable identifier for the user.
    # 'preferred_username' is used for the Invenio username.
    # 'name' is used for the Invenio full name.
    return {
        'user': {
            'email': user_info.get('email'),
            'profile': {
                'username': user_info.get('preferred_username'),
                'full_name': user_info.get('name'),
            },
        },
        'external_id': user_info.get('sub'),
        'external_method': remote.name,
    }

def upr_account_setup(user, token, resp):
    """
    Performs any extra setup after the user is created.
    
    For this basic setup, no extra actions are needed.
    """
    pass

#
# OAuth Settings Helper for Dex
#
class UprDexOAuthSettingsHelper(OAuthSettingsHelper):
    def __init__(self):
        super().__init__(
            title="UPR IDP",
            description="Login with your University of Pinar del Río account.",
            # This key points to the credentials dictionary below
            app_key="UPR_APP_CREDENTIALS",
            # The following URLs are taken directly from your dex config
            access_token_url="https://idp.upr.edu.cu/token",
            authorize_url="https://idp.upr.edu.cu/auth",
            # Define the scopes needed to get user profile information
            request_token_params={'scope': 'openid email profile groups'}
        )

    def get_handlers(self):
        """Return handlers for the UI login flow."""
        return {
            'authorized_handler': authorized_signup_handler,
            'disconnect_handler': disconnect_handler,
            'signup_handler': {
                'info': upr_account_info,
                'setup': upr_account_setup,
                'view': 'invenio_oauthclient.handlers:signup_handler',
            },
        }

    def get_rest_handlers(self):
        """Return handlers for the REST API login flow."""
        return {
            'authorized_handler': 'invenio_oauthclient.handlers.rest:authorized_signup_handler',
            'disconnect_handler': deny_all, # REST API does not support disconnect
            'signup_handler': {
                'info': upr_account_info,
                'setup': upr_account_setup,
                'view': 'invenio_oauthclient.handlers.rest:signup_handler',
            },
            'response_handler': 'invenio_oauthclient.handlers.rest:default_remote_response_handler',
            'authorized_redirect_url': '/',
            'disconnect_redirect_url': '/',
            'signup_redirect_url': '/',
            'error_redirect_url': '/',
        }

#
# Final Configuration
#
upr_dex_helper = UprDexOAuthSettingsHelper()

OAUTHCLIENT_REMOTE_APPS = {
    'upr-dex': upr_dex_helper.remote_app,
}

# ⚠️ ACTION REQUIRED: Replace these values with the actual credentials
# provided by your Dex administrator.
UPR_APP_CREDENTIALS = {
    'consumer_key': 'CHANGE_ME_TO_YOUR_CLIENT_ID',
    'consumer_secret': 'CHANGE_ME_TO_YOUR_CLIENT_SECRET',
}

# Optional: Set a friendly display name for the login button
OAUTHCLIENT_REMOTE_APPS['upr-dex']['title'] = 'Universidad de Pinar del Río'