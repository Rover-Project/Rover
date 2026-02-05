#!/usr/bin/env bash
# Shell Script para a configuração do ambiente rover
# Instala dependências do sistema 
# Instala e configura o pyenv para gerenciar versões do python
# Instala python 3.11 como global 

set -e # Interrompe o script em qualquer erro

# Cores para feadback do shell
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RC="\033[0m" # reseta cor

echo -e "${GREEN}Iniciando setup do ambiente Rover${RC}"

# Verifica se o script foi rodado como root 
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Erro${RC}: execute este script como root (sudo)."
    exit 1
fi

# Verifica se o sistema operacional é Ubuntu
if ! grep -qi ubuntu /etc/os-release; then
  echo -e "${RED}Erro${RC}: Este script suporta apenas Ubuntu."
  exit 1
fi

# Dependências de sistema
echo -e "${GREEN}Instalando dependências do sistema${RC}"

sudo apt update 
sudo apt-get install git-all
sudo apt install -y \
  software-properties-common \
  build-essential \
  curl \
  python3-pip \
  libssl-dev \
  zlib1g-dev \
  libbz2-dev \
  libreadline-dev \
  libsqlite3-dev \
  libncursesw5-dev \
  xz-utils \
  tk-dev \
  libffi-dev \
  liblzma-dev \ 
  libcamera-apps \ 
  libcamera-dev 

# Instala Python 3.11
if ! command -v python3.11 &>/dev/null; then
  echo -e "${GREEN}Instalando Python 3.11 via pyenv${RC}"

  if [ ! -d "$HOME/.pyenv" ]; then
    curl https://pyenv.run | bash
  fi

  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init -)"

  pyenv install -s 3.11.8
  pyenv global 3.11.8
else
  echo -e "${YELLOW}Python 3.11 já instalado${RC}"
fi

echo -e "${GREEN}Iniciando instalação e configuração da roverlib${RC}"

# Diretório raiz do projeto 
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

VENV_DIR="$PROJECT_ROOT/.venv"
ROVERLIB_DIR="$PROJECT_ROOT/roverlib"

# Criando ambiente virtual
if [ ! -d "$VENV_DIR" ]; then
  echo -e "${GREEN}Criando ambiente virtual em $VENV_DIR${RC}"
  python3.11 -m venv "$VENV_DIR"
else
  echo -e "${YELLOW}Ambiente virtual já existe.${RC}"
fi

# Ativando ambiente virtual
echo "Ativando ambiente virtual"
source "$VENV_DIR/bin/activate"

# Atualizando ferramentas
echo "Atualizando ferramentas Python"
pip install --upgrade pip setuptools wheel build

# Instalando roverlib
if [ -f "$ROVERLIB_DIR/pyproject.toml" ]; then
  echo -e "${GREEN}Instalando roverlib${RC}"
  pip install -e "$ROVERLIB_DIR"
else
  echo -e "${RED}pyproject.toml não encontrado em roverlib/${RC}"
  exit 1
fi

# Validando instalação
echo "Validando instalação"
rover --help >/dev/null

echo ""
echo -e "${GREEN}Ambiente Rover configurado com sucesso!${RC}"
echo ""
echo "Para começar:"
echo "   source .venv/bin/activate"
echo "   rover --help"