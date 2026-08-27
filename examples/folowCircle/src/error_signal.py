def normalize(error: float, radius: float) -> float:
  """Normaliza o erro entorno do raio"""
  return (error / radius)

def smooth_signal(current_error: float, last_error: float, alph: float) -> float:
  """Suavização via filtro de passas baixas"""
  return (alph * current_error) + ((1.0 - alph) * last_error)

def activation_function(raw_speed: float, min_deadzone: float) -> float:
  """Aplica o limiar mínimo de acionamento (40 e 30) remapeando a escala 0-100."""
  return raw_speed if abs(raw_speed) > min_deadzone else 0

def activation_deadzone(error: float, deadzone: float):
  return error if abs(error) > deadzone else 0