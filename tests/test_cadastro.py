from unittest.mock import patch

import pytest
import service

from app import srv as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@patch("service.cadastrar_usuario")
class TestCadastro:
    def test_cadastro_usuario(self, mock_svc, client):
        mock_svc.cadastrar_usuario.return_value = {}

        resp = client.post("/cadastrar")

        assert resp.status_code == 200

@patch("model.criar_usuario")
class TestCadastroModel:
    def test_cadastro_usuario(self, mock_svc):
        mock_svc.criar_usuario.return_value = {}
        assert service.cadastrar_usuario("cachorro", "cachorro@email.com", "12345678") == None

@patch("model.criar_usuario")
class TestCadastroModelErro:
    def test_cadastro_usuario_erro_campos(self, mock_svc):
        with pytest.raises(ValueError, match="Todos os campos do usuário devem ser preenchidos."):
            service.cadastrar_usuario("dhuwhauhud", "", "123456768")

    def test_cadastro_usuario_erro_nome(self, mock_svc):
        with pytest.raises(ValueError, match="O nome do usuário deve ter no máximo 20 caracteres."):
            service.cadastrar_usuario("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "aaaaa@email.com", "12345678")
        
    def test_cadastro_usuario_erro_email(self, mock_svc):
        with pytest.raises(ValueError, match="O email do usuário deve ter no máximo 30 caracteres."):
            service.cadastrar_usuario("cachorro", "cachorrocachorrocachorrocachorrocachorrocachorrocachorrocachorrocachorrocachorro@email.com", "12345678")
        
    def test_cadastro_usuario_erro_senha(self, mock_svc):
        with pytest.raises(ValueError, match="A senha do usuário deve ter no máximo 20 caracteres."):
             service.cadastrar_usuario("cachorro", "cachorro@email.com", "1234567891011121314151617181920")
        
    def test_cadastro_usuario_erro_email_invalido(self, mock_svc):
        with pytest.raises(ValueError, match="O email do usuário deve ser válido."):
            service.cadastrar_usuario("cachorro", "cachorroemailcom", "12345678")

@patch("model.config_evento")
class TestCadastroEventoModel:
    def test_cadastro_evento(self, mock_svc):
        mock_svc.config_evento.return_value = {}
        assert service.criar_evento(1, "evento teste", "local teste", "2024-01-01", "20:00", 100, "token123") == None

@patch("model.config_evento")
class TestCadastroEventoModelErro:
    def test_cadastro_evento_erro_(self, mock_svc):
        with pytest.raises(ValueError, match="Todos os campos do evento devem ser preenchidos."):
            service.criar_evento(1, "", "local", "2024-01-01", "20:00", 100, "token123")

    def test_cadastro_evento_erro_nome(self, mock_svc):
        with pytest.raises(ValueError, match="O nome do evento deve ter no máximo 20 caracteres."):
            service.criar_evento(1, "eventoeventoeventoeventoeventoeventoeventoeventoeventoeventoeventoeventoeventoevento", "local", "2024-01-01", "20:00", 100, "token123")

    def test_cadastro_evento_erro_local(self, mock_svc):
        with pytest.raises(ValueError, match="O local do evento deve ter no máximo 30 caracteres."):
            service.criar_evento(1, "evento", "locallocallocallocallocallocallocallocallocallocallocallocal", "2024-01-01", "20:00", 100, "token123")