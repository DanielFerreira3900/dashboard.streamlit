import numpy as np
import plotly.express as px
import os
import warnings
import pandas as pd 
import streamlit as st
import matplotlib.pyplot as plt 

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superloja", page_icon="📊", layout="wide")
st.title("📊 Amostra Superloja EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: UPLOAD A FILE", type=["csv", "txt", "xlsx", "xls"])
if fl is not None:
    filename = fl.name
    st.write(filename)
    
    try:
        if filename.endswith('.csv') or filename.endswith('.txt'):
            df = pd.read_csv(fl, encoding='latin1')
        else:
            df = pd.read_excel(fl)
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
else:
    os.chdir(r"C:\Users\Daniel Augusto\Documents\dados")
    df = pd.read_excel("Sample - Superstore.xls")

# Corrige nomes com espaços e letras
df.columns = df.columns.str.strip()
df.rename(columns={"Order Date": "OrdemData"}, inplace=True)
df["OrdemData"] = pd.to_datetime(df["OrdemData"])

datainicial = df["OrdemData"].min()
datafinal = df["OrdemData"].max()

col1, col2 = st.columns((2))
with col1:
    data1 = pd.to_datetime(st.date_input("Data Inicial", datainicial))
with col2:
    data2 = pd.to_datetime(st.date_input("Data Final", datafinal))

df = df[(df["OrdemData"] >= data1) & (df["OrdemData"] <= data2)].copy()

st.sidebar.header("Filtros")

region = st.sidebar.multiselect(
    "Escolha sua Região",
    options=df["Region"].unique()
)

if region:
    df = df[df["Region"].isin(region)]

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

estado = st.sidebar.multiselect(
    "Escolha seu Estado",
    options=df2["State"].unique()
)

if not estado:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(estado)]

cidade = st.sidebar.multiselect("Escolha a cidade", df3["City"].unique())

if not region and not estado and not cidade:
    filtradodf = df
elif not estado and not cidade:
    filtradodf = df[df["Region"].isin(region)]
elif not region and not estado:
    filtradodf = df[df["State"].isin(estado)]
elif estado and cidade:
    filtradodf = df3[df3["State"].isin(estado) & df3["City"].isin(cidade)]
elif cidade:
    filtradodf = df3[df3["City"].isin(cidade)]
else:
    filtradodf = df3.copy()

categoriadf = filtradodf.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Categoria baseada em Vendas")
    fig = px.bar(
        categoriadf,
        x="Category",
        y="Sales",
        text=["${:,.2f}".format(x) for x in categoriadf["Sales"]],
        template="seaborn"
    )
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Vendas baseadas por região")
    fig = px.pie(filtradodf, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtradodf["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1: 
    with st.expander("Category_ViewData"):
        max_value = categoriadf["Sales"].max()
        styled_df = categoriadf.style.applymap(
            lambda v: f"background-color: rgba(0, 0, 255, {v / max_value:.2f})",
            subset=["Sales"]
        )
        st.write(styled_df)

        csv = categoriadf.to_csv(index=False).encode('utf-8')
        st.download_button("Download dos Dados", data=csv, file_name="Category.csv", mime="text/csv")

with cl2: 
    with st.expander("Region_ViewData"):
        regiao_df = filtradodf.groupby(by="Region", as_index=False)["Sales"].sum()
        max_region = regiao_df["Sales"].max()
        styled_region = regiao_df.style.applymap(
            lambda v: f"background-color: rgba(255, 165, 0, {v / max_region:.2f})",
            subset=["Sales"]
        )
        st.write(styled_region)

        csv = regiao_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

# Séries temporais
filtradodf["month_year"] = filtradodf["OrdemData"].dt.to_period("M").dt.to_timestamp()
st.subheader("Séries Temporais")

linechart = filtradodf.groupby("month_year")["Sales"].sum().reset_index()
fig2 = px.line(
    linechart,
    x="month_year",
    y="Sales",
    labels={"Sales": "Quantidade", "month_year": "Mês/Ano"},
    height=500,
    width=1000,
    template="plotly_white"
)
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Visualização de data das séries temporais"):
    st.write(
        linechart.T.style.set_properties(
            **{'border': '1px solid #ddd', 'text-align': 'center'}
        )
    )

    csv = linechart.to_csv(index=False).encode("utf-8")

    st.download_button(
        label='Download Data',
        data=csv,
        file_name="SeriesTemporais.csv",
        mime='text/csv'
    )
#Criar a tremap baseada em região, categoria e sub-categoria
st.subheader("Visão hierarquica de Vendas usando Treemap")
fig3 = px.treemap(filtradodf, path= ["Region", "Category", "Sub-Category"], values = "Sales", hover_data = ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width= True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Vendas segmentadas')
    fig = px.pie(filtradodf, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filtradodf["Segment"], textposition = "inside")
    st.plotly_chart(fig,use_container_width = True)

with chart2:
    st.subheader('Vendas por categoria')
    fig = px.pie(filtradodf, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filtradodf["Category"], textposition = "inside")
    st.plotly_chart(fig,use_container_width = True)

import plotly.figure_factory as ff
st.subheader(":point_right: Resumo de Vendas de Subcategorias por Mês")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale= "Cividis")
    st.plotly_chart(fig, use_container_width= True)

    st.markdown("Tabela de subcategorias por mês")
    filtradodf ["month"] = filtradodf["OrdemData"].dt.month_name()
    subcategoria_ano = pd.pivot_table(data = filtradodf, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(subcategoria_ano)

data1 = px.scatter(filtradodf, x="Sales", y="Profit", size="Quantity")


data1.update_layout(
    title=dict(
        text="Relações entre Vendas e Lucros utilizando do gráfico de Dispersão",
        font=dict(size=20)
    ),
    xaxis=dict(
        title=dict(text="Vendas", font=dict(size=19))
    ),
    yaxis=dict(
        title=dict(text="Lucro", font=dict(size=19))
    )
)

st.plotly_chart(data1, use_container_width=True)