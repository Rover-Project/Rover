# Shell Script para a configuração do ambiente rover 
# Instalação de depedências de sistema, python e roverlib

#!/usr/bin/env bash

set -e  # para o script se algo falhar

echo -e "\033[32mIniciando setup do ambiente Rover\033[0m"

# Verifica se o sistema operacional é a base de ubunto
if ! grep -qi ubuntu /etc/os-release; then
  echo -e "\033[31mEste script suporta apenas Ubuntu\033[0m"
  exit 1
fi

# Dependencias de sistema
echo -e "\033[32mInstalando dependências do sistema\033[0m"

sudo apt update
sudo apt install -y \
  software-properties-common \
  build-essential \
  curl \
  git \
  python3-venv \
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
  liblzma-dev

# Instala python 3.11
# Torna personalizavel essa versão do python 
if ! command -v python3.11 &>/dev/null; then
  echo -e "\033[32mInstalando Python 3.11 via pyenv\033[0m"

  if [ ! -d "$HOME/.pyenv" ]; then
    curl https://pyenv.run | bash
  fi

  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init -)"

  pyenv install -s 3.11.8
  pyenv global 3.11.8
else
  echo -e "\033[33mPython 3.11 já instalado\033[0m"
fi

# Criando ambiente virtual
VENV_DIR=".venv" # constante padrão para o nome 

if [ ! -d "$VENV_DIR" ]; then
  echo -e "\033[32mCriando ambiente virtual\033[0m"
  python3.11 -m venv $VENV_DIR
else
  echo -e "\033[33mAmbiente virtual já existe.\033[0m"
fi

# Ativa ambiente virtual
echo -e "\033[32mAtivando ambiente virtual\033[0m"
source $VENV_DIR/bin/activate

# Atualiza ferramentas de instalação e empacotamento
echo -e "\033[32mAtualizando ferramentas Python\033[0m"
pip install --upgrade pip setuptools wheel build

# Instalando roverlib
if [ -f "pyproject.toml" ]; then
  echo -e "\033[32mInstalando roverlib\033[0m"
  pip install -e .
else
  echo -e "\033[31mpyproject.toml não encontrado em roverlib/\033[0m"
  exit 1
fi

# Valida instalação da roverlib
echo -e "\033[32mValidando instalação\033[0m"
rover --help >/dev/null

echo ""
echo -e "\033[32mAmbiente Rover configurado com sucesso!\033[0m"
echo ""
echo "Para começar:"
echo "   source .venv/bin/activate"
echo "   rover --help"