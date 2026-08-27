def normalize(error: float, radius: float) -> float:
  """Normaliza o erro entorno do raio"""
  return (error / radius)

def smooth_signal(current_error: float, last_error: float, alph: float) -> float:
  """Suavização via filtro de passas baixas"""
  return (alph * current_error) + ((1.0 - alph) * last_error)

def activation_function(raw_speed: float, min_deadzone: float) -> float:
  """Aplica o limiar mínimo de acionamento (40 e 30) remapeando a escala 0-100."""
 
  sign = 1.0 if raw_speed > 0 else -1.0 # verifica o sinal do pulso

  # Mapeia linearmente a saída do PID para iniciar acima do valor de atrito mínimo
  scaled = min_deadzone + (abs_speed / 100.0) * (100.0 - min_deadzone)
  return sign * scaled

def activation_deadzone(error: float, deadzone: float):
  return error if abs(error) > deadzone else 0