"""
Script de setup para instalar dependências do detector de ML.
Fornece diferentes opções de instalação para diferentes plataformas.
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(text):
    """Imprime um cabeçalho formatado."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def run_command(cmd, description=""):
    """Executa um comando e retorna o resultado."""
    if description:
        print(f"[INFO] {description}...")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"[OK] {description} concluído com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao executar: {description}")
        print(f"       Comando: {cmd}")
        print(f"       Erro: {e}")
        return False


def install_basic_requirements():
    """Instala os requisitos básicos."""
    print_header("INSTALANDO REQUISITOS BÁSICOS")
    
    requirements = [
        ("opencv-python", "OpenCV"),
        ("ultralytics", "YOLOv8"),
        ("numpy", "NumPy"),
    ]
    
    for package, name in requirements:
        cmd = f"{sys.executable} -m pip install {package} --upgrade"
        run_command(cmd, f"Instalando {name}")


def install_gpu_requirements():
    """Instala requisitos com suporte a GPU."""
    print_header("INSTALANDO COM SUPORTE A GPU (CUDA)")
    
    print("""
    Para melhor performance com GPU, instale:
    
    Para NVIDIA CUDA:
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    
    Ou execute:
        python setup.py --gpu nvidia
    """)
    
    choice = input("\nDeseja instalar NVIDIA CUDA support? (s/n): ").strip().lower()
    
    if choice == 's':
        cmd = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
        run_command(cmd, "Instalando PyTorch com CUDA")


def install_raspberry_pi():
    """Instalação otimizada para Raspberry Pi."""
    print_header("SETUP PARA RASPBERRY PI")
    
    print("""
    Este setup é otimizado para Raspberry Pi com:
    - Versão reduzida do OpenCV
    - YOLOv8 Nano como padrão
    - Configurações de memória otimizadas
    """)
    
    print("\n[INFO] Instalando dependências do sistema...")
    commands = [
        ("sudo apt-get update", "Atualizando lista de pacotes"),
        ("sudo apt-get install -y python3-pip python3-dev python3-opencv", "Instalando pacotes do sistema"),
        (f"{sys.executable} -m pip install --upgrade pip setuptools wheel", "Atualizando pip"),
        (f"{sys.executable} -m pip install ultralytics numpy", "Instalando ultralytics e numpy"),
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc)
    
    print("""
    
    [OK] Raspberry Pi configurado!
    
    Próximos passos:
    1. Teste com: python MLModelConfig.py --model yolov8n.pt
    2. Para melhor FPS, use: --frame-skip 3 --width 320 --height 240
    """)


def install_jetson_nano():
    """Instalação otimizada para Jetson Nano."""
    print_header("SETUP PARA JETSON NANO")
    
    print("""
    Este setup é otimizado para Jetson Nano com:
    - TensorRT para aceleração
    - JetPack framework
    """)
    
    print("\n[INFO] Instalando dependências específicas do Jetson...")
    
    commands = [
        ("sudo apt-get update", "Atualizando pacotes"),
        ("sudo apt-get install -y python3-pip python3-dev", "Instalando Python dev"),
        (f"{sys.executable} -m pip install --upgrade pip", "Atualizando pip"),
        (f"{sys.executable} -m pip install ultralytics opencv-python numpy", "Instalando pacotes Python"),
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc)
    
    print("""
    
    [OK] Jetson Nano configurado!
    
    Para usar TensorRT (acelerado):
    1. Exportar modelo: yolo export model=yolov8s.pt format=engine
    2. Usar: python MLModelConfig.py --model best.engine
    """)


def install_docker():
    """Cria um Dockerfile para containerização."""
    print_header("GERANDO DOCKERFILE")
    
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \\
    libsm6 libxext6 libxrender-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos
COPY requirements.txt .
COPY MLModelConfig.py .
COPY test_models.py .
COPY config/ ./config/

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando padrão
ENTRYPOINT ["python", "MLModelConfig.py"]
CMD ["--model", "yolov8n.pt"]
"""
    
    requirements_content = """opencv-python==4.8.1.78
ultralytics==8.0.207
numpy==1.24.3
"""
    
    dockerfile_path = Path("Dockerfile")
    requirements_path = Path("requirements.txt")
    
    dockerfile_path.write_text(dockerfile_content)
    requirements_path.write_text(requirements_content)
    
    print(f"[OK] Dockerfile criado: {dockerfile_path}")
    print(f"[OK] requirements.txt criado: {requirements_path}")
    
    print("""
    
    Para usar Docker:
    1. Build: docker build -t rover-ml-detector .
    2. Run:   docker run --device /dev/video0 rover-ml-detector --model yolov8n.pt
    """)


def verify_installation():
    """Verifica se tudo está instalado corretamente."""
    print_header("VERIFICANDO INSTALAÇÃO")
    
    packages_to_check = [
        ("cv2", "OpenCV"),
        ("ultralytics", "YOLOv8"),
        ("numpy", "NumPy"),
    ]
    
    all_ok = True
    
    for module_name, display_name in packages_to_check:
        try:
            __import__(module_name)
            print(f"[OK] {display_name} instalado corretamente")
        except ImportError:
            print(f"[ERRO] {display_name} não encontrado!")
            all_ok = False
    
    if all_ok:
        print("\n[OK] Todas as dependências estão instaladas!")
        print("\nVocê pode iniciar com:")
        print("  python MLModelConfig.py --model yolov8n.pt")
        print("  python test_models.py")
    else:
        print("\n[ERRO] Algumas dependências faltam. Execute 'python setup.py' novamente.")
    
    return all_ok


def show_menu():
    """Mostra menu de instalação."""
    print("\n" + "█"*70)
    print("█ " + " "*66 + " █")
    print("█ " + "ML OBJECT DETECTOR - SETUP".center(66) + " █")
    print("█ " + " "*66 + " █")
    print("█"*70)
    
    print("""
    1. Instalação Básica (Recomendado para começar)
    2. Instalação com GPU (NVIDIA CUDA)
    3. Setup Raspberry Pi
    4. Setup Jetson Nano
    5. Gerar Dockerfile (para containerização)
    6. Verificar Instalação
    0. Sair
    """)


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Setup para ML Object Detector"
    )
    
    parser.add_argument(
        "--basic", action="store_true",
        help="Instalação básica"
    )
    parser.add_argument(
        "--gpu", type=str, choices=["nvidia"],
        help="Instalar com suporte a GPU"
    )
    parser.add_argument(
        "--raspberry-pi", action="store_true",
        help="Setup para Raspberry Pi"
    )
    parser.add_argument(
        "--jetson-nano", action="store_true",
        help="Setup para Jetson Nano"
    )
    parser.add_argument(
        "--docker", action="store_true",
        help="Gerar Dockerfile"
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Verificar instalação"
    )
    
    args = parser.parse_args()
    
    # Se argumentos foram passados
    if args.basic:
        install_basic_requirements()
        verify_installation()
        return
    
    if args.gpu:
        install_basic_requirements()
        install_gpu_requirements()
        verify_installation()
        return
    
    if args.raspberry_pi:
        install_raspberry_pi()
        verify_installation()
        return
    
    if args.jetson_nano:
        install_jetson_nano()
        verify_installation()
        return
    
    if args.docker:
        install_docker()
        return
    
    if args.verify:
        verify_installation()
        return
    
    # Menu interativo se nenhum argumento
    while True:
        show_menu()
        choice = input("Escolha uma opção (0-6): ").strip()
        
        if choice == "1":
            install_basic_requirements()
            verify_installation()
        
        elif choice == "2":
            install_basic_requirements()
            install_gpu_requirements()
            verify_installation()
        
        elif choice == "3":
            install_raspberry_pi()
        
        elif choice == "4":
            install_jetson_nano()
        
        elif choice == "5":
            install_docker()
        
        elif choice == "6":
            verify_installation()
        
        elif choice == "0":
            print("\n[INFO] Encerrando setup...")
            break
        
        else:
            print("\n[ERRO] Opção inválida!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Setup interrompido pelo usuário.")
    except Exception as e:
        print(f"\n[ERRO] Erro fatal: {e}")
        import traceback
        traceback.print_exc()
