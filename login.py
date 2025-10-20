#!/usr/bin/env python3
import customtkinter as ctk
from tkinter import messagebox
import sqlite3, os, subprocess, re, hashlib, sys, secrets

DB_USERS = "usuarios.db"

# ------------------ BANCO DE USUÁRIOS ------------------
def conectar():
    conn = sqlite3.connect(DB_USERS)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            endereco TEXT,
            usuario TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

def hash_senha(senha: str):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def validar_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

# ------------------ CADASTRO ------------------
def cadastrar_usuario():
    def salvar_cadastro():
        nome = entry_nome.get().strip()
        email = entry_email.get().strip()
        endereco = entry_endereco.get().strip()
        usuario = entry_usuario.get().strip()
        senha = entry_senha.get().strip()

        if not all([nome, email, usuario, senha]):
            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios!")
            return
        if not validar_email(email):
            messagebox.showerror("Erro", "Email inválido!")
            return

        senha_hash = hash_senha(senha)
        conn = conectar()
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (nome, email, endereco, usuario, senha_hash) VALUES (?, ?, ?, ?, ?)",
                      (nome, email, endereco, usuario, senha_hash))
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            janela_cadastro.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário ou email já cadastrado!")
        finally:
            conn.close()

    janela_cadastro = ctk.CTkToplevel(app)
    janela_cadastro.title("Cadastro de Novo Usuário")
    janela_cadastro.geometry("400x420")
    janela_cadastro.transient(app)
    janela_cadastro.grab_set()
    janela_cadastro.focus_force()
    janela_cadastro.lift()

    ctk.CTkLabel(janela_cadastro, text="Cadastro de Usuário", font=("Arial", 20, "bold")).pack(pady=15)
    entry_nome = ctk.CTkEntry(janela_cadastro, placeholder_text="Nome completo"); entry_nome.pack(pady=8)
    entry_email = ctk.CTkEntry(janela_cadastro, placeholder_text="Email"); entry_email.pack(pady=8)
    entry_endereco = ctk.CTkEntry(janela_cadastro, placeholder_text="Endereço (opcional)"); entry_endereco.pack(pady=8)
    entry_usuario = ctk.CTkEntry(janela_cadastro, placeholder_text="Usuário"); entry_usuario.pack(pady=8)
    entry_senha = ctk.CTkEntry(janela_cadastro, placeholder_text="Senha", show="*"); entry_senha.pack(pady=8)
    ctk.CTkButton(janela_cadastro, text="Cadastrar", command=salvar_cadastro).pack(pady=20)

# ------------------ LOGIN ------------------
def login():
    usuario_text = entry_usuario.get().strip()
    senha_text = entry_senha.get().strip()

    if not usuario_text or not senha_text:
        messagebox.showwarning("Aviso", "Preencha usuário e senha!")
        return

    senha_hash = hash_senha(senha_text)
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT nome FROM usuarios WHERE usuario=? AND senha_hash=?", (usuario_text, senha_hash))
    row = c.fetchone()
    conn.close()

    if row:
        nome_usuario = row[0]
        token = secrets.token_hex(16)  # token de 32 caracteres
        app.destroy()  # fecha login

        # Definir caminho do main.exe (ou main.py em dev)
        if getattr(sys, 'frozen', False):
            # Está rodando como exe (PyInstaller)
            caminho_main = os.path.join(sys._MEIPASS, "main.exe")
        else:
            # Rodando como script Python
            caminho_main = os.path.join(os.getcwd(), "main.py")

        if os.path.exists(caminho_main):
            python_exe = sys.executable
            # Se for exe, podemos abrir diretamente
            args = [caminho_main, nome_usuario, token]
            if caminho_main.endswith(".py"):
                # Se for script Python, usar pythonw.exe para não mostrar console
                python_exe = python_exe.replace("python.exe", "pythonw.exe")
                if not os.path.exists(python_exe):
                    python_exe = sys.executable
                args = [python_exe, caminho_main, nome_usuario, token]

            subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS
            )
        else:
            messagebox.showerror("Erro", "main.exe ou main.py não encontrado!")
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos!")

# ------------------ INTERFACE ------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Login - ECU Manager")
app.geometry("400x320")

frame = ctk.CTkFrame(app, corner_radius=10)
frame.pack(pady=40, padx=40, fill="both", expand=True)

ctk.CTkLabel(frame, text="Login", font=("Arial", 22, "bold")).pack(pady=10)
entry_usuario = ctk.CTkEntry(frame, placeholder_text="Usuário"); entry_usuario.pack(pady=10)
entry_senha = ctk.CTkEntry(frame, placeholder_text="Senha", show="*"); entry_senha.pack(pady=10)
ctk.CTkButton(frame, text="Entrar", command=login).pack(pady=10)
ctk.CTkButton(frame, text="Cadastrar novo usuário", command=cadastrar_usuario, fg_color="gray", hover_color="dimgray").pack(pady=10)

app.mainloop()
