import yaml


class Config:

    """
    Lê e grava o `config.yaml` (ou qualquer arquivo YAML).

    O arquivo é relido a cada chamada, então mudanças feitas nele durante o programa são vistas.
    Também serve para guardar parâmetros do seu próprio programa, como velocidades ou ganhos de um PID.

    Exemplo:

    ```python
    from roverlib import Config

    config = Config("config.yaml")
    camera = config.get("camera", {})          # dicionário da seção, ou {} se não existir
    pid = config.get("pid", {"kp": 0.4})       # valor padrão para seções do seu programa
    config.setConfig({"pid": {"kp": 0.5}})     # grava (substitui a seção inteira)
    ```
    """
    def __init__(self, path):
        """
        Args:
            path (str | Path): caminho do arquivo YAML. O arquivo só é aberto ao ler ou gravar.
        """
        self.config_path = path

    def load(self) -> dict:
        """
        Lê o arquivo inteiro.

        Returns:
            dict: o conteúdo do arquivo; um arquivo vazio vira `{}`.

        Raises:
            FileNotFoundError: o arquivo não existe.
        """
        with open(self.config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        return config or {}

    def get(self, key: str, default=None):
        """
        Lê uma seção (chave de primeiro nível) do arquivo.

        Args:
            key (str): nome da seção, por exemplo `"camera"`.
            default: valor devolvido se a seção não existir. Padrão None.

        Returns:
            O valor da seção (normalmente um dicionário), ou `default`.
        """
        return self.load().get(key, default)

    def setConfig(self, config_write: dict):
        """
        Grava seções no arquivo, mantendo as demais.

        Cada chave do dicionário substitui a seção inteira de mesmo nome. Os comentários do
        arquivo não são preservados na gravação.

        Args:
            config_write (dict): seções a gravar, por exemplo `{"pid": {"kp": 0.5}}`.
        """
        config = dict(self.load())

        # Adiciona as novas configurações
        config.update(config_write)

        # Escreve as novas configurações no arquivo
        with open(self.config_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(config, file, default_flow_style=False, allow_unicode=True)
