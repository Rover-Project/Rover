import click # type: ignore
from roverlib.core.movement_loader import load_motor
from roverlib.modules.movement.robot import Robot

@click.group()
def movement():
    """Comandos relacionados à movimentação do Rover"""
    pass

@movement.command()
@click.option("--backend", default="mock", show_default=True)
@click.option("--speed", default=50, show_default=True)
def test(backend, speed):

    MotorClass = load_motor(backend)

    if backend == "mock":
        left_motor = MotorClass("left")
        right_motor = MotorClass("right")
        

    robot = Robot(
        left_motor,
        right_motor,
    )

    print("\n")
    click.echo("Frente")
    robot.forward(speed, duration=2)
    print("\n")
    click.echo("Girando esquerda")
    robot.turn_left(speed, duration=2)
    print("\n")
    click.echo("Girando direita")
    robot.turn_right(speed, duration=2)
    print("\n")
    click.echo("Parando")
    robot.stop()
    robot.cleanup()
    print("\n")
    click.echo("Teste de movimentação finalizado")



