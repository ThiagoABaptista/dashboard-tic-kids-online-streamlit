import streamlit as st
import pandas as pd
import altair as alt

# Configuração da página
st.set_page_config(page_title="Observatório Airbnb RJ", layout="wide")
st.title("Análise Exploratória: Airbnb no Rio de Janeiro")
st.write("Dashboard desenvolvido para a Prova Final UFRGS - Observatório de Turismo.")

# Carregamento de dados com cache para otimizar a performance
@st.cache_data
def carregar_dados():
    df = pd.read_csv('listings.csv')
    return df

df = carregar_dados()

# Sidebar para filtros interativos
st.sidebar.header("Filtros do Dashboard")
preco_max = st.sidebar.slider("Preço Máximo Diária (R$)", min_value=100, max_value=5000, value=2500, step=100)
noites_max = st.sidebar.slider("Máximo de Noites Mínimas", min_value=1, max_value=30, value=30, step=1)

# Aplicar filtros
df_filtrado = df[(df['price'] <= preco_max) & (df['minimum_nights'] <= noites_max)]

# Layout em colunas
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Distribuição Espacial e Preços")
    # Mapa
    mapa = alt.Chart(df_filtrado).mark_circle(size=12).encode(
        x=alt.X('longitude:Q', scale=alt.Scale(zero=False), title='Longitude'),
        y=alt.Y('latitude:Q', scale=alt.Scale(zero=False), title='Latitude'),
        color=alt.Color('price:Q', scale=alt.Scale(scheme='yelloworangered'), title='Preço (R$)'),
        opacity=alt.value(0.5),
        tooltip=['name', 'neighbourhood', 'price', 'room_type']
    ).properties(height=500).interactive()
    st.altair_chart(mapa, use_container_width=True)

with col2:
    st.subheader("Análise por Tipo de Quarto")
    
    # Boxplot
    boxplot = alt.Chart(df_filtrado).mark_boxplot(extent='min-max').encode(
        x=alt.X('room_type:N', title='Tipo de Quarto'),
        y=alt.Y('price:Q', title='Preço (R$)'),
        color=alt.Color('room_type:N', legend=None)
    ).properties(height=230)
    st.altair_chart(boxplot, use_container_width=True)
    
    # Gráfico de Barras (Média de Noites)
    barras = alt.Chart(df_filtrado).mark_bar().encode(
        x=alt.X('room_type:N', title='Tipo de Quarto'),
        y=alt.Y('mean(minimum_nights):Q', title='Média de Noites Mínimas'),
        color=alt.Color('room_type:N', legend=None),
        tooltip=['room_type', 'mean(minimum_nights)']
    ).properties(height=230)
    st.altair_chart(barras, use_container_width=True)

st.markdown("---")
st.markdown("**Fonte dos Dados:** Inside Airbnb, coleta de 24 de junho de 2026.")