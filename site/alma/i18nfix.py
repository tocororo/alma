from heapq import merge
from flask import current_app
import traceback
from json import JSONDecodeError, dump, load
from pathlib import Path
import subprocess
import polib
from jinja2 import BaseLoader, Environment
from click import group, option, secho
from importlib_metadata import entry_points
import os 

TRANSIFEX_CONFIG_TEMPLATE = """
[main]
host = https://www.transifex.com

[o:inveniosoftware:p:invenio:r:{{- resource }}]
file_filter = {{- temporary_cache }}/{{- package }}/<lang>/messages.po
source_file = {{- package }}/assets/semantic-ui/translations/{{- package }}/translations.pot
source_lang = en
type = PO
"""

I18N_TRANSIFEX_JS_RESOURCES_MAP = {
    "invenio-administration-messages-ui": "invenio_administration",
    "invenio-app-rdm-messages-ui": "invenio_app_rdm",
    "invenio-communities-messages-ui": "invenio_communities",
    "invenio-rdm-records-messages-ui": "invenio_rdm_records",
    "invenio-requests-messages-ui": "invenio_requests",
    "invenio-search-ui-messages-js": "invenio_search_ui"
}
I18N_JS_DISTR_EXCEPTIONAL_PACKAGE_MAP = {
    "jobs": "invenio_jobs",
    "invenio_previewer_theme": "invenio_previewer",
    "invenio_app_rdm_theme": "invenio_app_rdm",
}




def map_to_i18next_style(pofile):
    """Map translations from po to i18next style.

    Plurals need a special format.
    """
    obj = {}
    for entry in pofile:
        obj[entry.msgid] = entry.msgstr
        if entry.msgstr_plural:
            obj[entry.msgid] = entry.msgstr_plural[0]
            obj[entry.msgid + "_plural"] = entry.msgstr_plural[1]
    return obj


def create_transifex_configuration(temporary_cache, js_resources):
    """Create a transifex fetch configuration.

    This configuration is built dynamically because the targeted packages are
    customizable over the configuration variable I18N_TRANSIFEX_JS_RESOURCES_MAP.
    """
    environment = Environment(loader=BaseLoader())
    config_template = environment.from_string(TRANSIFEX_CONFIG_TEMPLATE)

    with Path(temporary_cache / "collected_config").open("w") as fp:
        for resource, package in js_resources.items():
            config = config_template.render(
                temporary_cache=temporary_cache,
                resource=resource,
                package=package,
            )
            fp.write(config)
            fp.write("\n\n")


def fetch_translations_from_transifex(token, temporary_cache, languages, js_resources):
    """Fetch translations from transifex."""
    temporary_cache.mkdir(parents=True, exist_ok=True)

    create_transifex_configuration(temporary_cache, js_resources)

    transifex_pull_cmd = [
        "tx",
        f"--token={token}",
        f"--config={temporary_cache}/collected_config",
        "pull",
        f"--languages={languages}",
        "--force",
    ]
    subprocess.run(transifex_pull_cmd)


def fetch_from_transifex(token, languages, output_directory):
    """Retrieve package translations from Transifex and unify them to a single file using i18next format.

    Usage
    -----
    .. code-block:: console
       $ invenio i18n fetch-from-transifex -t <your transifex API token> -l 'de,en,fr' -o js_translations/

    The command expects an API token associated with a Transifex account to be able to pull translations.
    Such a token can be generated in the user settings on the Transifex website.

    The output directory will be used to store downloaded translations per package as well as the unified translation file.

    To supply the packages for which translations should be pulled, add the following config to your instance's ``invenio.cfg``:

    .. code-block:: python
        I18N_TRANSIFEX_JS_RESOURCES_MAP = {
            "invenio-administration-messages-ui": "invenio_administration",
            "invenio-app-rdm-messages-ui": "invenio_app_rdm",
            "invenio-communities-messages-ui": "invenio_communities",
            "invenio-rdm-records-messages-ui": "invenio_rdm_records",
            "invenio-requests-messages-ui": "invenio_requests",
            "invenio-search-ui-messages-js": "invenio_search_ui"
        }

    Fetching and unifying of translations
    ---------------------------
    This CLI command pulls translations in PO format from Transifex for all packages specified in the config.
    It will then unify all translations to a single JSON file in a format that can be used with the i18next library.
    The unified file will contain keys for package names on the top level and a nested dict with translation keys and values for each package, e.g.:

    .. code-block:: json
        {
            "invenio_administration": {
                "Error": "Fehler",
                "Save": "Speichern",
                ...
            },
            "invenio_app_rdm": {
                "Basic information": "Allgemeine Informationen",
                "New": "Neu",
                ...
            },
            ...
        }
    """
    js_resources = I18N_TRANSIFEX_JS_RESOURCES_MAP

    temporary_cache = output_directory / "tmp"

    fetch_translations_from_transifex(token, temporary_cache, languages, js_resources)

    collected_translations = {}

    for language in languages.split(","):
        collected_translations[language] = {}

        for package in js_resources.values():
            po_path = f"{temporary_cache}/{package}/{language}/messages.po"
            pofile = polib.pofile(po_path)

            collected_translations[language][package] = map_to_i18next_style(pofile)

        output_file = Path(f"{output_directory}/{language}.json")
        with output_file.open("w", encoding="utf-8") as fp:
            dump(collected_translations[language], fp, indent=4, ensure_ascii=False)

def pofile_open(path):
    try:
        # Try with UTF-8 firs
        po = polib.pofile(path)
    except UnicodeDecodeError:
        # Fall back to latin-1 (ISO-8859-1) which can read any byte
        po = polib.pofile(path, encoding='latin-1')
    finally:
        return po
   
def do_merge(polib_dst, polib_src):
    for entry in polib_src:
        # Only add if not already present (or modify logic as needed)
        if entry.msgid not in [e.msgid for e in polib_dst]:
            polib_dst.append(polib.POEntry(
                msgid=entry.msgid,
                msgstr=entry.msgstr
            ))


def get_merge_invenio_po_files(lang, venv_path):

    pofile = polib.POFile()

    for item in os.listdir(f'{venv_path}'):
        # if item.rfind('invenio') >= 0:
        if item.rfind('invenio') >= 0 and item.rfind('dist-info') < 0:
            
            p = f'{venv_path}{item}'
            if os.path.isdir(p):
                for item2 in os.listdir(p):
                    if item2 == 'translations':
                        p2 = f'{venv_path}{item}/translations'
                        if os.path.exists(f'{p2}/{lang}/LC_MESSAGES/messages.po'):
                            do_merge(polib_dst=pofile, polib_src=pofile_open(f'{p2}/{lang}/LC_MESSAGES/messages.po'))
                        elif os.path.exists(f'{p2}/messages.pot'):
                            do_merge(polib_dst=pofile, polib_src=pofile_open(f'{p2}/messages.pot'))

    return pofile


def merge_all_translations(input_directory: Path, languages, output_directory, pot_file_path, venv_path):
    js_resources = I18N_TRANSIFEX_JS_RESOURCES_MAP
    
    pot_file = polib.POFile(pot_file_path)

    for language in languages.split(","):
        merged = polib.POFile()

        for package in js_resources.values():
            po_path = f"{input_directory}/{package}/{language}/messages.po"
            pofile = polib.pofile(po_path)
            merged.extend(pofile)
        
        do_merge(merged, pofile_open(pot_file_path))
        do_merge(merged, get_merge_invenio_po_files(lang=language, venv_path=venv_path))


        merge_path = Path(f"{output_directory}/{language}/LC_MESSAGES/")
        merge_path.mkdir(parents=True, exist_ok=True)

        translated = [entry for entry in merged if entry.translated()]

        new_pofile = polib.POFile()
        new_pofile.metadata = merged.metadata
        for entry in translated:
            new_pofile.append(entry)
        new_pofile.save(merge_path / "translated.po")

        # TODO: conectar a un llm y traducir.

        untranslated = [entry for entry in merged if not entry.translated()]
        new_pofile = polib.POFile()
        new_pofile.metadata = merged.metadata
        for entry in untranslated:
            new_pofile.append(entry)
        new_pofile.save(merge_path / "untranslated.po")


        print(f't:{len(translated)}  u:{len(untranslated)}')



def source_translation_files(input_directory):
    """Map source translation file contents to their languages."""
    for source_file in input_directory.iterdir():
        if not source_file.is_file() or source_file.suffix != ".json":
            msg = f"source file: {source_file} is not meant to be distributed."
            secho(msg, fg="yellow")
            continue

        language = source_file.stem

        with source_file.open("r") as source_file:
            try:
                obj = load(source_file)
            except JSONDecodeError as error:
                tb = traceback.format_exc()
                msg = f"ERROR: source file: {source_file.name} couldn't be loaded because of error: {str(error)}\n{tb}"
                secho(msg, fg="red")
            else:
                yield language, obj


def calculate_target_packages(
    exceptional_package_names,
    entrypoint_group,
    language,
):
    """Calculate target package translation paths.

    Maps each package to its target translation file path by inspecting entrypoint and handling exceptional package names.
    """
    package_translations_paths = {}

    for entry_point in entry_points(group=entrypoint_group):
        package_name = entry_point.name
        package_path = Path(entry_point.load().path)

        # Some webpack entry points use names that differ from their package names.
        # Map these exceptional webpack entry‑point names to their correct package names.
        package_name = exceptional_package_names.get(package_name, package_name)

        target_translations_path = (
            package_path / "translations" / package_name / "messages" / language
        )

        package_translations_paths[package_name] = (
            target_translations_path / "translations.json"
        )

    return package_translations_paths


INVENIO_RDM_RECORDS_INDEX_JS_FIX= """
import TRANSLATE_EN from "./en/translations.json";
import TRANSLATE_DE from "./de/translations.json";
import TRANSLATE_EL from "./el/translations.json";
import TRANSLATE_SV from "./sv/translations.json";
import TRANSLATE_CS from "./cs/translations.json";
import TRANSLATE_ES from "./es/translations.json";

export const translations = {
  el: { translation: TRANSLATE_EL },
  en: { translation: TRANSLATE_EN },
  de: { translation: TRANSLATE_DE },
  sv: { translation: TRANSLATE_SV },
  cs: { translation: TRANSLATE_CS },
  es: { translation: TRANSLATE_ES },
};

"""

def distribute_js_translations(input_directory: Path, entrypoint_group: str):
    """
    Distribute package‑specific JavaScript translations.

    Usage
    -----
    .. code-block:: console
       $ invenio i18n distribute-js-translations -i js_translations/

    The command expects an input directory that contains one unified JSON file per
    language, named after the locale code—e.g., de.json, tr.json, de_AT.json, etc.

    The ``invenio i18n fetch-from-transifex`` command can be used to retrieve translations from Transifex and unify them.

    The command uses invenio_assets.webpack entrypoint group to determine package asset paths. In order for the command to work properly, add the following config to the ``invenio.cfg``:

    .. code-block:: python
       I18N_JS_DISTR_EXCEPTIONAL_PACKAGE_MAP = {
         "jobs": "invenio_jobs",
         "invenio_previewer_theme": "invenio_previewer",
         "invenio_app_rdm_theme": "invenio_app_rdm",
       }


    Distribution of translation
    ---------------------------
    This CLI command processes unified per‑language JSON files in a given input path.  The command extracts translations that belong to the target package, discovers asset root paths of packages through the ``invenio_assets.webpack``
    entry‑point group and writes it to the package’s  translation folder in react-i18next format here.

    For example, for locale ``tr`` the extracted fragment for
    ``invenio_communities`` is written to:

    ``<site‑packages>/invenio-communities/assets/semantic-ui/translations/invenio_communities/messages/tr/translations.json``

    Missing directories and files will be created automatically if not exist.
    """
    exceptional_package_names = I18N_JS_DISTR_EXCEPTIONAL_PACKAGE_MAP

    # Read unified source translation files and distribute translations to relevant packages
    for language, unified_translations in source_translation_files(input_directory):
        target_packages = calculate_target_packages(
            exceptional_package_names, entrypoint_group, language
        )

        for package_name, translations in unified_translations.items():
            if package_name not in target_packages:
                msg = f"Package {package_name} doesn't have webpack entrypoint. Skipping..."
                secho(msg, fg="yellow")
                continue

            target_file = target_packages[package_name]

            if not target_file.parent.exists():
                msg = f"Translations directory for {package_name} in language {language} not found. Creating..."
                secho(msg, fg="yellow")
                target_file.parent.mkdir(parents=True)

            with target_file.open("w") as file_pointer:
                dump(translations, file_pointer, indent=2, ensure_ascii=False)

            msg = f"{package_name} translations for language {language} have been written."
            secho(msg, fg="green")

            if package_name == 'invenio_rdm_records':

                indexjs = target_file.parent.parent / "index.js"

                cat_cmd = [
                'cat',
                indexjs]
                subprocess.run(cat_cmd)
                secho(f'ohhh...{indexjs}', fg='blue')

                with indexjs.open("w") as file_pointer:
                    file_pointer.write(INVENIO_RDM_RECORDS_INDEX_JS_FIX)

                subprocess.run(cat_cmd)
                secho(f'ohhh...{indexjs}', fg='blue')
