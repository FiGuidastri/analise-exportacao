#%%
import pandas as pd
import duckdb as db
import os

# %%
# === Conexão com o banco duckdb ===
conn = db.connect(r'C:\Users\filipe.guidastri\Documents\Projetos\estudo-exportacao\warehouse.duckdb', read_only=False)

# Consultar os dados
df = conn.execute('''
                    SELECT 
                        e.CO_ANO AS Ano,
                        n.NO_NCM_POR AS Item,
                        m.NO_VIA AS Modal,
                        e.SG_UF_NCM as Estado,
                        SUM(e.QT_ESTAT) AS Quantidade,
                        SUM(e.KG_LIQUIDO) AS Volume,
                        SUM(e.VL_FOB) AS Valor
                    FROM f_exportacao e
                    INNER JOIN dimNcm n ON n.CO_NCM = e.CO_NCM
                    INNER JOIN dimEstados uf ON uf.CO_UF = e.CO_UNID
                    INNER JOIN dimModais m ON m.CO_VIA = e.CO_VIA
                    WHERE e.SG_UF_NCM IN ('SP', 'MS', 'PR')
                    GROUP BY e.CO_ANO, e.SG_UF_NCM, m.NO_VIA, n.NO_NCM_POR
                    ORDER BY Quantidade DESC;
''').fetchdf()

df.info()
# %%
df.head()
# %%
