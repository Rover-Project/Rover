import click # type: ignore
from roverlib.modules.movement.robot import Robot
from roverlib.utils.config_manager import Config
from time import sleep

@click.command()
@click.option("--direction", default='f', type=str)
@click.option("--speed", default=50, show_default=True, type=int)
@click.option("--time", default=2, type=float)
def move(direction: str, speed: int, time: float):
    """
        Move os motores para frente ou para trás.
    Args:
        speed (float): velocidade de rotação dos motores.
    """

    # lendo pinos da gpio
    pins_motors = Config.get("gpio")
    left = (int(pins_motors["motor_esquerdo"]["in3"]), int(pins_motors["motor_esquerdo"]["in4"]))
    right = (int(pins_motors["motor_direito"]["in1"]), int(pins_motors["motor_direito"]["in2"]))

    # instânciando motores
    robot = Robot(
        left,
        right,
    )
    
    # move para frente
    if direction.lower() == 'f':
        robot.forward(speed)
        
    # move para trás
    elif direction.lower() == 'b':
        robot.backward(speed)
    else:
        click.echo("Direção inválida tente:")
        click.echo("rover move --direction=b")
    
    sleep(time) # tempo de rotação
    robot.stop() # para motores
    robot.cleanup() # limpa configuração da gpio