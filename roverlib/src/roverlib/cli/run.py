import click # type: ignore
from roverlib.core.runner import run_project

@click.command()
@click.argument("path", default=".")
def run(path):
    """Executa um projeto Rover."""
    try:
        code = run_project(path)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    raise SystemExit(code)
