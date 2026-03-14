import flask as fk
from flask import Flask, request, render_template, app
from secrets import token_hex
import model as md
from urllib.parse import quote, unquote

srv = fk.Flask(__name__)
srv.secret_key = token_hex()

UPLOAD_FOLDER = 'static/uploads/usuarios'
srv.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@srv.get("/") #Tela inicial
def get_home():
    return fk.render_template("home.html")

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

@srv.get("/perfil")
def get_perfil():
    usuario_id = fk.session["usuario_id"]
    usuario_nome = fk.session["usuario_nome"]
    usuario_email = md.get_email_usuario(usuario_id)
    usuario_foto = md.get_foto_usuario(usuario_id)
    print(fk.session)
    try:
        usuario_nome = fk.session["usuario_nome"]
        return fk.render_template("perfil.html", usuario_id=usuario_id, usuario_nome=usuario_nome, usuario_email=usuario_email, usuario_foto=usuario_foto)
    except KeyError:
        return fk.redirect("login")
    
@srv.get("/edit_perfil")
def get_edit_perfil():
    usuario_id = fk.session["usuario_id"]
    usuario_nome = fk.session["usuario_nome"]
    usuario_email = md.get_email_usuario(usuario_id)
    usuario_senha = fk.session["usuario_senha"]
    usuario_foto = md.get_foto_usuario(usuario_id)
    print(fk.session)
    return fk.render_template("edit_perfil.html", usuario_id=usuario_id, usuario_nome=usuario_nome, usuario_email=usuario_email, usuario_senha=usuario_senha, usuario_foto=usuario_foto)

@srv.post("/editarperfil")
def editar_perfil():
    usuario_id = fk.session["usuario_id"]
    usuario_nome = request.form["nome"]
    usuario_email = request.form["email"]
    usuario_senha = request.form["senha"]
    if usuario_senha:
    #não passo senha na sessão, corrigir    
     fk.session["usuario_senha"] = usuario_senha
    foto = request.files.get("foto")
    print(fk.session)
     # Verifica se uma nova foto foi enviada
    if foto and foto.filename != "":
        # Define o caminho para salvar a foto
        foto_path = f"{UPLOAD_FOLDER}/{usuario_id}_{foto.filename}"
        foto.save(foto_path)  # Salva a foto no servidor
        foto_rel_path = f"uploads/usuarios/{usuario_id}"  # Caminho relativo para o banco
    else:
        # Mantém a foto atual se nenhuma nova foto for enviada
        foto_rel_path = md.get_foto_usuario(usuario_id)

    md.editar_perfil(usuario_id, usuario_nome, usuario_email, usuario_senha, foto.filename)
    fk.session["usuario_nome"] = usuario_nome
    return fk.render_template("perfil.html", arq_foto=usuario_id)

if __name__ == "__main__":
    srv.run(host="localhost",port=5050, debug=True)