# upload_warehouse.py

import pandas as pd
import numpy as np
import duckdb
import os

# === 1. Ler CSV tratado ===
caminho_csv = r'../data/dados_tratados.csv'
if not os.path.exists(caminho_csv):
    raise FileNotFoundError(f"Arquivo '{caminho_csv}' não encontrado.")

df = pd.read_csv(caminho_csv, sep=';')

# === 3. Criar (ou conectar) ao warehouse ===
caminho_warehouse = 'warehouse.duckdb'
con = duckdb.connect(caminho_warehouse)

# === 4. Criar tabela e popular ===
nome_tabela = 'f_exportacao'

# Registra o DataFrame temporariamente
con.register('df_temp', df)

# Cria a tabela se ainda não existir
con.execute(f"""
    CREATE TABLE IF NOT EXISTS {nome_tabela} AS SELECT * FROM df_temp LIMIT 0
""")

# Insere os dados
con.execute(f"""
    INSERT INTO {nome_tabela} SELECT * FROM df_temp
""")

print(f"✅ Warehouse criado em '{caminho_warehouse}' e {len(df)} registros inseridos na tabela '{nome_tabela}'.")


