import flask as fk
from flask import Flask, request, render_template, app
from secrets import token_hex
import model as md
from urllib.parse import quote, unquote

srv = fk.Flask(__name__)
srv.secret_key = token_hex()

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

if __name__ == "__main__":
    srv.run(host="localhost",port=5050, debug=True)