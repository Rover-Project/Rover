#!/usr/bin/env bash

set -e  # para o script se algo falhar

echo "🚀 Iniciando setup do ambiente Rover"

# ===============================
# 1. Verificação do sistema
# ===============================
if ! grep -qi ubuntu /etc/os-release; then
  echo "❌ Este script suporta apenas Ubuntu"
  exit 1
fi

# ===============================
# 2. Dependências do sistema
# ===============================
echo "📦 Instalando dependências do sistema"

sudo apt update
sudo apt install -y \
  software-properties-common \
  build-essential \
  curl \
  git \
  python3-venv \
  python3-pip

# ===============================
# 3. Python 3.11
# ===============================
if ! python3.11 --version &>/dev/null; then
  echo "🐍 Instalando Python 3.11"
  sudo add-apt-repository ppa:deadsnakes/ppa -y
  sudo apt update
  sudo apt install -y python3.11 python3.11-venv python3.11-dev
else
  echo "✅ Python 3.11 já instalado"
fi

# ===============================
# 4. Ambiente virtual
# ===============================
VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "🧪 Criando ambiente virtual"
  python3.11 -m venv $VENV_DIR
else
  echo "✅ Ambiente virtual já existe"
fi

# ===============================
# 5. Ativação
# ===============================
echo "⚡ Ativando ambiente virtual"
source $VENV_DIR/bin/activate

# ===============================
# 6. Ferramentas Python
# ===============================
echo "🔧 Atualizando ferramentas Python"
pip install --upgrade pip setuptools wheel build

# ===============================
# 7. Instalação do roverlib
# ===============================
if [ -f "roverlib/pyproject.toml" ]; then
  echo "📦 Instalando roverlib"
  pip install -e roverlib
else
  echo "❌ pyproject.toml não encontrado em roverlib/"
  exit 1
fi

# ===============================
# 8. Validação
# ===============================
echo "🧪 Validando instalação"
rover --help >/dev/null

echo ""
echo "✅ Ambiente Rover configurado com sucesso!"
echo ""
echo "➡️ Para começar:"
echo "   source .venv/bin/activate"
echo "   rover --help"
