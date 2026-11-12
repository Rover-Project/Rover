# Movimento

`Robot` controla os dois motores do Rover. Pelo `Rover`, ele é acessado como `rover.move`.

Fora da Raspberry Pi (ou com `simulate=True` / `ROVER_SIMULATE=1`), os motores são simulados pelo `VirtualMotor`.

::: roverlib.modules.movement.robot.Robot

::: roverlib.modules.movement.motorCalibration.Calibration

::: roverlib.modules.movement.PID.PID

## Drivers de motor

Usados internamente pelo `Robot`. Só é preciso usá-los diretamente para controlar um motor isolado.

::: roverlib.plugins.motor.motorDriver.MotorDriver

::: roverlib.plugins.motor.vitualMotor.VirtualMotor
