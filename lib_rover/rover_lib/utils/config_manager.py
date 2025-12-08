import yaml
from pathlib import Path

class Config:
    _config_path = Path(__file__).parent.parent / "configs" / "config.yaml"

    @classmethod
    def load(cls):
        """Ler o arquivo de configuração"""
        with open(cls._config_path, "r") as file:
            config = yaml.safe_load(file)
        return config

    @classmethod
    def get(cls, key: str):
        """Acessa um campo do arquivo de configuração"""
        config = cls.load()
        return config.get(key)

    @classmethod 
    def setConfig(cls, config_write: dict):
        """
        Adicona novas configuracoes no arquivo de config
        Args:
            config_write (dict): nova configuração que deve ser escrita.
        """
        
        config = dict(cls.load())
        
        #print(config)
        
        # Adiciona as novas configurações
        for key, value in config_write.items():
            
            print(key, value)
            config[key] = value
        
        # Escreve as novas configurações no arquivo
        with open(cls._config_path, "w") as file:
            yaml.safe_dump(config, file, default_flow_style=False)