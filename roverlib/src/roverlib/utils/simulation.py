"""
Controle compartilhado do modo simulação (motores e servos).
"""
import os

# Variável de ambiente para forçar a simulação (ex.: testar na Raspberry sem mover nada)
SIMULATE_ENV = "ROVER_SIMULATE"


def env_simulate() -> bool:
    """True se a variável ROVER_SIMULATE pedir simulação (1, true, yes, sim)."""
    return os.environ.get(SIMULATE_ENV, "").strip().lower() in ("1", "true", "yes", "sim")


def resolve_simulate(simulate, hardware_available: bool, component: str, how_to_require: str,
                     simulated_name: str = None) -> bool:
    """
    Decide se um componente deve ser simulado.

    Args:
        simulate: None (automático), True (sempre simula) ou False (exige o hardware).
        hardware_available: se o driver real pode ser usado neste computador.
        component: nome do componente, usado no aviso (ex.: "motores").
        how_to_require: como exigir o hardware, usado no aviso (ex.: "Robot(..., simulate=False)").
        simulated_name: como chamar a versão simulada no aviso. Padrão: "<component> simulados".

    Returns:
        True se o componente deve ser simulado.
    """
    if simulate is not None:
        return bool(simulate)
    if env_simulate():
        return True
    if not hardware_available:
        simulated_name = simulated_name or f"{component} simulados"
        print(f"AVISO: hardware de {component} não disponível. Usando {simulated_name}. "
              f"Use {how_to_require} para exigir o hardware.")
        return True
    return False
