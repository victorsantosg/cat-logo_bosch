#!/usr/bin/env python3
"""
ECU Manager (CustomTkinter + SQLite + CSV Import)
Autor: Victor Peixoto
"""

import os
import sqlite3
import csv
import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox

DB_FILE = "ecus.db"
TABLE_NAME = "modelos_ecu"

# ---------------- DATABASE ----------------
def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num_bosch TEXT NOT NULL,
            modelo_ecu TEXT NOT NULL,
            fabricante TEXT NOT NULL,
            UNIQUE(num_bosch, modelo_ecu)
        )
    """)
    conn.commit()
    conn.close()

def insert_ecu(num_bosch, modelo_ecu, fabricante):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(f"INSERT INTO {TABLE_NAME} (num_bosch, modelo_ecu, fabricante) VALUES (?, ?, ?)",
                  (num_bosch.strip(), modelo_ecu.strip(), fabricante.strip()))
        conn.commit()
        return c.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def update_ecu(row_id, num_bosch, modelo_ecu, fabricante):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(f"UPDATE {TABLE_NAME} SET num_bosch=?, modelo_ecu=?, fabricante=? WHERE id=?",
                  (num_bosch.strip(), modelo_ecu.strip(), fabricante.strip(), row_id))
        conn.commit()
        return c.rowcount > 0
    finally:
        conn.close()

def delete_ecu(row_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"DELETE FROM {TABLE_NAME} WHERE id=?", (row_id,))
    conn.commit()
    ok = c.rowcount > 0
    conn.close()
    return ok

def search_ecus(num_bosch_like="", modelo_like="", fabricante_like=""):
    conn = get_connection()
    c = conn.cursor()
    query = f"SELECT id, num_bosch, modelo_ecu, fabricante FROM {TABLE_NAME} WHERE 1=1"
    params = []
    if num_bosch_like:
        query += " AND num_bosch LIKE ?"
        params.append(f"%{num_bosch_like}%")
    if modelo_like:
        query += " AND modelo_ecu LIKE ?"
        params.append(f"%{modelo_like}%")
    if fabricante_like:
        query += " AND fabricante LIKE ?"
        params.append(f"%{fabricante_like}%")
    query += " ORDER BY id ASC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

# ---------------- GUI ----------------
class ECUManagerApp:
    def __init__(self, root, nome_usuario):
        self.root = root
        self.root.title("Banco de dados de ECUs")
        self.root.geometry("1200x600")
        self.selected_id = None

        self._build_ui(nome_usuario)
        self.refresh_grid()

    def _build_ui(self, nome_usuario):
        pad = 10
        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self.root, fg_color="#1f1f1f", corner_radius=15)
        header_frame.pack(fill="x", padx=pad, pady=(pad, 0))
        lbl_user = ctk.CTkLabel(header_frame, text=f"Bem-vindo, {nome_usuario}!", font=("Arial", 16, "bold"),
                                text_color="lightgreen")
        lbl_user.pack(side="left", padx=10, pady=10)

        btn_logout = ctk.CTkButton(header_frame, text="Sair", width=100, corner_radius=12,
                                   command=self.logout)
        btn_logout.pack(side="right", padx=10, pady=10)

        # --- Busca ---
        search_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        search_frame.pack(fill="x", padx=pad, pady=(pad, 0))
        self.search_bosch = ctk.CTkEntry(search_frame, placeholder_text="Número BOSCH", width=180)
        self.search_bosch.grid(row=0, column=0, padx=6, pady=6)
        self.search_model = ctk.CTkEntry(search_frame, placeholder_text="Modelo ECU", width=180)
        self.search_model.grid(row=0, column=1, padx=6, pady=6)
        self.search_fabricante = ctk.CTkEntry(search_frame, placeholder_text="Fabricante", width=180)
        self.search_fabricante.grid(row=0, column=2, padx=6, pady=6)

        ctk.CTkButton(search_frame, text="Buscar", command=self.on_search, width=100).grid(row=0, column=3, padx=6)
        ctk.CTkButton(search_frame, text="Limpar Busca", command=self.on_clear_search, width=120).grid(row=0, column=4, padx=6)

        # --- Grid ---
        self.tree_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15) # Cor de fundo
        self.tree_frame.pack(fill="both", expand=True, padx=pad, pady=pad) # Preenchimento

        # Aqui usamos ttk.Treeview, não há alternativa CTk, mas podemos ajustar cores

        #---- Grid --- (CTkTreeview)
        import tkinter.ttk as ttk
        style = ttk.Style()
        style.theme_use("clam") 

        # Estilos do corpo da tabela
        style.configure("Treeview", # Estilo do corpo
                     font=("Arial", 9), # Fonte
                     rowheight=24, # Altura das linhas
                     background="#262626", # Cor de fundo
                     foreground="#FFFFFF", # Cor da fonte
                     fieldbackground="#262626") # Cor de fundo das linhas
        
        # Estilos do cabeçalho da tabela 
        style.configure("Treeview.Heading", # Estilo do cabeçalho
                     font=("Arial", 11, "bold"), # Fonte em negrito
                     background="#262626", # Cor de fundo
                     foreground="#ffffff") # Cor da fonte
        
        # Definição das colunas da tabela
        columns = ("✅", "Numero BOSCH", "Modelo", "Fabricante") # Nomes das colunas
        self.tree = ttk.Treeview(self.tree_frame, # Definição da tabela
                                 columns=columns, # Colunas da tabela
                                 show="headings", # Mostra cabeçalhos
                                 selectmode="browse") # Modo de seleção
        
        # Configuração dos cabeçalhos e larguras das colunas
        for col, w in zip(columns, [220, 420, 220, 420]): # Nomes das colunas e larguras
            header_text = {
                "✅": "✅", 
                "Numero BOSCH": "Número BOSCH", 
                "Modelo": "Modelo", 
                "Fabricante": "Fabricante"
            }[col]
            self.tree.heading(col, text=header_text, anchor="center") # Texto do cabeçalho
            self.tree.column(col, width=w, anchor="center") # Largura da coluna

        # Barra de rolagem
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        # Ajustes para redimensionamento dinamico
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)

        #Estilo de linhas alternadas
        self.tree.tag_configure("evenrow", background="#262626") # Cor de fundo
        self.tree.tag_configure("oddrow", background="#333333") # Cor de fundo

        # Eventos
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_edit_clicked)

        # --- CRUD ---
        crud_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        crud_frame.pack(fill="x", padx=pad, pady=(0, pad))
        self.entry_bosch = ctk.CTkEntry(crud_frame, placeholder_text="Número BOSCH", width=180)
        self.entry_bosch.grid(row=0, column=0, padx=6, pady=6)
        self.entry_model = ctk.CTkEntry(crud_frame, placeholder_text="Modelo ECU", width=180)
        self.entry_model.grid(row=0, column=1, padx=6, pady=6)
        self.entry_fabricante = ctk.CTkEntry(crud_frame, placeholder_text="Fabricante", width=180)
        self.entry_fabricante.grid(row=0, column=2, padx=6, pady=6)

        ctk.CTkButton(crud_frame, text="Adicionar", command=self.on_add_clicked).grid(row=1, column=0, padx=6, pady=6)
        ctk.CTkButton(crud_frame, text="Salvar Edição", command=self.on_save_edit_clicked).grid(row=1, column=1, padx=6, pady=6)
        ctk.CTkButton(crud_frame, text="Excluir Selecionado", command=self.on_delete_clicked).grid(row=1, column=2, padx=6, pady=6)
        ctk.CTkButton(crud_frame, text="Exportar CSV", command=self.on_export_csv).grid(row=1, column=3, padx=6, pady=6)
        ctk.CTkButton(crud_frame, text="Importar CSV", command=self.on_import_csv).grid(row=1, column=4, padx=6, pady=6)

        # --- Status ---
        self.status_var = ctk.StringVar(value="Pronto")
        status_label = ctk.CTkLabel(self.root, textvariable=self.status_var, fg_color="#1f1f1f", corner_radius=10)
        status_label.pack(fill="x", padx=pad, pady=(0, pad))

    # ---------------- CALLBACKS ----------------
    def set_status(self, text): # Atualiza o status
        self.status_var.set(text) # Atualiza o status

    def refresh_grid(self, num="", model="", fabri=""): 
        for r in self.tree.get_children(): # Limpa a tabela
            self.tree.delete(r) # Limpa a tabela
        for row in search_ecus(num, model, fabri): # Preenche a tabela
            self.tree.insert("", "end", values=row) # Preenche a tabela

    def on_search(self):
        self.refresh_grid(self.search_bosch.get(), self.search_model.get(), self.search_fabricante.get())
        self.set_status("Busca atualizada")

    def on_clear_search(self): # Limpa a busca
        self.search_bosch.delete(0, "end") # Limpa a busca
        self.search_model.delete(0, "end") 
        self.search_fabricante.delete(0, "end")
        self.refresh_grid()
        self.set_status("Busca limpa")

    def on_tree_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            self.selected_id = None
            return
        vals = self.tree.item(sel[0])["values"]
        self.selected_id = vals[0]
        self.entry_bosch.delete(0, "end")
        self.entry_bosch.insert(0, vals[1])
        self.entry_model.delete(0, "end")
        self.entry_model.insert(0, vals[2])
        self.entry_fabricante.delete(0, "end")
        self.entry_fabricante.insert(0, vals[3])

    def on_add_clicked(self):
        num = self.entry_bosch.get().strip()
        model = self.entry_model.get().strip()
        fabri = self.entry_fabricante.get().strip()
        if not num or not model or not fabri:
            messagebox.showwarning("Aviso", "Preencha todos os campos")
            return
        if insert_ecu(num, model, fabri):
            self.refresh_grid()
        else:
            messagebox.showinfo("Duplicado", "Essa ECU já existe.")

    def on_save_edit_clicked(self):
        if not self.selected_id:
            messagebox.showwarning("Aviso", "Selecione um registro")
            return
        if update_ecu(self.selected_id, self.entry_bosch.get(), self.entry_model.get(), self.entry_fabricante.get()):
            self.refresh_grid()
        else:
            messagebox.showerror("Erro", "Falha ao atualizar registro.")

    def on_delete_clicked(self):
        if not self.selected_id:
            messagebox.showwarning("Aviso", "Selecione um registro")
            return
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir?"):
            delete_ecu(self.selected_id)
            self.refresh_grid()

    def on_export_csv(self):
        rows = search_ecus()
        if not rows:
            messagebox.showinfo("Info", "Nenhum registro para exportar")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id","num_bosch","modelo_ecu","fabricante"])
            writer.writerows(rows)
        messagebox.showinfo("Exportado", f"{len(rows)} registros salvos")

    def on_import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        imported, skipped = 0, 0
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    num = row.get("num_bosch")
                    model = row.get("modelo_ecu")
                    fabri = row.get("fabricante")
                    if num and model and fabri:
                        if insert_ecu(num, model, fabri): imported +=1
                        else: skipped +=1
            self.refresh_grid()
            messagebox.showinfo("Importação Concluída", f"Importados: {imported}\nDuplicados: {skipped}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def on_edit_clicked(self, event=None):
        self.on_tree_select(event)

    def logout(self):
        """Fecha main.py e reabre login.py"""
        import subprocess, sys
        self.root.destroy()
        subprocess.Popen([sys.executable, "login.py"])

# ---------------- MAIN ----------------
def main():
    if len(sys.argv) < 3:
        print("❌ Acesso negado: execute via login_app.py")
        sys.exit()
    nome_usuario = sys.argv[1]
    token = sys.argv[2]
    if len(token) != 32:
        print("❌ Token inválido!")
        sys.exit()

    init_db()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    ECUManagerApp(root, nome_usuario)

    root.mainloop()


if __name__ == "__main__":
    main()
