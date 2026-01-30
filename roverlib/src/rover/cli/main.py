import click
from rover.cli.new import new
from rover.cli.run import run
from rover.cli.hello import hello
from rover.cli.camera import camera
from rover.cli.movement import movement

@click.group()
def cli():
    """CLI para criação e execução de projetos Rover."""
    pass

cli.add_command(new)
cli.add_command(run)
cli.add_command(hello)
cli.add_command(camera)
cli.add_command(movement)