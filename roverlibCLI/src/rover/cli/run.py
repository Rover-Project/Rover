import click
from rover.core.runner import run_project

@click.command()
@click.argument("path", default=".")
def run(path):
    """Executa um projeto Rover."""
    run_project(path)
