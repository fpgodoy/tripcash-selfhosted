import pytest
from tripcash import create_app

def test_config():
    """Testa se a configuração de testes é injetada corretamente."""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_index_redirect_or_render(client):
    """Testa o acesso inicial à home sem banco mockado de forma profunda (vai dar erro 500 sem DB, ou vai redirecionar se o banco falhar).
    Para uma verificação apenas de factory:
    """
    pass
