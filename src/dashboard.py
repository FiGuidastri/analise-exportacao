import streamlit as st
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(layout="wide")
st.title("📊 Dashboard de Exportações")

# Conexão com DuckDB
conn = duckdb.connect(r'../warehouse.duckdb')

# Consulta SQL
query = """
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
GROUP BY e.CO_ANO, e.SG_UF_NCM, m.NO_VIA, n.NO_NCM_POR;
"""

# Cache dos dados
@st.cache_data
def carregar_dados():
    return conn.execute(query).df()

df = carregar_dados()

# Sidebar – Filtros
st.sidebar.header("🔍 Filtros")
itens = sorted(df["Item"].unique())
item_selecionado = st.sidebar.selectbox("Filtrar por Item (opcional)", ["Todos"] + itens)

# Filtragem
if item_selecionado != "Todos":
    df_filtrado = df[df["Item"] == item_selecionado]
else:
    df_filtrado = df.copy()

# =====================
# ANÁLISES PRINCIPAIS
# =====================
# Valor de exportação por ano
valor_por_ano = df_filtrado.groupby("Ano")["Valor"].sum().reset_index()
st.subheader("📈 Valor de Exportação por Ano")
st.line_chart(valor_por_ano.set_index("Ano"))

# Valor por modal
st.subheader("🚛 Valor por Modal")
valor_modal = df_filtrado.groupby("Modal")["Valor"].sum().reset_index()
st.bar_chart(valor_modal.set_index("Modal"))

# Valor por estado
st.subheader("🗺️ Valor por Estado")
valor_estado = df_filtrado.groupby("Estado")["Valor"].sum().reset_index()
st.bar_chart(valor_estado.set_index("Estado"))

# =====================
# NOVAS ANÁLISES
# =====================

# Top 10 itens exportados no ano mais recente
ano_recente = df_filtrado["Ano"].max()
top_itens = df_filtrado[df_filtrado["Ano"] == ano_recente].groupby("Item")["Valor"].sum().nlargest(10).reset_index()
st.subheader(f"🏆 Top 10 Itens Exportados em {ano_recente}")
st.bar_chart(top_itens.set_index("Item"))

# Mapa de calor Estado x Modal
st.subheader("🌐 Mapa de Calor: Estado x Modal (Valor de Exportação em R$ milhões)")

# Preparando a tabela dinâmica
pivot_heatmap = df_filtrado.pivot_table(
    index="Estado", columns="Modal", values="Valor", aggfunc="sum", fill_value=0
)

# Convertendo para milhões para melhor leitura
pivot_milhoes = pivot_heatmap / 1_000_000

#mapa de calor
# Tamanho ajustado dinamicamente
fig, ax = plt.subplots(figsize=(1 + len(pivot_milhoes.columns)*1.2, 0.5 + len(pivot_milhoes)*0.5))

sns.heatmap(
    pivot_milhoes,
    annot=True,
    fmt=".1f",
    cmap="YlGnBu",
    linewidths=0.5,
    linecolor='gray',
    cbar_kws={"label": "Valor (R$ milhões)"},
    ax=ax
)

ax.set_title("Exportações por Estado e Modal", fontsize=14)
plt.xticks(rotation=45)
plt.yticks(rotation=0)
st.pyplot(fig)


# Comparativo Volume vs Valor por Modal
comparativo_modal = df_filtrado.groupby("Modal")[["Volume", "Valor"]].sum().reset_index()
st.subheader("📦 Volume vs Valor por Modal")
st.bar_chart(comparativo_modal.set_index("Modal"))

# Evolução da quantidade exportada por ano
quant_por_ano = df_filtrado.groupby("Ano")["Quantidade"].sum().reset_index()
st.subheader("📦 Quantidade Exportada por Ano")
st.line_chart(quant_por_ano.set_index("Ano"))

# =====================
# Download dos dados
# =====================
st.subheader("⬇️ Exportar Dados")
st.download_button(
    "📥 Baixar dados filtrados (CSV)",
    data=df_filtrado.to_csv(index=False),
    file_name="exportacoes_filtradas.csv",
    mime="text/csv"
)
