import model as md

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
    md.criar_usuario(usuario_nome, usuario_email, usuario_senha)


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
