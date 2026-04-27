import flask as fk
import service
from functools import wraps
from secrets import token_hex
from flask import request

srv = fk.Flask(__name__)
srv.secret_key = token_hex()

UPLOAD_FOLDER = 'static/uploads/usuarios'
srv.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# === AUTENTICAÇÃO ===

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario_id" not in fk.session:
            return fk.redirect("/login")
        return f(*args, **kwargs)
    return decorated


@srv.get("/")
def get_home():
    usuario_id = fk.session.get("usuario_id")
    eventos = service.get_home_eventos(usuario_id)
    return fk.render_template("home.html", eventos=eventos)


@srv.get("/login")
def get_login():
    erro = request.args.get("erro")
    mensagem_erro = "Usuário ou senha inválidos. Tente novamente." if erro == "1" else None
    return fk.render_template("auth/login.html", error=mensagem_erro)


@srv.post("/login")
def post_login():
    usuario = service.autenticar_usuario(
        request.form.get("nome"),
        request.form.get("senha")
    )
    if usuario:
        fk.session["usuario_id"] = usuario[0]
        fk.session["usuario_nome"] = usuario[1]
        fk.session["usuario_email"] = usuario[2]
        return fk.redirect("/")
    return fk.redirect("/login?erro=1")


@srv.get("/cadastrar")
def get_cadastrar():
    return fk.render_template("auth/register.html")


@srv.post("/cadastrar")
def post_cadastrar():
    try:
        service.cadastrar_usuario(
            request.form.get("nome"),
            request.form.get("email"),
            request.form.get("senha")
        )
    except ValueError as e:
        return fk.render_template("auth/register.html", error=str(e))
    return fk.redirect("/login")


@srv.get("/logout")
def get_logout():
    fk.session.clear()
    return fk.redirect("/")


# === PERFIL ===

@srv.get("/perfil")
@login_required
def get_perfil():
    usuario_id = fk.session["usuario_id"]
    return fk.render_template("user/profile.html",
                               usuario_id=usuario_id,
                               usuario_nome=fk.session["usuario_nome"],
                               usuario_email=fk.session["usuario_email"],
                               usuario_foto=service.get_foto(usuario_id))


@srv.get("/editar-perfil")
@login_required
def get_editar_perfil():
    usuario_id = fk.session["usuario_id"]
    return fk.render_template("user/edit_profile.html",
                               usuario_id=usuario_id,
                               usuario_nome=fk.session["usuario_nome"],
                               usuario_email=fk.session["usuario_email"],
                               usuario_foto=service.get_foto(usuario_id))


@srv.post("/editar-perfil")
@login_required
def post_editar_perfil():
    usuario_id = fk.session["usuario_id"]
    usuario_nome = request.form["nome"]
    usuario_email = request.form["email"]
    foto_path = service.editar_perfil(
        usuario_id,
        usuario_nome,
        usuario_email,
        request.files.get("foto"),
        UPLOAD_FOLDER
    )
    fk.session["usuario_nome"] = usuario_nome
    return fk.render_template("user/profile.html",
                               usuario_id=usuario_id,
                               usuario_nome=usuario_nome,
                               usuario_email=usuario_email,
                               usuario_foto=foto_path)


# === EVENTOS ===

@srv.get("/criar-evento")
@login_required
def get_criar_evento():
    return fk.render_template("events/create_event.html")


@srv.post("/criar-evento")
@login_required
def post_criar_evento():
    try:
        token = service.criar_evento(
            fk.session["usuario_id"],
            request.form["nome"],
            request.form["local"],
            request.form["data"],
            request.form["hora"],
            request.form["limite"]
        )
    except ValueError as e:
        return fk.render_template("events/create_event.html", error=str(e))
    return fk.redirect(f"/evento/{token}")


@srv.get("/meus-eventos")
@login_required
def get_meus_eventos():
    eventos = service.get_meus_eventos(fk.session["usuario_id"])
    return fk.render_template("events/all_events.html",
                               proximos_eventos=eventos["proximos"],
                               anteriores_eventos=eventos["anteriores"])


@srv.get("/sobre")
def get_sobre():
    return fk.render_template("about.html")


@srv.get("/evento/<evento_token>")
def get_evento(evento_token):
    evento = service.get_evento(evento_token)
    if not evento:
        return "Evento não encontrado", 404

    usuario_id = fk.session.get("usuario_id")
    is_admin = False
    if usuario_id:
        import model as md
        is_admin = md.is_admin_evento(evento["id"], usuario_id)

    url = f'http://localhost:5050/evento/{evento_token}'
    return fk.render_template("events/event_detail.html",
                               evento=evento["dados"],
                               usuarios=evento["participantes"],
                               solicitacoes=evento["solicitacoes"],
                               num_participantes=evento["num_participantes"],
                               passou=evento["passou"],
                               is_admin=is_admin,
                               url=url)


@srv.post("/editar-evento")
@login_required
def post_editar_evento():
    try:
        token = service.editar_evento(
            request.form["evento_id"],
            fk.session["usuario_id"],
            request.form["nome"],
            request.form["local"],
            request.form["data"],
            request.form["hora"],
            request.form["limite"]
        )
    except PermissionError as e:
        return str(e), 403
    return fk.redirect(f"/evento/{token}")


@srv.post("/evento/deletar")
@login_required
def post_deletar_evento():
    evento_id = request.form.get("evento_id")
    if not evento_id:
        return fk.redirect("/")
    try:
        service.deletar_evento(evento_id, fk.session["usuario_id"])
    except PermissionError as e:
        return str(e), 403
    return fk.redirect("/")


# === LISTA / SOLICITAÇÕES ===

@srv.post("/evento/solicitar")
@login_required
def post_solicitar_participacao():
    service.solicitar_participacao(
        request.form.get("evento_id"),
        fk.session["usuario_id"]
    )
    return fk.redirect(fk.request.referrer or "/")


@srv.post("/lista/aceitar")
@login_required
def post_aceitar_solicitacao():
    service.aceitar_solicitacao(
        request.form.get("evento_id"),
        request.form.get("usuario_id")
    )
    return fk.redirect(fk.request.referrer or "/")


@srv.post("/lista/recusar")
@login_required
def post_recusar_solicitacao():
    service.recusar_solicitacao(
        request.form.get("evento_id"),
        request.form.get("usuario_id")
    )
    return fk.redirect(fk.request.referrer or "/")


if __name__ == "__main__":
    srv.run(host="localhost", port=5050, debug=True)