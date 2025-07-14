# in your invenio.cfg or module
from invenio_oauthclient.contrib.settings import OAuthSettingsHelper

class DexOAuthSettingsHelper(OAuthSettingsHelper):
    def __init__(self):
        super().__init__(
            title="UPR Dex",
            description="Login via UPR Dex Identity Provider",
            base_url="https://idp.upr.edu.cu/",
            app_key="DEX_APP_CREDENTIALS",
            access_token_url="https://idp.upr.edu.cu/token",
            authorize_url="https://idp.upr.edu.cu/auth",
            userinfo_url="https://idp.upr.edu.cu/userinfo"
        )

    def get_handlers(self):
        return dict(
            authorized_handler='invenio_oauthclient.handlers:authorized_signup_handler',
            disconnect_handler='invenio_oauthclient.handlers:default_disconnect_handler',
            signup_handler=dict(
                info='invenio_oauthclient.handlers:info_signup_handler',
                setup='invenio_oauthclient.handlers:setup_signup_handler',
                view='invenio_oauthclient.handlers:signup_handler',
            ),
        )

    def get_rest_handlers(self):
        return dict(
            authorized_handler='invenio_oauthclient.handlers.rest:authorized_signup_handler',
            disconnect_handler='invenio_oauthclient.handlers.rest:default_disconnect_handler',
            signup_handler=dict(
                info='invenio_oauthclient.handlers.rest:info_signup_handler',
                setup='invenio_oauthclient.handlers.rest:setup_signup_handler',
                view='invenio_oauthclient.handlers.rest:signup_handler',
            ),
            response_handler='invenio_oauthclient.handlers.rest:default_remote_response_handler',
            authorized_redirect_url='/',
            disconnect_redirect_url='/',
            signup_redirect_url='/',
            error_redirect_url='/',
        )

# Instantiate and register
dex_helper = DexOAuthSettingsHelper()
OAUTHCLIENT_REMOTE_APPS = dict(
    uprdex=dex_helper.remote_app,
)
DEX_APP_CREDENTIALS = dict(
    consumer_key="<your-client-id>",
    consumer_secret="<your-client-secret>",
)
