import flask as fk
from flask import Flask, request, render_template, app
from secrets import token_hex
import model as md
from urllib.parse import quote, unquote
import secrets

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
    return fk.render_template("auth/login.html")

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
        return fk.redirect("/login")
    
@srv.get("/cadastrar") #Tela cadastro
def register_get():
    return fk.render_template("auth/register.html")

@srv.post("/cadastrar") #Processar cadastro
def register_post():
    usuario_nome = request.form.get("nome")
    usuario_email = request.form.get("email")
    usuario_senha = request.form.get("senha")

    md.criar_usuario(usuario_nome, usuario_email, usuario_senha)

    return fk.render_template("auth/login.html")

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
    evento_categoria = request.form["categoria"]

    valor_total = request.form.get("valor_total")
    itens = request.form.get("itens")

    evento_token = secrets.token_urlsafe(22)

    evento_id = md.config_evento(
        administrador_id,
        evento_nome,
        evento_local,
        evento_data,
        evento_horario,
        evento_limite,
        evento_token,
        evento_categoria,
        valor_total,
    )

    # ✔️ coletivo
    if evento_categoria == "3" and itens:
        lista_itens = [i.strip() for i in itens.split(",") if i.strip()]
        md.salvar_itens(evento_id, lista_itens)

    return fk.redirect(f"/evento/{evento_token}")

@srv.post("/editarEvento")
def editar_evento():
    evento_id = request.form["evento_id"]
    evento_nome = request.form["nome"]
    evento_local = request.form["local"]
    evento_data = request.form["data"]
    evento_horario = request.form["hora"]
    evento_limite = request.form["limite"]
    evento_categoria = request.form["categoria"]
    valor_total = request.form.get("valor_total")
    itens = request.form.get("itens")
    md.editar_evento(evento_id, evento_nome, evento_local, evento_data, evento_horario, evento_limite, evento_categoria, valor_total)
    
    if evento_categoria != "3":
        md.deletar_itens_do_evento(evento_id)

    if evento_categoria == "3" and itens:
        lista_itens = [i.strip() for i in itens.split(",") if i.strip()]
        md.atualizar_itens_evento(evento_id, lista_itens)
    
    return fk.redirect(f"/evento/{md.get_token_evento(evento_id)}")

@srv.get("/evento/<evento_token>")
def get_evento(evento_token):
    evento_id = md.get_id_evento(evento_token)
    url = f'http://localhost:5050/evento/{evento_token}'
    print(evento_id)
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
    print(usuarios)
    return fk.render_template("events/event_detail.html", usuarios=usuarios, solicitacoes=solicitacoes, is_admin=is_admin, evento=evento, url=url)

@srv.post("/evento/solicitar")
def solicitar_participacao():
    evento_id = request.form.get("evento_id")
    usuario_id = fk.session["usuario_id"]
    if evento_id and usuario_id:
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