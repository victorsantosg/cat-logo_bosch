# ⚙️ ECU Manager

**ECU Manager** é uma aplicação desktop desenvolvida em **Python** com **CustomTkinter**, **SQLite3** e **criptografia de senhas (hash)**, criada para gerenciar dados técnicos de **ECUs automotivas**.
O sistema inclui autenticação de usuários, controle de acesso seguro e uma interface moderna para cadastro, consulta, edição e exportação de informações.

---

## 🧩 Funcionalidades Principais

### 🔐 Autenticação Segura

* Tela de **login e cadastro de usuários**.
* Armazenamento seguro das senhas com **hash (bcrypt)**.
* Validação de e-mail antes do cadastro.
* Proteção contra acesso direto: o arquivo `main.py` só pode ser aberto após login bem-sucedido.

### 🗃️ Gerenciamento de Banco de Dados (ECUs)

* Banco local em **SQLite3** (`ecus.db`).
* Tabela estruturada com campos:

  * `num_bosch`
  * `modelo_ecu`
  * `fabricante`
* Controle de duplicidade e atualizações automáticas.
* CRUD completo:

  * Adicionar
  * Editar
  * Excluir
  * Buscar

### 📁 Importação e Exportação

* Importa dados de ECUs a partir de **arquivos CSV**.
* Exporta registros para **CSV** com apenas um clique.

### 🎨 Interface Moderna

* Desenvolvida com **CustomTkinter**:

  * Design escuro elegante.
  * Cantos arredondados.
  * Campos com placeholders.
  * Botões e frames com cores harmônicas e tipografia consistente.
* Linhas “zebradas” no grid (Treeview) para melhor leitura.
* Mensagens sutis e automáticas (sem alertas intrusivos).

---

## 🖼️ Estrutura do Projeto

```
📂 ECU-Manager/
├── login.py        # Tela de login e cadastro (hash + validação)
├── main.py         # Área principal: gerenciamento de ECUs
├── ecus.db         # Banco de dados SQLite
├── users.db        # Banco de dados de usuários
├── requirements.txt
└── README.md
```

---

## 🧠 Tecnologias Utilizadas

| Categoria      | Ferramenta                                                      |
| -------------- | --------------------------------------------------------------- |
| Interface      | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| Banco de dados | SQLite3                                                         |
| Segurança      | Bcrypt (hash de senhas)                                         |
| Backend        | Python 3.12+                                                    |
| CSV            | csv (biblioteca padrão Python)                                  |

---

## 🚀 Como Executar

### 1️⃣ Instalar dependências

```bash
pip install customtkinter bcrypt
```

### 2️⃣ Executar o sistema

Inicie pela tela de login:

```bash
python login.py
```

Após login bem-sucedido, a aplicação abrirá automaticamente o `main.py`.

---

## 🧰 Recursos da Tela Principal

| Função            | Descrição                                               |
| ----------------- | ------------------------------------------------------- |
| **Buscar ECU**    | Filtra registros por número Bosch, modelo ou fabricante |
| **Adicionar**     | Insere nova ECU na base de dados                        |
| **Salvar Edição** | Atualiza o registro selecionado                         |
| **Excluir**       | Remove o item selecionado                               |
| **Importar CSV**  | Lê registros de um arquivo externo                      |
| **Exportar CSV**  | Gera relatório completo da base                         |
| **Sair**          | Retorna à tela de login                                 |

---

## 🔒 Segurança

* Senhas nunca são armazenadas em texto puro.
* Todo login gera um **token de sessão temporário** para validação da execução.
* `main.py` não pode ser iniciado diretamente (verificação obrigatória de token).

---

## 🧱 Empacotando o Aplicativo em .exe

Para gerar um executável do seu sistema e rodar sem precisar abrir o Python:

### 1️⃣ Instalar o **PyInstaller**

```bash
pip install pyinstaller
```

### 2️⃣ Criar o executável

Execute o comando abaixo no terminal, dentro da pasta do projeto:

```bash
pyinstaller --noconsole --onefile --icon=icone.ico login.py
```

**Opções:**

* `--noconsole` → oculta o terminal ao abrir o app.
* `--onefile` → gera apenas um único arquivo `.exe`.
* `--icon=icone.ico` → adiciona um ícone personalizado (opcional).

### 3️⃣ Local do executável

Após o processo, o arquivo `.exe` estará em:

```
dist/login.exe
```

Basta executá-lo para iniciar o programa.

> ⚠️ **Dica:** Inclua os arquivos `users.db` e `ecus.db` na mesma pasta do `.exe`, ou adicione lógica no código para criá-los automaticamente se não existirem.

---

## 👨‍💻 Autor

**Victor Peixoto Santos**
📅 Desenvolvido em **17 de Outubro de 2025**
💡 “Transformando código em soluções práticas e seguras.”

---

## 📸 Screenshot 

> Interface do Programa (`/img/Banco_de_dados_ecu.png`)

---

## 📜 Licença

Projeto desenvolvido para fins educacionais e profissionais.
Licenciado sob a **MIT License**.
