"""
ECU Manager (Tkinter + SQLite + CSV Import)
Autor: Victor Peixoto
"""

import os, sys, sqlite3, csv, subprocess
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog

DB_FILE = "ecus.db" # Caminho do banco de dados
TABLE_NAME = "modelos_ecu" # Nome da tabela

# ---------------- DATABASE ----------------
def get_connection(): # Conecta ao banco
    return sqlite3.connect(DB_FILE) # Retorna a conexão

def init_db(): # Cria a tabela
    conn = get_connection() # Conecta ao banco
    c = conn.cursor()# Cria um cursor
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num_bosch TEXT NOT NULL,
            modelo_ecu TEXT NOT NULL,
            fabricante TEXT NOT NULL,
            UNIQUE(num_bosch, modelo_ecu)
        )
    """) # Cria a tabela
    conn.commit() # Salva as alterações
    conn.close() # Fecha a conexão

def insert_ecu(num_bosch, modelo_ecu, fabricante): # Insere um ECU
    conn = get_connection() # Conecta ao banco
    c = conn.cursor() # Cria um cursor
    try: # Tenta inserir
        c.execute(f"INSERT INTO {TABLE_NAME} (num_bosch, modelo_ecu, fabricante) VALUES (?, ?, ?)",
                  (num_bosch.strip(), modelo_ecu.strip(), fabricante.strip())) # Insere o ECU
        conn.commit() # Salva as alterações
        rowid = c.lastrowid # Retorna o ID do ECU
    except sqlite3.IntegrityError: # Se o ECU ja existir
        rowid = None # Retorna None
    finally: # Fecha a conexão
        conn.close()
    return rowid # Retorna o ID do ECU

def update_ecu(row_id, num_bosch, modelo_ecu, fabricante): # Atualiza um ECU
    conn = get_connection()
    c = conn.cursor()
    try: # Tenta atualizar
        c.execute(f"UPDATE {TABLE_NAME} SET num_bosch=?, modelo_ecu=?, fabricante=? WHERE id=?",
                  (num_bosch.strip(), modelo_ecu.strip(), fabricante.strip(), row_id)) # Atualiza o ECU
        conn.commit()
        return c.rowcount > 0 # Retorna True se o ECU foi atualizado
    except Exception as e: # Se ocorrer um erro
        print("❌ Erro ao atualizar ECU:", e) # Imprime o erro
        return False
    finally:
        conn.close()

def delete_ecu(row_id): # Exclui um ECU
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"DELETE FROM {TABLE_NAME} WHERE id=?", (row_id,)) # Exclui o ECU
    conn.commit()
    ok = c.rowcount > 0 # Retorna True se o ECU foi excluido
    conn.close()
    return ok

def search_ecus(num_bosch_like="", modelo_like="", fabricante_like=""): # Busca ECUs
    conn = get_connection()
    c = conn.cursor()
    query = f"SELECT id, num_bosch, modelo_ecu, fabricante FROM {TABLE_NAME} WHERE 1=1" # Busca os ECUs
    params = [] # Lista de parâmetros
    if num_bosch_like: # Se o num_bosch for diferente de vazio
        query += " AND num_bosch LIKE ?" # Adiciona o parâmetro
        params.append(f"%{num_bosch_like}%") # Adiciona o parâmetro
    if modelo_like:     # Se o modelo_ecu for diferente de vazio
        query += " AND modelo_ecu LIKE ?" # Adiciona o parâmetro
        params.append(f"%{modelo_like}%")
    if fabricante_like:     # Se o fabricante for diferente de vazio
        query += " AND fabricante LIKE ?"
        params.append(f"%{fabricante_like}%")
    query += " ORDER BY id ASC"
    c.execute(query, params) # Executa a query
    rows = c.fetchall() # Retorna os ECUs
    conn.close()
    return rows

# ---------------- GUI ----------------
class ECUManagerApp:  # Classe da interface gráfica
    def __init__(self, root, nome_usuario):  # Construtor
        self.root = root
        self.root.title("Banco de dados de ECUs")
        self.root.geometry("1200x600")  # Tamanho da janela
        self.selected_id = None  # ID do ECU selecionado
        self.nome_usuario = nome_usuario  # Nome do usuário
        self._build_ui()  # Cria a interface gráfica
        self.refresh_grid()  # Atualiza a tabela

    def _build_ui(self):  # Cria a interface gráfica
        pad = 10  # PADDING
        # --- Cabeçalho ---
        header_frame = ctk.CTkFrame(self.root, fg_color="#1f1f1f", corner_radius=15)  # Cria um frame
        header_frame.pack(fill="x", padx=pad, pady=(pad, 0))
        lbl_user = ctk.CTkLabel(header_frame, text=f"Bem-vindo, {self.nome_usuario}!", font=("Arial", 16, "bold"),
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
        self.tree_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)  # Cria um frame
        self.tree_frame.pack(fill="both", expand=True, padx=pad, pady=pad)  # Preenche o frame

        import tkinter.ttk as ttk 
        style = ttk.Style() #
        style.configure("Treeview", background="#333333", fieldbackground="#2b2b2b", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        columns = ("num_bosch", "modelo_ecu", "fabricante")  # removendo ID
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", selectmode="browse")  # Cria a tabela
        for col, w in zip(columns, [300, 400, 250]):  # Nomes das colunas e larguras
            self.tree.heading(col, text=col.replace("_", " ").capitalize(), anchor="center") 
            self.tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_edit_clicked)

        # --- CRUD ---
        crud_frame = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)  # Cria um frame
        crud_frame.pack(fill="x", padx=pad, pady=(0, pad))  # Preenche o frame
        ctk.CTkLabel(crud_frame, text="Número BOSCH:").grid(row=0, column=0, padx=6, pady=6, sticky="w") # removendo ID
        self.entry_bosch = ctk.CTkEntry(crud_frame, width=180) 
        self.entry_bosch.grid(row=0, column=1, padx=6, pady=6) 
        ctk.CTkLabel(crud_frame, text="Modelo ECU:").grid(row=0, column=2, padx=6, pady=6, sticky="w") 
        self.entry_model = ctk.CTkEntry(crud_frame, width=300)
        self.entry_model.grid(row=0, column=3, padx=6, pady=6)
        ctk.CTkLabel(crud_frame, text="Fabricante:").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.entry_fabricante = ctk.CTkEntry(crud_frame, width=180)
        self.entry_fabricante.grid(row=0, column=5, padx=6, pady=6)

        ctk.CTkButton(crud_frame, text="Adicionar", command=self.on_add_clicked, width=100).grid(row=1, column=0, padx=6, pady=6) 
        ctk.CTkButton(crud_frame, text="Salvar Edição", command=self.on_save_edit_clicked, width=120).grid(row=1, column=1, padx=6, pady=6)
        ctk.CTkButton(crud_frame, text="Excluir Selecionado", command=self.on_delete_clicked, width=150).grid(row=1, column=2, padx=6, pady=6)
        ctk.CTkButton(crud_frame, text="Exportar CSV", command=self.on_export_csv, width=120).grid(row=1, column=3, padx=6, pady=6)
        ctk.CTkButton(crud_frame, text="Importar CSV", command=self.on_import_csv, width=120).grid(row=1, column=4, padx=6, pady=6)

        # Status
        self.status_var = ctk.StringVar(value="Pronto") # Atualiza o status
        ctk.CTkLabel(self.root, textvariable=self.status_var, fg_color="#1f1f1f", height=25).pack(fill="x", padx=pad, pady=(0, 0))

    # ---------------- CALLBACKS ----------------
    def set_status(self, text): # Atualiza o status
        self.status_var.set(text) 

    def refresh_grid(self, num="", model="", fabri=""): # Limpa a tabela
        for r in self.tree.get_children(): 
            self.tree.delete(r) #
        for row in search_ecus(num, model, fabri): # Preenche a tabela
            self.tree.insert("", "end", iid=row[0], values=(row[1], row[2], row[3])) 

    def on_search(self): # Limpa a busca
        self.refresh_grid(self.search_bosch.get().strip(), 
                          self.search_model.get().strip(),
                          self.search_fabricante.get().strip()) # Limpa a busca
        self.set_status("Busca atualizada") 

    def on_clear_search(self): # Limpa a busca
        self.search_bosch.delete(0, "end") 
        self.search_model.delete(0, "end") 
        self.search_fabricante.delete(0, "end")
        self.refresh_grid() 
        self.set_status("Busca limpa")

    def on_tree_select(self, event): # Seleciona o ECU
        sel = self.tree.selection() 
        if sel: 
            vals = self.tree.item(sel[0], "values")
            self.selected_id = int(sel[0])
            self.entry_bosch.delete(0, "end"); self.entry_bosch.insert(0, vals[0]) # Limpa e insere o ECU selecionado
            self.entry_model.delete(0, "end"); self.entry_model.insert(0, vals[1]) # Limpa e insere o ECU selecionado
            self.entry_fabricante.delete(0, "end"); self.entry_fabricante.insert(0, vals[2]) # Limpa e insere o ECU selecionado

    def on_add_clicked(self): # Adiciona o ECU
        num = self.entry_bosch.get().strip()
        model = self.entry_model.get().strip()
        fabri = self.entry_fabricante.get().strip() # Limpa e insere o ECU selecionado
        if not num or not model or not fabri: # Verifica se todos os campos foram preenchidos
            messagebox.showwarning("Aviso", "Preencha todos os campos.") # Exibe uma mensagem de aviso caso algum campo esteja vazio
            return
        if insert_ecu(num, model, fabri): # Insere o ECU na tabela
            self.refresh_grid()
        else:
            messagebox.showinfo("Duplicado", "Essa ECU já existe.") 

    def on_save_edit_clicked(self): # Atualiza o ECU
        if not self.selected_id: # Verifica se um ECU foi selecionado
            messagebox.showwarning("Selecione", "Selecione um registro.") # Exibe uma mensagem de aviso caso nenhum ECU seja selecionado
            return
        num = self.entry_bosch.get().strip()
        model = self.entry_model.get().strip()
        fabri = self.entry_fabricante.get().strip() # Limpa e insere o ECU selecionado 
        if not num or not model or not fabri: # Verifica se todos os campos foram preenchidos
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        if update_ecu(self.selected_id, num, model, fabri): # Atualiza o ECU  
            self.refresh_grid()
        else:
            messagebox.showerror("Erro", "Falha ao atualizar registro.")

    def on_delete_clicked(self): # Exclui o ECU
        if not self.selected_id: # Verifica se um ECU foi selecionado 
            messagebox.showwarning("Selecione", "Selecione um registro.")
            return
        if messagebox.askyesno("Excluir", f"Excluir registro selecionado?"):
            if delete_ecu(self.selected_id):
                self.refresh_grid()

    def on_export_csv(self): # Exporta o ECU
        rows = search_ecus() # Busca os ECUs
        if not rows: # Verifica se os ECUs foram encontrados
            messagebox.showinfo("Vazio", "Nenhum registro para exportar.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path: # Verifica se o caminho foi selecionado
            return
        with open(path, "w", newline="", encoding="utf-8") as f: # Abre o arquivo para escrita
            writer = csv.writer(f)
            writer.writerow(["num_bosch","modelo_ecu","fabricante"])
            writer.writerows([(r[1], r[2], r[3]) for r in rows]) # Escreve os ECUs no arquivo
        messagebox.showinfo("Exportado", f"{len(rows)} registros salvos em {path}")

    def on_import_csv(self): # Importa o ECU
        path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")]) # Abre o arquivo para leitura
        if not path: # Verifica se o caminho foi selecionado
            return
        imported, skipped = 0, 0 # Contadores
        try:
            with open(path, newline="", encoding="utf-8") as f: # Abre o arquivo para leitura
                reader = csv.DictReader(f) # Leitura do CSV
                for row in reader: # Para cada linha do CSV 
                    num = row.get("num_bosch") or row.get("NumeroBosch") # Verifica se o campo num_bosch ou NumeroBosch foi encontrado
                    model = row.get("modelo_ecu") or row.get("Modelo") # Verifica se o campo modelo_ecu ou Modelo foi encontrado
                    fabri = row.get("fabricante") or row.get("Fabricante") # Verifica se o campo fabricante ou Fabricante foi encontrado
                    if num and model and fabri: # Verifica se todos os campos foram encontrados
                        res = insert_ecu(num, model, fabri) # Insere o ECU
                        if res: imported +=1 # Verifica se o ECU foi inserido
                        else: skipped +=1 # Verifica se o ECU foi duplicado
            self.refresh_grid()
            messagebox.showinfo("Importação Concluída", f"Importados: {imported}\nDuplicados ignorados: {skipped}")
        except Exception as e:
            messagebox.showerror("Erro ao importar", str(e))

    def on_edit_clicked(self, event=None): 
        self.on_tree_select(event) 

    def logout(self):
        self.root.destroy()

# ---------------- MAIN ----------------
def main(): # Função principal
    if len(sys.argv) < 3: # Verifica se os argumentos foram fornecidos
        print("❌ Acesso negado: execute via login.exe")
        sys.exit() # Encerra o programa
    nome_usuario = sys.argv[1] 
    token = sys.argv[2] # Verifica se o token foi fornecido
    if len(token) != 32: # Verifica se o token foi fornecido com 32 caracteres 
        print("❌ Token inválido!")
        sys.exit() # Encerra o programa

    init_db() # Inicializa o banco de dados
    ctk.set_appearance_mode("dark") # Define o modo de aparencia
    ctk.set_default_color_theme("blue") # Define o tema de cores
    root = ctk.CTk() # Cria a janela
    app = ECUManagerApp(root, nome_usuario) # Cria a classe ECUManagerApp
    root.mainloop() # Inicia a janela

if __name__ == "__main__":  # Verifica se o arquivo foi executado diretamente 
    main()
