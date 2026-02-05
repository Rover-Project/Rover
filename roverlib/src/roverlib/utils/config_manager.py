import yaml
from pathlib import Path

class Config:
    
    def __init__(self, path):
        """
        Carrega dados do arquivo de configuração.

        Args:
            path (path): Caminho para o arquivo de configuração.
        """
        self.config_path = path

    def load(self):
        """Ler o arquivo de configuração"""
        with open(self.config_path, "r") as file:
            config = yaml.safe_load(file)
            
        return config

    def get(self, key: str):
        """Acessa um campo do arquivo de configuração"""
        config = self.load()
        return config.get(key)
 
    def setConfig(self, config_write: dict):
        """
        Adicona novas configuracoes no arquivo de config
        Args:
            config_write (dict): nova configuração que deve ser escrita.
        """
        
        config = dict(self.load())
        
        #print(config)
        
        # Adiciona as novas configurações
        for key, value in config_write.items():
            
            print(key, value)
            config[key] = value
        
        # Escreve as novas configurações no arquivo
        with open(self.config_path, "w") as file:
            yaml.safe_dump(config, file, default_flow_style=False)