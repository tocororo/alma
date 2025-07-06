
import click
from flask.cli import with_appcontext
from pathlib import Path

from alma.i18nfix import fetch_from_transifex, distribute_js_translations, merge_all_translations

@click.group()
def alma():
    """alma custom commands."""


@alma.command("init")
@with_appcontext
def init_alma():
    """alma initialization command"""
    click.secho(message="import users", fg="green")
    click.secho(message="import communities", fg="red")
    click.secho(message="import vocabularies")
    click.secho(message="edit and run again...", fg="blue")


@alma.group()
def data():
    """alma data manipulation commands"""


@data.command("projects")
@with_appcontext
def load_projects():
    """load projects metadata from excel file"""
    click.secho("heloooooo", fg="green")


@alma.command()
@with_appcontext
@click.option("--token", "-t", required=True, help="API token for your Transifex account.")
@click.option(
    "--languages",
    "-l",
    required=True,
    help="Languages you want to download translations for (one or multiple comma separated values, e.g. 'de,en,fr').",
)
@click.option(
    "--output-directory",
    "-o",
    required=True,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, path_type=Path
    ),
    help="Directory to which collected translations in JSON format should be written.",
)
def i18n_fetch_from_transifex(token, languages, output_directory):
    fetch_from_transifex(token, languages, output_directory)


@alma.command()
@with_appcontext
@click.option(
    "-i",
    "--input-directory",
    required=True,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=False, path_type=Path
    ),
    help="Input directory containing translations in JSON format.",
)
@click.option(
    "--languages",
    "-l",
    required=True,
    help="Languages you want to merge (one or multiple comma separated values, e.g. 'de,en,fr').",
)
@click.option(
    "--output-directory",
    "-o",
    required=True,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, path_type=Path
    ),
    help="Directory to output the merged files.",
)
@click.option(
    "--pot-file",
    "-p",
    required=True,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, writable=True, path_type=Path
    ),
    help="Directory to output the merged files.",
)
@click.option(
    "--venv-path",
    "-v",
    required=True,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True, path_type=Path
    ),
    help="",
)
def i18n_merge_all_translations(input_directory: Path, languages, output_directory, pot_file, venv_path):
    merge_all_translations(input_directory, languages, output_directory,pot_file,venv_path)

@alma.command()
@with_appcontext
@click.option(
    "-i",
    "--input-directory",
    required=True,
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=False, path_type=Path
    ),
    help="Input directory containing translations in JSON format.",
)
@click.option(
    "--entrypoint-group",
    default="invenio_assets.webpack",
    help="Entrypoint group used to get package assets paths. Default: \"invenio_assets.webpack\" You don't need to set this option under normal circumstances.'",
)
def i18n_distribute_js_translations(input_directory: Path, entrypoint_group: str):
    distribute_js_translations(input_directory, entrypoint_group)