
from invenio_records_resources.services.custom_fields import TextCF
from invenio_vocabularies.services.custom_fields import VocabularyCF
from marshmallow_utils.fields import SanitizedHTML
from invenio_records_resources.services.records.facets import CFTermsFacet
from invenio_vocabularies.services.facets import VocabularyLabels

from invenio_i18n import lazy_gettext as _


UPR_NAMESPACE = {
    "upr": "https://codemeta.github.io/terms/#",
}

UPR_CUSTOM_FIELDS = [
    VocabularyCF(  # the type of custom field, VocabularyCF is a controlled vocabulary
        name="upr:facultades",  # name of the field, namespaced by `cern`
        vocabulary_id="upr:facultades",  # controlled vocabulary id defined in the vocabularies.yaml file
        dump_options=True,  # True when the list of all possible values will be visible in the dropdown UI component, typically for small vocabularies
        multiple=False, # if the field accepts a list of values (True) or single value (False)
    ),
]

UPR_CUSTOM_FIELDS_UI = {
        "section": _("Fields from UPR"),
        "fields": [
            dict(
            field="upr:facultades",
            ui_widget="Dropdown",
            props=dict(
                label=_("Faculty"),
                placeholder=_("Faculty"),
                icon="university",
                description=_("Faculty to which the registry mainly belongs"),
                search=False,
                multiple=False,
                clearable=True,
            ),
        ),
    ],
}

UPR_CUSTOM_FACETS = {
    "facultades": {
        "facet": CFTermsFacet(
            field="upr:facultades.id",
            label=_("Faculty"),
            value_labels=VocabularyLabels("upr:facultades"),
        ),
        "ui": {  # ui display
            "field": CFTermsFacet.field("upr:facultades.id"),
        },
    },
}