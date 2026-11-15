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
    """
    Base de todas as exceções da RoverLib.

    Cada exceção da biblioteca também herda da exceção padrão do Python correspondente
    (`RuntimeError`, `ValueError`...), então códigos antigos que tratam essas exceções
    continuam funcionando.

    Exemplo:

    ```python
    from roverlib import Rover
    from roverlib.exceptions import RoverLibError

    try:
        with Rover.from_config("config.yaml") as rover:
            rover.camera.get_frame()
    except RoverLibError as erro:
        print("Problema no Rover:", erro)
    ```
    """


class HardwareNotAvailable(RoverLibError, RuntimeError):
    """
    O hardware, ou a biblioteca que o acessa, não está disponível neste computador.

    Acontece, por exemplo, ao exigir o hardware (`simulate=False`) rodando no PC.
    Cada plugin tem a sua versão: `PinNotAvailable`, `MotorCreationError`,
    `CameraNotAvailable`, `LidarNotAvailable` e `PCANotAvailable`.
    """
