import yaml


class Config:

    def __init__(self, path):
        """
        Carrega dados do arquivo de configuração.

        Args:
            path (path): Caminho para o arquivo de configuração.
        """
        self.config_path = path

    def load(self) -> dict:
        """Lê o arquivo de configuração. Um arquivo vazio vira um dicionário vazio."""
        with open(self.config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        return config or {}

    def get(self, key: str, default=None):
        """
        Acessa um campo do arquivo de configuração.

        Args:
            key (str): nome do campo (ex.: "camera").
            default: valor retornado se o campo não existir. Padrão: None.
        """
        return self.load().get(key, default)

    def setConfig(self, config_write: dict):
        """
        Adiciona novas configurações no arquivo de configuração.

        Args:
            config_write (dict): nova configuração que deve ser escrita.
        """
        config = dict(self.load())

        # Adiciona as novas configurações
        config.update(config_write)

        # Escreve as novas configurações no arquivo
        with open(self.config_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(config, file, default_flow_style=False, allow_unicode=True)
