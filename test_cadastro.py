from unittest.mock import patch
from service import cadastrar_usuario, criar_evento
import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

@patch('model.criar_usuario')
class TestCadastros:
    def test_cadastrar_usuario_sucesso(self, mock_svc, client):
        mock_svc.criar_usuario.return_value = None

        resp = client.post("/cadastrar")

        assert resp.status_code == 200
        assert resp.data.decode() == "auth/login.html"

        mock_svc.criar_usuario.assert_called_once()
