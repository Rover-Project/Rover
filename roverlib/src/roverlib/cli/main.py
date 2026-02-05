import click # type: ignore
from .new import new
from .run import run
from .hello import hello

@click.group()
def cli():
    """CLI para criação e execução de projetos Rover."""
    pass

cli.add_command(new)
cli.add_command(run)
cli.add_command(hello)
