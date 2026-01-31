import click

@click.command()
def hello():
    """Verifica se a lib foi instalada corretamente."""
    click.echo("RoverLib foi instalada corretamente.")


