import pandas as pd
import duckdb as db

# Conexão com o banco duckdb
conn = db.connect(r'../warehouse.duckdb', read_only=False)

# Define abas desejadas: {nome_aba: nome_tabela}
abas_desejadas = {
    "6": "dimNcm",
    "10": "dimPaises",
    "12": "dimEstados",
    "14": "dimModais"
}

# Ler apenas as abas desejadas
sheets = pd.read_excel(
    r'../data/TABELAS_AUXILIARES.xlsx',
    sheet_name=list(abas_desejadas.keys())
)

# Iterar sobre cada aba
for nome_aba, df in sheets.items():
    nome_tabela = abas_desejadas[nome_aba]  # usa o nome da tabela definido no dicionário

    # Registrar temporariamente
    conn.register("temp_df", df)

    # Criar a tabela automaticamente com base nos dados
    conn.execute(f"DROP TABLE IF EXISTS {nome_tabela}")
    conn.execute(f"CREATE TABLE {nome_tabela} AS SELECT * FROM temp_df")

    print(f"Tabela '{nome_tabela}' criada com sucesso com {len(df)} registros.")

print("✅ Todas as tabelas auxiliares foram criadas com sucesso.")

# Fechar conexão
conn.close()
