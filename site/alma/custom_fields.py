
from invenio_records_resources.services.custom_fields import TextCF
from invenio_vocabularies.services.custom_fields import VocabularyCF
from marshmallow_utils.fields import SanitizedHTML
from invenio_records_resources.services.records.facets import CFTermsFacet
from invenio_vocabularies.services.facets import VocabularyLabels

from invenio_i18n import lazy_gettext as _


UPR_NAMESPACE = {
    "upr": "https://www.upr.edu.cu/vocabs/",
}

UPR_CUSTOM_FIELDS = [
    VocabularyCF(  # the type of custom field, VocabularyCF is a controlled vocabulary
        name="upr:entidades",  # name of the field, namespaced by `cern`
        vocabulary_id="upr:entidades",  # controlled vocabulary id defined in the vocabularies.yaml file
        dump_options=True,  # True when the list of all possible values will be visible in the dropdown UI component, typically for small vocabularies
        multiple=False, # if the field accepts a list of values (True) or single value (False)
    ),
    VocabularyCF(  # the type of custom field, VocabularyCF is a controlled vocabulary
        name="upr:materias",  # name of the field, namespaced by `cern`
        vocabulary_id="upr:materias",  # controlled vocabulary id defined in the vocabularies.yaml file
        dump_options=True,  # True when the list of all possible values will be visible in the dropdown UI component, typically for small vocabularies
        multiple=True, # if the field accepts a list of values (True) or single value (False)
    ),    
]

UPR_CUSTOM_FIELDS_UI = {
        "section": _("Fields from UPR"),
        "fields": [
            dict(
            field="upr:entidades",
            ui_widget="Dropdown",
            props=dict(
                label=_("Entity"),
                placeholder=_("Entity UPR"),
                icon="university",
                description=_("Entity of UPR to which the registry mainly belongs"),
                search=False,
                multiple=False,
                clearable=True,
            ),
        ),
        dict(
            field="upr:materias",
            ui_widget="Dropdown",
            props=dict(
                label=_("Subjects"),
                placeholder=_("Subjects UPR"),
                icon="university",
                description=_("Subjects defined by UPR"),
                search=True,
                multiple=True,
                clearable=True,
            ),
        ),
    ],
}

UPR_CUSTOM_FACETS = {
    "upr:entidades": {
        "facet": CFTermsFacet(
            field="upr:entidades.id",
            label=_("Entidades UPR"),
            value_labels=VocabularyLabels("upr:entidades"),
        ),
        "ui": {  # ui display
            "field": CFTermsFacet.field("upr:entidades.id"),
        },
    },
    "upr:materias": {
        "facet": CFTermsFacet(
            field="upr:materias.id",
            label=_("Materias UPR"),
            value_labels=VocabularyLabels("upr:materias"),
        ),
        "ui": {  # ui display
            "field": CFTermsFacet.field("upr:materias.id"),
        },
    },    
}