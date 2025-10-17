import pandas as pd

arquivo_original = "bosch_ecu_final.csv"
arquivo_limpo = "bosch_ecu_limpo.csv"

# Lê o arquivo como texto bruto para corrigir aspas e espaços
with open(arquivo_original, "r", encoding="utf-8", errors="ignore") as f:
    linhas = f.readlines()

# Remove aspas problemáticas e espaços extras
linhas_limpas = []
for linha in linhas:
    linha = linha.replace('",', ',')   # remove aspas antes de vírgula
    linha = linha.replace(',"', ',')   # remove aspas depois de vírgula
    linha = linha.replace('"', '')     # remove aspas isoladas
    linha = linha.strip()              # remove quebras e espaços
    if linha:
        linhas_limpas.append(linha)

# Salva um CSV temporário sem aspas quebradas
arquivo_temp = "bosch_ecu_temp.csv"
with open(arquivo_temp, "w", encoding="utf-8") as f:
    f.write("\n".join(linhas_limpas))

# Agora lê normalmente com pandas
df = pd.read_csv(arquivo_temp, sep=",", engine="python", on_bad_lines="skip")

print("Colunas detectadas:", df.columns.tolist())

# Renomeia para padronizar
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
renomear = {
    'numerobosch': 'num_bosch',
    'numero_bosch': 'num_bosch',
    'bosch': 'num_bosch',
    'modelo': 'modelo_ecu',
    'ecu': 'modelo_ecu',
    'fabricanteecu': 'fabricante',
}
df.rename(columns=renomear, inplace=True)

# Filtra apenas colunas importantes
df = df[[c for c in df.columns if any(k in c for k in ['bosch', 'modelo', 'fabricante'])]]
df.columns = ['num_bosch', 'modelo_ecu', 'fabricante'][:len(df.columns)]

# Remove espaços e nulos
for col in df.columns:
    df[col] = df[col].astype(str).str.strip()

df.dropna(subset=["num_bosch", "modelo_ecu"], inplace=True)
df.drop_duplicates(subset=["num_bosch", "modelo_ecu"], inplace=True)

# Mostra resultado
print(f"\n✅ Linhas válidas: {len(df)}")
print(df.head(10))

# Salva o novo CSV limpo
df.to_csv(arquivo_limpo, index=False, encoding="utf-8")
print(f"\n✅ Arquivo limpo salvo como: {arquivo_limpo}")
