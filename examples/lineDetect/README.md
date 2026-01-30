# Script inicial para detecção de linhas 

## Implementação 

- Tecnica de detecção de linhas: Usar transformada de Hough para detectar as linhas 

- Realizar um pré-processamento básico:
    
    - Conversão para escala de cinza.
    - Filtro de passas baixas para amenizar detalhes internos 
    - Detecção de bordas 

- Uso

```bash
python -m examples.lineDetect.main file
```

file é o arquivo contido na pasta assets que deseja escolher para a detecção.