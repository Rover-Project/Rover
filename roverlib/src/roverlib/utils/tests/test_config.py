"""
Testes do Config (leitura e escrita do config.yaml).

Executar (na pasta roverlib/):  python -m pytest src/roverlib/utils
"""
from roverlib.utils.config_manager import Config


def escrever(tmp_path, texto):
    path = tmp_path / "config.yaml"
    path.write_text(texto, encoding="utf-8")
    return Config(path)


def test_get_com_e_sem_padrao(tmp_path):
    config = escrever(tmp_path, "graph:\n  max_points: 50\n")
    assert config.get("graph") == {"max_points": 50}
    assert config.get("nao_existe") is None
    assert config.get("nao_existe", {"a": 1}) == {"a": 1}   # usado pelos exemplos lidarGraph e continuousFocus


def test_arquivo_vazio(tmp_path):
    config = escrever(tmp_path, "# só comentários\n")
    assert config.load() == {}
    assert config.get("camera", {}) == {}


def test_acentos_em_utf8(tmp_path):
    config = escrever(tmp_path, "# configuração da câmera\nnome: Ação\n")
    assert config.get("nome") == "Ação"


def test_set_config_preserva_o_resto(tmp_path):
    config = escrever(tmp_path, "a: 1\nb: 2\n")
    config.setConfig({"b": 3, "c": "ç"})
    assert config.load() == {"a": 1, "b": 3, "c": "ç"}
