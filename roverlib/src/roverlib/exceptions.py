"""
Exceção base da RoverLib.

Todas as exceções dos plugins herdam de RoverLibError (além da exceção
padrão do Python que já usavam), então é possível tratar qualquer erro
da biblioteca de uma vez:

    from roverlib.exceptions import RoverLibError

    try:
        ...
    except RoverLibError as erro:
        print("Problema no Rover:", erro)
"""


class RoverLibError(Exception):
    """Base de todas as exceções da RoverLib."""


class HardwareNotAvailable(RoverLibError, RuntimeError):
    """O hardware (ou a biblioteca que o acessa) não está disponível neste computador."""
