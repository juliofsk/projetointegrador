import flask as fk
import model as md
import secrets
import service
from datetime import date
from secrets import token_hex
from urllib.parse import quote, unquote
from flask import Flask, request, render_template, app

srv = fk.Flask(__name__)
srv.secret_key = token_hex()

UPLOAD_FOLDER = 'static/uploads/usuarios'
srv.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@srv.get("/") #Tela inicial
def get_home():
    eventos = []
    try:
        session_id = fk.session["usuario_id"]
        eventos = md.filtrar_eventos_proximos(session_id)
        print(eventos)     
    except KeyError:
        pass

    return fk.render_template("home.html", eventos=eventos)

@srv.get("/login") #Tela login
def login_get():
    erro = request.args.get("erro")
    mensagem_erro = None
    if erro == "1":
        mensagem_erro = "Usuário ou senha inválidos. Tente novamente."
    return fk.render_template("auth/login.html", error=mensagem_erro)

@srv.post("/login") #Processar login
def login_post():
    usuario_nome = request.form.get("nome")
    usuario_senha = request.form.get("senha")
    usuario = md.autenticar_usuario(usuario_nome, usuario_senha)
    # usuario é (id, nome) ou None
    if usuario:
        fk.session["usuario_id"] = usuario[0]
        fk.session["usuario_nome"] = usuario[1]
        fk.session["usuario_email"] = usuario[2]
        return fk.redirect("/")
    else:
        return fk.redirect("/login?erro=1")
    
@srv.get("/cadastrar") #Tela cadastro
def register_get():
    return fk.render_template("auth/register.html")

@srv.post("/cadastrar") #Processar cadastro
def register_post():
    usuario_nome = request.form.get("nome")
    usuario_email = request.form.get("email")
    usuario_senha = request.form.get("senha")

    service.cadastrar_usuario(usuario_nome, usuario_email, usuario_senha)

    return fk.redirect("auth/login.html")

@srv.get("/logout")
def get_logout():
    del fk.session["usuario_nome"]
    return fk.redirect("/")

@srv.get("/perfil")
def get_perfil():
    usuario_id = fk.session["usuario_id"]
    usuario_nome = fk.session["usuario_nome"]
    usuario_email = fk.session["usuario_email"]
    usuario_foto = md.get_foto(usuario_id)
    print(fk.session)
    try:
        usuario_nome = fk.session["usuario_nome"]
        return fk.render_template("user/profile.html", usuario_id=usuario_id, usuario_nome=usuario_nome, usuario_email=usuario_email, usuario_foto=usuario_foto)
    except KeyError:
        return fk.redirect("login")
    
@srv.get("/edit_perfil")
def get_edit_perfil():
    usuario_id = fk.session["usuario_id"]
    usuario_nome = fk.session["usuario_nome"]
    usuario_email = fk.session["usuario_email"]
    usuario_foto = md.get_foto(usuario_id)
    print(fk.session)
    return fk.render_template("user/edit_profile.html", usuario_id=usuario_id, usuario_nome=usuario_nome, usuario_email=usuario_email, usuario_foto=usuario_foto)

@srv.post("/editarperfil")
def editar_perfil():
    usuario_id = fk.session["usuario_id"]
    usuario_nome = request.form["nome"]
    usuario_email = request.form["email"]
    foto = request.files.get("foto")
    print(fk.session)
     # Verifica se uma nova foto foi enviada
    if foto and foto.filename != "":
        # Define o caminho para salvar a foto
        foto_path = f"{UPLOAD_FOLDER}/{usuario_id}.png"
        foto.save(foto_path)  # Salva a foto no servidor
        foto_rel_path = f"uploads/usuarios/{usuario_id}.png" 
    else:
        # Mantém a foto atual se nenhuma nova foto for enviada
        foto_rel_path = md.get_foto(usuario_id)

    md.editar_perfil(usuario_id, usuario_nome, usuario_email, foto.filename)
    fk.session["usuario_nome"] = usuario_nome
    return fk.render_template("user/profile.html", arq_foto=foto_rel_path)

@srv.get("/criarEvento")
def get_criar_evento():
    return fk.render_template("events/create_event.html")

@srv.post("/criarEvento")
def post_evento():
    administrador_id = fk.session.get("usuario_id")
    if not administrador_id:
        return fk.redirect("/login")

    evento_nome = request.form["nome"]
    evento_local = request.form["local"]
    evento_data = request.form["data"]
    evento_horario = request.form["hora"]
    evento_limite = request.form["limite"]

    evento_token = secrets.token_urlsafe(22)

    service.criar_evento(administrador_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite, evento_token)

    evento_id = md.get_id_evento(evento_token)

    return fk.redirect(f"/evento/{evento_token}")

@srv.get("/listarEventos")
def listar_eventos():
    proximos_eventos = []
    anteriores_eventos = []
    data = date.today().isoformat()
    try:
        id_usuario = fk.session["usuario_id"]
        proximos_eventos = md.filtrar_proximos_eventos(id_usuario, data)
        anteriores_eventos = md.filtrar_anteriores_eventos(id_usuario, data)    
    except KeyError:
        pass

    return fk.render_template("events/all_events.html", proximos_eventos=proximos_eventos, anteriores_eventos=anteriores_eventos)

@srv.get("/sobre")
def get_sobre():

    return fk.render_template("partials/_about.html")

@srv.post("/editarEvento")
def editar_evento():
    evento_id = request.form["evento_id"]
    evento_nome = request.form["nome"]
    evento_local = request.form["local"]
    evento_data = request.form["data"]
    evento_horario = request.form["hora"]
    evento_limite = request.form["limite"]
    md.editar_evento(evento_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite)
    
    return fk.redirect(f"/evento/{md.get_token_evento(evento_id)}")

@srv.get("/evento/<evento_token>")
def get_evento(evento_token):
    evento_id = md.get_id_evento(evento_token)
    url = f'http://localhost:5050/evento/{evento_token}'
    print(evento_id)

    passou = md.evento_ja_passou(evento_id)

    num_participantes = md.get_num_participantes(evento_id)

    if not evento_id:
        return "Evento não encontrado", 404
    evento = md.get_evento(evento_id)
    if not evento:
        return "Evento não encontrado", 404
    
    usuarios = md.usuarios_lista(evento_id)
    solicitacoes = []
    # se a função existir, carrega solicitacoes (status=1)
    try:
        solicitacoes = md.usuarios_solicitacoes(evento_id)
    except AttributeError:
        solicitacoes = []
    # verifica se o usuário atual é administrador do evento
    usuario_id = fk.session["usuario_id"]
    is_admin = False
    if usuario_id:
        try:
            is_admin = md.is_evento_admin(evento_id, usuario_id)
        except AttributeError:
            is_admin = False
    print(solicitacoes)
    return fk.render_template("events/event_detail.html", usuarios=usuarios, solicitacoes=solicitacoes, is_admin=is_admin, evento=evento, url=url, num_participantes=num_participantes, passou=passou)

@srv.post("/evento/solicitar")
def solicitar_participacao():
    evento_id = request.form.get("evento_id")
    usuario_id = fk.session["usuario_id"]
    if evento_id and usuario_id:
        if md.get_status(evento_id, usuario_id) != 2:
            md.solicitar_participacao(evento_id, usuario_id)
    return fk.redirect(fk.request.referrer or "/")

@srv.post("/lista/aceitar")
def aceitar_solicitacao():
    evento_id = request.form.get("evento_id")
    usuario_id = request.form.get("usuario_id")
    if evento_id and usuario_id:
        md.aceitar_solicitacao(evento_id, usuario_id)
    return fk.redirect(fk.request.referrer or "/")

@srv.post("/lista/recusar")
def recusar_solicitacao():
    evento_id = request.form.get("evento_id")
    usuario_id = request.form.get("usuario_id")
    if evento_id and usuario_id:
        md.recusar_solicitacao(evento_id, usuario_id)
    return fk.redirect(fk.request.referrer or "/")

@srv.post("/evento/deletar")
def deletar_evento():
    evento_id = request.form.get("evento_id")
    if evento_id:
        md.deletar_evento(evento_id,)
    return fk.redirect("/")


if __name__ == "__main__":
    srv.run(host="localhost",port=5050, debug=True)