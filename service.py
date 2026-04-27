import secrets

import model as md
from werkzeug.security import generate_password_hash
from PIL import Image, ImageDraw, ImageFont
import os

def gerar_avatar_padrao(usuario_id, inicial):
    # Cria uma imagem 100x100 com fundo azul e letra branca
    img = Image.new('RGB', (100, 100), color=(255, 71, 107))
    draw = ImageDraw.Draw(img)
    # Tentar usar uma fonte, se não, default
    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except:
        font = ImageFont.load_default()
    # Centralizar a letra
    bbox = draw.textbbox((0, 0), inicial, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = 50
    y = 50
    draw.text((x, y), inicial, fill=(255, 255, 255), font=font, anchor="mm")
    # Salvar
    os.makedirs('static/uploads/usuarios', exist_ok=True)
    img.save(f'static/uploads/usuarios/{usuario_id}.png')
    return f'{usuario_id}.png'

def cadastrar_usuario(nome, email, senha):
    """
    Valida e cadastra um novo usuário.
    Lança ValueError com mensagem amigável se algum campo for inválido.
    """
    if not nome or not email or not senha:
        raise ValueError("Todos os campos do usuário devem ser preenchidos.")
    if len(nome) > 20:
        raise ValueError("O nome do usuário deve ter no máximo 20 caracteres.")
    if len(email) > 30:
        raise ValueError("O email do usuário deve ter no máximo 30 caracteres.")
    if len(senha) > 20:
        raise ValueError("A senha do usuário deve ter no máximo 20 caracteres.")
    if "@" not in email or "." not in email:
        raise ValueError("O email do usuário deve ser válido.")
    senha_hash = generate_password_hash(senha)
    usuario_id = md.criar_usuario(nome, email, senha_hash)
    # Gerar avatar padrão
    inicial = nome[0].upper()
    nome_foto = gerar_avatar_padrao(usuario_id, inicial)
    # Atualizar no banco
    md.editar_perfil(usuario_id, nome, email, nome_foto)


def autenticar_usuario(nome, senha):
    """
    Autentica o usuário pelo nome e senha.
    Retorna (id, nome, email) se válido, ou None.
    """
    return md.autenticar_usuario(nome, senha)
 
 
def get_foto(usuario_id):
    """Retorna o caminho da foto do usuário ou None."""
    return md.get_foto(usuario_id)
 
 
def editar_perfil(usuario_id, nome, email, foto_arquivo, upload_folder):
    """
    Atualiza os dados do perfil do usuário.
    Recebe o objeto de arquivo enviado pelo form e o caminho da pasta de uploads.
    Retorna o caminho relativo da foto para exibição.
    """
    if foto_arquivo and foto_arquivo.filename != "":
        foto_arquivo.save(f"{upload_folder}/{usuario_id}.png")
        nome_foto = foto_arquivo.filename
    else:
        nome_foto = md.get_foto(usuario_id)
 
    md.editar_perfil(usuario_id, nome, email, nome_foto)
    foto_rel_path = f"uploads/usuarios/{usuario_id}.png" if nome_foto else None
    return foto_rel_path
 
 
# === EVENTO ===
 
def criar_evento(administrador_id, nome, local, data, hora, limite):
    """
    Valida os dados, gera o token e cria o evento.
    Retorna o token do evento criado.
    Lança ValueError com mensagem amigável se algum campo for inválido.
    """
    if not nome or not local or not data or not hora or not limite:
        raise ValueError("Todos os campos do evento devem ser preenchidos.")
    if len(nome) > 20:
        raise ValueError("O nome do evento deve ter no máximo 20 caracteres.")
    if len(local) > 30:
        raise ValueError("O local do evento deve ter no máximo 30 caracteres.")
    token = secrets.token_urlsafe(22)
    md.criar_evento(administrador_id, nome, local, data, hora, limite, token)
    return token
 
 
def editar_evento(evento_id, usuario_id, nome, local, data, hora, limite):
    """
    Valida permissão e atualiza os dados do evento.
    Lança PermissionError se o usuário não for o administrador.
    Retorna o token do evento para redirecionamento.
    """
    if not md.is_admin_evento(evento_id, usuario_id):
        raise PermissionError("Apenas o administrador pode editar o evento.")
    md.editar_evento(evento_id, nome, local, data, hora, limite)
    return md.get_token_evento(evento_id)
 
 
def deletar_evento(evento_id, usuario_id):
    """
    Valida permissão e deleta o evento.
    Lança PermissionError se o usuário não for o administrador.
    """
    if not md.is_admin_evento(evento_id, usuario_id):
        raise PermissionError("Apenas o administrador pode deletar o evento.")
    md.deletar_evento(evento_id)
 
 
def get_evento(evento_token):
    """
    Busca e retorna todos os dados necessários para a página de detalhe do evento.
    Retorna None se o evento não for encontrado.
    """
    evento_id = md.get_id_evento(evento_token)
    if not evento_id:
        return None
    evento = md.get_evento(evento_id)
    if not evento:
        return None
    return {
        "id": evento_id,
        "dados": evento,
        "participantes": md.get_participantes(evento_id),
        "solicitacoes": md.get_solicitacoes(evento_id),
        "num_participantes": md.get_num_participantes(evento_id),
        "passou": md.evento_ja_passou(evento_id),
    }
 
 
def get_meus_eventos(usuario_id):
    """
    Retorna dicionário com listas de eventos próximos e anteriores do usuário.
    """
    from datetime import date
    data_hoje = date.today().isoformat()
    return {
        "proximos": md.get_eventos_usuario(usuario_id, data_hoje, futuros=True),
        "anteriores": md.get_eventos_usuario(usuario_id, data_hoje, futuros=False),
    }
 
 
def get_home_eventos(usuario_id):
    """Retorna até 3 eventos próximos para exibir na home."""
    if not usuario_id:
        return []
    return md.get_tres_proximos_eventos(usuario_id)
 
 
# === LISTA ===
 
def solicitar_participacao(evento_id, usuario_id):
    """
    Cria uma solicitação de participação se o usuário ainda não estiver confirmado.
    """
    if md.get_status_usuario(evento_id, usuario_id) != 2:
        md.solicitar_participacao(evento_id, usuario_id)
 
 
def aceitar_solicitacao(evento_id, usuario_id):
    """Aprova a solicitação de participação de um usuário."""
    md.aceitar_solicitacao(evento_id, usuario_id)
 
 
def recusar_solicitacao(evento_id, usuario_id):
    """Recusa e remove a solicitação de participação de um usuário."""
    md.recusar_solicitacao(evento_id, usuario_id)