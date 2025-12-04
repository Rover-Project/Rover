from pathlib import Path
import json

def saveConfig(dados, fileName):
    save = "config" / Path(fileName)

    with open(save, "w", encoding="UTF-8") as file:
        json.dump(dados, file, indent=4, ensure_ascii=False)