"""Translation and localization commands for the CLI."""

import subprocess
from pathlib import Path

import click

from app import app


@app.cli.group()
def translate():
    """Translation and localization commands."""
    pass


@translate.command()
@click.argument("lang")
def init(lang):
    """Initialize a new language."""
    filename = "messages.pot"
    extract_cmd = [
        "pybabel",
        "extract",
        "-F",
        "babel.cfg",
        "-k",
        "_l",
        "-o",
        filename,
        ".",
    ]
    subprocess.run(extract_cmd, check=True)

    init_cmd = [
        "pybabel",
        "init",
        "-i",
        filename,
        "-d",
        "app/translations",
        "-l",
        lang,
    ]
    subprocess.run(init_cmd, check=True)

    try:
        Path(filename).unlink()
    except FileNotFoundError:
        click.echo(f"File {filename} does not exist.")


@translate.command()
def update():
    """Update all languages."""
    filename = "messages.pot"
    extract_cmd = [
        "pybabel",
        "extract",
        "-F",
        "babel.cfg",
        "-k",
        "_l",
        "-o",
        filename,
        ".",
    ]
    subprocess.run(extract_cmd, check=True)

    update_cmd = ["pybabel", "update", "-i", filename, "-d", "app/translations"]
    subprocess.run(update_cmd, check=True)

    try:
        Path(filename).unlink()
    except FileNotFoundError:
        click.echo(f"File {filename} does not exist.")


@translate.command()
def compile():
    """Compile all languages."""
    compile_cmd = ["pybabel", "compile", "-d", "app/translations"]
    subprocess.run(compile_cmd, check=True)
