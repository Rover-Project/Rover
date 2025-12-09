"""
Script de exemplo para testar múltiplos modelos de Machine Learning.
Facilita a experimentação com diferentes modelos YOLO e configurações.
"""

import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Imprime um cabeçalho formatado."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def run_detector(model_path, **kwargs):
    """
    Executa o detector com o modelo especificado.
    
    Args:
        model_path: Caminho do modelo ou nome YOLO
        **kwargs: Argumentos adicionais (camera, confidence, etc)
    """
    cmd = [sys.executable, "MLModelConfig.py", "--model", model_path]
    
    # Adicionar argumentos opcionais
    for key, value in kwargs.items():
        if key == "camera":
            cmd.extend(["-c", str(value)])
        elif key == "confidence":
            cmd.extend(["--confidence", str(value)])
        elif key == "width":
            cmd.extend(["--width", str(value)])
        elif key == "height":
            cmd.extend(["--height", str(value)])
        elif key == "frame_skip":
            cmd.extend(["--frame-skip", str(value)])
        elif key == "no_stats":
            if value:
                cmd.append("--no-stats")
    
    print(f"[EXECUTANDO] {' '.join(cmd)}\n")
    subprocess.run(cmd)


def show_menu():
    """Mostra menu de modelos disponíveis."""
    print_header("DETECTOR DE OBJETOS - SELEÇÃO DE MODELO")
    
    print("Modelos YOLOv8 Padrão (Baixa Automático):")
    print("  1. YOLOv8 Nano     (3.2M params)  - Mais rápido")
    print("  2. YOLOv8 Small    (11.2M params)")
    print("  3. YOLOv8 Medium   (25.9M params)")
    print("  4. YOLOv8 Large    (43.7M params)")
    print("  5. YOLOv8 XLarge   (68.2M params) - Mais preciso")
    
    print("\nModelos Customizados:")
    print("  6. Modelo Customizado (local)")
    print("  7. Modelo TFLite")
    
    print("\nOpcões Especiais:")
    print("  8. Comparação rápida (3 modelos)")
    print("  9. Teste Raspberry Pi (otimizado)")
    print("  0. Sair")


def test_comparison():
    """Testa 3 modelos em sequência para comparação."""
    print_header("TESTE COMPARATIVO - 3 MODELOS")
    
    models = [
        ("yolov8n.pt", "YOLOv8 Nano (Rápido)"),
        ("yolov8s.pt", "YOLOv8 Small (Equilibrado)"),
        ("yolov8m.pt", "YOLOv8 Medium (Preciso)")
    ]
    
    for model_path, model_name in models:
        print_header(f"Testando: {model_name}")
        print(f"Modelo: {model_path}")
        print("Pressione 'q' para passar para o próximo modelo\n")
        
        run_detector(
            model_path,
            camera=0,
            confidence=0.65,
            frame_skip=2
        )


def test_raspberry_pi():
    """Teste otimizado para Raspberry Pi."""
    print_header("TESTE OTIMIZADO PARA RASPBERRY PI")
    
    print("Configuração:")
    print("  - Modelo: YOLOv8 Nano (mais rápido)")
    print("  - Frame Skip: 3 (otimiza FPS)")
    print("  - Resolução: 640x480")
    print("  - Confiança: 0.6\n")
    
    run_detector(
        "yolov8n.pt",
        camera=0,
        confidence=0.6,
        frame_skip=3,
        width=640,
        height=480
    )


def custom_model():
    """Permite usar um modelo customizado."""
    print_header("MODELO CUSTOMIZADO")
    
    model_path = input("Digite o caminho do modelo (ex: ./models/best.pt): ").strip()
    
    if not model_path:
        print("[ERRO] Caminho inválido")
        return
    
    confidence = input("Digite a confiança (padrão 0.65): ").strip()
    confidence = float(confidence) if confidence else 0.65
    
    frame_skip = input("Digite o frame skip (padrão 2): ").strip()
    frame_skip = int(frame_skip) if frame_skip else 2
    
    print_header(f"Executando: {model_path}")
    
    run_detector(
        model_path,
        camera=0,
        confidence=confidence,
        frame_skip=frame_skip
    )


def main():
    """Função principal."""
    print("\n" + "█"*70)
    print("█ " + " "*66 + " █")
    print("█ " + "DETECTOR DE OBJETOS COM MACHINE LEARNING - ROVER PROJECT".center(66) + " █")
    print("█ " + " "*66 + " █")
    print("█"*70 + "\n")
    
    while True:
        show_menu()
        choice = input("\nEscolha uma opção (0-9): ").strip()
        
        if choice == "1":
            print_header("YOLOv8 Nano")
            run_detector("yolov8n.pt", confidence=0.65)
        
        elif choice == "2":
            print_header("YOLOv8 Small")
            run_detector("yolov8s.pt", confidence=0.65)
        
        elif choice == "3":
            print_header("YOLOv8 Medium")
            run_detector("yolov8m.pt", confidence=0.65)
        
        elif choice == "4":
            print_header("YOLOv8 Large")
            run_detector("yolov8l.pt", confidence=0.65)
        
        elif choice == "5":
            print_header("YOLOv8 XLarge")
            run_detector("yolov8x.pt", confidence=0.65)
        
        elif choice == "6":
            custom_model()
        
        elif choice == "7":
            print_header("Modelo TFLite")
            model_path = input("Digite o caminho do modelo .tflite: ").strip()
            run_detector(model_path, confidence=0.65)
        
        elif choice == "8":
            test_comparison()
        
        elif choice == "9":
            test_raspberry_pi()
        
        elif choice == "0":
            print("\n[INFO] Encerrando...\n")
            break
        
        else:
            print("\n[ERRO] Opção inválida!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Programa interrompido pelo usuário.")
    except Exception as e:
        print(f"\n[ERRO] Erro fatal: {e}")
        import traceback
        traceback.print_exc()
