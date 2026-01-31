import click # type: ignore
from roverlib.modules.movement.robot import Robot
from roverlib.utils.config_manager import Config

@click.group()
def movement():
    """Comandos relacionados à movimentação do Rover"""
    pass

@movement.command()
@click.option("--speed", default=50, show_default=True)
def test(backend, speed):

    # lendo pinos da gpio
    pins_motors = Config.get("gpio")
    left = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
    right = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))

    # instânciado motores
    robot = Robot(
        left,
        right,
    )

    # Testando
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