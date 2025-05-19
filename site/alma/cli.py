
import click
from flask.cli import with_appcontext


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
