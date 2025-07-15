from flask_login import current_user
from invenio_oauthclient.utils import create_registrationform
from invenio_userprofiles.forms import ProfileForm
from wtforms import BooleanField, ValidationError, validators, FormField
from werkzeug.local import LocalProxy
from flask import current_app, url_for
from markupsafe import Markup

from flask import current_app
import re 
from invenio_i18n import lazy_gettext as _


def validate_username(username):
    """Validate the username.

    See :data:`~.username_regex` to know which rules are applied.

    :param username: A username.
    :raises ValueError: If validation fails.
    """
    username_regex = re.compile(current_app.config["ACCOUNTS_USERNAME_REGEX"])
    if not username_regex.match(username):
        raise ValueError(current_app.config['ACCOUNTS_USERNAME_RULES_TEXT'])


class AlmaProfileForm(ProfileForm):
        
    def validate_username(self, field):
        """Wrap username validator for WTForms."""
        try:
            validate_username(field.data)
        except ValueError as e:
            raise ValidationError(e)

        # Check if username is already taken.
        datastore = current_app.extensions["security"].datastore
        user = datastore.find_user(username=field.data)
        if user is None:
            return

        # NOTE: Form validation error.
        msg = _("Username is not available.")

        if current_user.is_anonymous:
            # We are handling a new sign up (i.e. anonymous user) AND a
            # the username already exists. Fail.
            raise ValidationError(msg)
        else:
            # We are handling a user editing their profile AND a
            # the username already exists.
            is_same_user = current_user.get_id() == str(user.id)
            if not is_same_user:
                # Username already taken by another user.
                raise ValidationError(msg)

_security = LocalProxy(lambda: current_app.extensions['security'])


def alma_registration_form(*args, **kwargs):
    class DefaultRegistrationForm(_security.confirm_register_form):
            password = None  # remove the password field
            profile = FormField(AlmaProfileForm, separator=".")
            recaptcha = None  # remove the captcha
            submit = None  # remove submit btn, already defined in the template
            # terms_of_use = BooleanField(terms_of_use_text, [validators.required()])  # add the new field

    return DefaultRegistrationForm(*args, **kwargs)