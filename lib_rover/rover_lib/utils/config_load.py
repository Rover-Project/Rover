import yaml
from pathlib import Path

class Config:
    _config = None

    @classmethod
    def load(cls):
        """Ler o arquivo de configuração"""
        if cls._config is None:
            config_path = Path(__file__).parent.parent / "configs" / "config.yaml"
            with open(config_path, "r") as file:
                cls._config = yaml.safe_load(file)
        return cls._config

    @classmethod
    def get(cls, key: str):
        """Acessa um campo do arquivo de configuração"""
        config = cls.load()
        return config.get(key)
