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

def cadastrar_usuario(usuario_nome, usuario_email, usuario_senha):
    #validar usuário
    if not usuario_nome or not usuario_email or not usuario_senha:
        raise ValueError("Todos os campos do usuário devem ser preenchidos.")
    if len(usuario_nome) > 20:
        raise ValueError("O nome do usuário deve ter no máximo 20 caracteres.")
    if len(usuario_email) > 30:
        raise ValueError("O email do usuário deve ter no máximo 30 caracteres.")
    if len(usuario_senha) > 20:
        raise ValueError("A senha do usuário deve ter no máximo 20 caracteres.")
    if "@" not in usuario_email or "." not in usuario_email:
        raise ValueError("O email do usuário deve ser válido.")
    senha_hash = generate_password_hash(usuario_senha)
    usuario_id = md.criar_usuario(usuario_nome, usuario_email, senha_hash)
    # Gerar avatar padrão
    inicial = usuario_nome[0].upper()
    nome_foto = gerar_avatar_padrao(usuario_id, inicial)
    # Atualizar no banco
    md.editar_perfil(usuario_id, usuario_nome, usuario_email, nome_foto)


def criar_evento(administrador_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite, evento_token):
    #validar evento
    if not evento_nome or not evento_local or not evento_data or not evento_horario or not evento_limite:
        raise ValueError("Todos os campos do evento devem ser preenchidos.")
    if len(evento_nome) > 20:
        raise ValueError("O nome do evento deve ter no máximo 20 caracteres.")
    if len(evento_local) > 30:
        raise ValueError("O local do evento deve ter no máximo 30 caracteres.")
    md.config_evento(
        administrador_id,
        evento_nome,
        evento_local,
        evento_data,
        evento_horario,
        evento_limite,
        evento_token,
    )    
