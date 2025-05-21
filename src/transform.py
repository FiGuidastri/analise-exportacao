#%%
import pandas as pd
import numpy as np
#%%
df = pd.read_csv('../data/EXP_COMPLETA.csv', sep=';')

df.head()
#%%
df = df[df['CO_ANO'] > 2020] 
df.head()
# %%
df.info()
# %%
for col in df.select_dtypes(include=['int64']).columns:
    df[col] = df[col].astype(np.int32)
    
df.info()

# %%
# exportar os dados
df.to_csv('../data/dados_tratados.csv', sep=';', index=False)
# %%
