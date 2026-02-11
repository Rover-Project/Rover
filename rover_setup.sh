#!/usr/bin/env bash
# Setup do ambiente Rover
# Raspberry Pi OS (Debian Trixie)

set -e

# Cores
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RC="\033[0m"

echo -e "${GREEN}Iniciando setup do ambiente Rover${RC}"

# Verificação do Sistema
if ! grep -qi "debian" /etc/os-release; then
  echo -e "${RED}Erro:${RC} Este script suporta apenas Debian / Raspberry Pi OS."
  exit 1
fi

# Função para verificar pacote APT
is_installed() {
  dpkg -s "$1" &> /dev/null
}

install_if_missing() {
  if is_installed "$1"; then
    echo -e "${YELLOW}$1 já está instalado.${RC}"
  else
    echo -e "${GREEN}Instalando $1...${RC}"
    sudo apt install -y "$1"
  fi
}

echo -e "${GREEN}Verificando dependências do sistema...${RC}"

sudo apt update

APT_PACKAGES=(
  git
  build-essential
  curl
  python3-pip
  python3-venv
  libssl-dev
  zlib1g-dev
  libbz2-dev
  libreadline-dev
  libsqlite3-dev
  libncursesw5-dev
  xz-utils
  tk-dev
  libffi-dev
  liblzma-dev
  rpicam-apps
  libcamera-dev
)

for pkg in "${APT_PACKAGES[@]}"; do
  install_if_missing "$pkg"
done

# Verifica pyenv
if [ ! -d "$HOME/.pyenv" ]; then
  echo -e "${GREEN}Instalando pyenv.${RC}"
  curl https://pyenv.run | bash
else
  echo -e "${YELLOW}pyenv já instalado.${RC}"
fi

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Verifica Python 3.11
if pyenv versions --bare | grep -q "3.11.8"; then
  echo -e "${YELLOW}Python 3.11.8 já instalado.${RC}"
else
  echo -e "${GREEN}Instalando Python 3.11.8...${RC}"
  pyenv install 3.11.8
fi

pyenv global 3.11.8
pyenv rehash

# Configuração do Projeto
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

VENV_DIR="$PROJECT_ROOT/.venv"
ROVERLIB_DIR="$PROJECT_ROOT/roverlib"

if [ ! -d "$VENV_DIR" ]; then
  echo -e "${GREEN}Criando ambiente virtual...${RC}"
  python -m venv "$VENV_DIR --system-site-packages venv"
else
  echo -e "${YELLOW}Ambiente virtual já existe.${RC}"
fi

source "$VENV_DIR/bin/activate"

echo -e "${GREEN}Verificando ferramentas Python...${RC}"
pip install --upgrade pip setuptools wheel build

# Verifica roverlib
if [ -f "$ROVERLIB_DIR/pyproject.toml" ]; then
  echo -e "${GREEN}Instalando roverlib (modo dev)...${RC}"
  pip install -e "$ROVERLIB_DIR"
else
  echo -e "${RED}Erro:${RC} pyproject.toml não encontrado em roverlib/"
  exit 1
fi

if command -v rover &> /dev/null; then
  echo -e "${GREEN}Ambiente Rover configurado com sucesso!${RC}"
else
  echo -e "${RED}Erro:${RC} comando rover não encontrado."
  exit 1
fi

echo ""
echo "Para usar:"
echo "  source .venv/bin/activate"
echo "  rover --help"
