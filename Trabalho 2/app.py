from pathlib import Path

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Configuração
st.set_page_config(
    page_title="TIC Kids Online Brasil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. Carregamento e validação dos dados
@st.cache_data
def load_data():
    """Carrega o CSV da pasta data, localizada ao lado deste arquivo."""
    file_path = Path(__file__).resolve().parent / "data" / "tic_kids_online_b1b_final.csv"

    try:
        data = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Arquivo de dados não encontrado: {file_path}")
        st.stop()

    required_columns = {
        "ano", "linha", "metrica", "valor_verificado", "fonte"
    }
    missing = required_columns.difference(data.columns)
    if missing:
        st.error(
            "O CSV não possui todas as colunas esperadas. "
            f"Colunas ausentes: {', '.join(sorted(missing))}"
        )
        st.stop()

    data["ano"] = pd.to_numeric(data["ano"], errors="coerce")
    data["valor_verificado"] = pd.to_numeric(
        data["valor_verificado"], errors="coerce"
    )
    data = data.dropna(subset=["ano", "valor_verificado"]).copy()
    data["ano"] = data["ano"].astype(int)
    data["linha"] = data["linha"].astype(str).str.strip()
    data["metrica"] = data["metrica"].astype(str).str.strip()
    return data


df = load_data()

# 3. Rótulos e grupos
METRICAS = {
    "redes_sociais_sim": "Redes sociais",
    "mensagens_instantaneas_sim": "Mensagens instantâneas",
    "chamada_video_sim": "Chamadas de vídeo",
}
COR_METRICA = {
    "Redes sociais": "#1f77b4",
    "Mensagens instantâneas": "#ff7f0e",
    "Chamadas de vídeo": "#2ca02c",
}
FAIXAS_ETARIAS = [
    "De 9 a 10 anos",
    "De 11 a 12 anos",
    "De 13 a 14 anos",
    "De 15 a 17 anos",
]
REGIOES = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

GRUPOS_BARRAS = (
    ["TOTAL"] + FAIXAS_ETARIAS + ["Masculino", "Feminino"]
    + ["Urbana", "Rural"] + REGIOES
)

ANOS_DISPONIVEIS = sorted(df["ano"].unique())

if not ANOS_DISPONIVEIS:
    st.error("O arquivo não contém anos válidos para análise.")
    st.stop()


# 4. Controles interativos
st.sidebar.header("Filtros")
st.sidebar.markdown(
    "Explore as diferenças entre grupos e a evolução dos "
    "indicadores ao longo das edições."
)
periodo = st.sidebar.select_slider(
    "Período da pesquisa",
    options=ANOS_DISPONIVEIS,
    value=(ANOS_DISPONIVEIS[0], ANOS_DISPONIVEIS[-1]),
)
metrica_selecionada = st.sidebar.selectbox(
    "Métrica (seções 2, 3 e 4)",
    options=list(METRICAS.keys()),
    format_func=lambda item: METRICAS[item],
)

# 5. Filtro temporal
ano_inicial, ano_final = periodo
df_periodo = df[
    (df["ano"] >= ano_inicial) & (df["ano"] <= ano_final)
].copy()
df_total = df_periodo[df_periodo["linha"] == "TOTAL"].copy()
anos_periodo = [a for a in ANOS_DISPONIVEIS if ano_inicial <= a <= ano_final]
nome_metrica = METRICAS[metrica_selecionada].lower()


# 6. Funções auxiliares
def resumo_diferenca(grupo_a, grupo_b):
    """Texto-resumo da diferença (em p.p.) entre dois grupos no período."""
    dados = df_periodo[
        (df_periodo["metrica"] == metrica_selecionada)
        & (df_periodo["linha"].isin([grupo_a, grupo_b]))
    ]
    largo = dados.pivot_table(
        index="ano", columns="linha", values="valor_verificado"
    )
    if not {grupo_a, grupo_b}.issubset(largo.columns):
        return None
    largo = largo.dropna(subset=[grupo_a, grupo_b])
    if largo.empty:
        return None

    dif = largo[grupo_a] - largo[grupo_b]
    primeiro, ultimo = dif.index[0], dif.index[-1]
    texto = (
        f"Em {primeiro}, {grupo_a} registrou {largo.loc[primeiro, grupo_a]:.0f}% "
        f"e {grupo_b} {largo.loc[primeiro, grupo_b]:.0f}% "
        f"(diferença de {dif[primeiro]:+.0f} p.p.)."
    )
    if primeiro != ultimo:
        ano_max = dif.abs().idxmax()
        texto += (
            f" Em {ultimo}, a diferença foi de {dif[ultimo]:+.0f} p.p. "
            f"A maior diferença do período ocorreu em {ano_max} "
            f"({dif[ano_max]:+.0f} p.p.)."
        )
    return texto


def mostrar_comparacao(grupo_a, grupo_b):
    """Dumbbell (Altair): dois grupos por edição, com segmento entre eles."""
    dados = df_periodo[
        (df_periodo["metrica"] == metrica_selecionada)
        & (df_periodo["linha"].isin([grupo_a, grupo_b]))
    ].copy()
    largo = dados.pivot_table(
        index="ano", columns="linha", values="valor_verificado"
    )
    if not {grupo_a, grupo_b}.issubset(largo.columns):
        st.warning("Não há dados para os grupos no período selecionado.")
        return
    largo = largo.dropna(subset=[grupo_a, grupo_b]).reset_index()
    if largo.empty:
        st.warning("Não há dados para os grupos no período selecionado.")
        return
    largo = largo.rename(columns={grupo_a: "valor_a", grupo_b: "valor_b"})

    # Com pontos (e não barras) o eixo pode ser recortado para destacar a diferença
    limite_inf = max(0, min(largo["valor_a"].min(), largo["valor_b"].min()) - 5)
    limite_sup = min(100, max(largo["valor_a"].max(), largo["valor_b"].max()) + 5)
    escala_x = alt.Scale(domain=[limite_inf, limite_sup])
    eixo_y = alt.Y(
        "ano:O", sort=anos_periodo, title="Edição da pesquisa",
        axis=alt.Axis(labelAngle=0),
    )

    segmento = (
        alt.Chart(largo)
        .mark_rule(color="#bbbbbb", strokeWidth=4)
        .encode(
            y=eixo_y,
            x=alt.X("valor_a:Q", scale=escala_x, title="Percentual (%)"),
            x2="valor_b:Q",
        )
    )
    pontos = (
        alt.Chart(dados)
        .mark_point(filled=True, size=140, opacity=1)
        .encode(
            y=eixo_y,
            x=alt.X("valor_verificado:Q", scale=escala_x),
            color=alt.Color(
                "linha:N",
                title="Grupo",
                scale=alt.Scale(
                    domain=[grupo_a, grupo_b], range=["#6a3d9a", "#17becf"]
                ),
            ),
            tooltip=[
                alt.Tooltip("ano:O", title="Edição"),
                alt.Tooltip("linha:N", title="Grupo"),
                alt.Tooltip("valor_verificado:Q", title="Percentual", format=".0f"),
            ],
        )
    )
    st.altair_chart(
        (segmento + pontos).properties(
            title=alt.TitleParams(
                f"Uso de {nome_metrica} — {grupo_a} e {grupo_b}",
                subtitle=(
                    "O segmento cinza mostra a diferença entre os grupos em "
                    "cada edição. O eixo não começa em zero."
                ),
            ),
            height=38 * len(largo) + 50,
        ),
        use_container_width=True,
        theme="streamlit",
    )

    resumo = resumo_diferenca(grupo_a, grupo_b) or ""
    st.caption(
        f"Interpretação: {resumo} Valores positivos indicam percentual maior "
        f"para {grupo_a}; negativos, para {grupo_b} (p.p. = pontos "
        "percentuais). Diferenças de poucos pontos podem estar dentro da "
        "margem de erro da pesquisa, que não consta no arquivo."
    )


# 7. Apresentação
st.title("TIC Kids Online Brasil: Comunicação Digital entre Crianças e Adolescentes")
st.markdown(
    """
Este dashboard explora dados da **TIC Kids Online Brasil**, com foco no
uso de **redes sociais, mensagens instantâneas e chamadas de vídeo**
por crianças e adolescentes de 9 a 17 anos usuários de internet.
"""
)

with st.expander("📖 Glossário", expanded=False):
    st.markdown(
        """
**Usuários de internet de 9 a 17 anos.** Base de todos os percentuais do
dashboard: crianças e adolescentes dessa faixa etária que usaram a internet
no período de referência da pesquisa. Quem não usa a internet não está na base.

**Redes sociais.** Plataformas em que a pessoa mantém um perfil e interage
com conteúdos e outras pessoas. Exemplos: Instagram, TikTok, Facebook.

**Mensagens instantâneas.** Troca de mensagens de texto, áudio ou imagem
entre pessoas ou grupos. Exemplos: WhatsApp, Telegram.

**Chamadas de vídeo.** Conversas por vídeo em tempo real. Exemplos: Google
Meet, Zoom, chamada de vídeo do WhatsApp.

**Percentual de uso.** Proporção da base que respondeu "sim" à atividade:
usou redes sociais, enviou mensagens instantâneas ou conversou por chamada de
vídeo.

**Ponto percentual (p.p.).** Diferença entre dois percentuais. Se um grupo
passa de 60% para 65%, a variação é de 5 p.p.

**Observação.** As definições e os exemplos acima são explicativos e não
substituem a redação oficial do questionário. Um mesmo aplicativo pode se
encaixar em mais de uma forma de comunicação, e a pesquisa registra o que o
respondente declara ter feito.
"""
    )

st.markdown(
    """
A análise busca responder as seguintes perguntas (nas perguntas 2 a 4, a
"forma de comunicação selecionada" é a escolhida no filtro **Métrica** da
barra lateral):

1. **Quais formas de comunicação digital são mais usadas por crianças e
   adolescentes de 9 a 17 anos usuários de internet no Brasil, e como seus
   percentuais variaram entre as edições da pesquisa?**
2. **O percentual de uso da forma de comunicação selecionada difere entre as
   faixas etárias, e a distância entre a faixa mais nova e a mais velha mudou
   ao longo das edições?**
3. **Há diferença no percentual de uso da forma de comunicação selecionada
   entre meninos e meninas e entre áreas urbanas e rurais, e essa diferença se
   manteve ao longo das edições?**
4. **Quais regiões têm os maiores e os menores percentuais de uso da forma de
   comunicação selecionada, e essa ordem se manteve ao longo das edições?**
"""
)
anos_texto = ", ".join(str(int(ano)) for ano in ANOS_DISPONIVEIS)
st.info(
    f"Os percentuais se referem a usuários de internet de 9 a 17 anos. "
    f"As edições disponíveis são: {anos_texto}. "
    "A edição de 2020 não está presente no recorte utilizado."
)

# 8. Indicadores resumidos
st.subheader("Indicadores resumidos")
st.caption(
    "Os cartões mostram o percentual da última edição do período "
    "selecionado, no total de usuários de internet de 9 a 17 anos, e a variação em "
    "pontos percentuais (p.p.) desde a primeira edição do período."
)
col1, col2, col3 = st.columns(3)


def mostrar_ultimo(container, metrica, titulo):
    serie = (
        df_total[df_total["metrica"] == metrica]
        .sort_values("ano")[["ano", "valor_verificado"]]
    )
    if serie.empty:
        container.metric(titulo, "—")
        return
    primeiro, ultimo = serie.iloc[0], serie.iloc[-1]
    delta = None
    if len(serie) > 1:
        variacao = ultimo["valor_verificado"] - primeiro["valor_verificado"]
        delta = f"{variacao:+.0f} p.p. desde {int(primeiro['ano'])}"
    container.metric(
        f"{titulo} — {int(ultimo['ano'])}",
        f"{ultimo['valor_verificado']:.0f}%",
        delta=delta,
        delta_color="off",
    )


mostrar_ultimo(col1, "redes_sociais_sim", "Redes sociais")
mostrar_ultimo(col2, "mensagens_instantaneas_sim", "Mensagens instantâneas")
mostrar_ultimo(col3, "chamada_video_sim", "Chamadas de vídeo")
st.markdown("---")

# 9. Pergunta 1 — evolução no total (Plotly) e por grupo (Altair)
st.subheader("1. Formas de comunicação mais usadas e sua evolução")
st.markdown(
    "Percentual observado no total de usuários de internet de 9 a 17 anos, "
    "por edição da pesquisa."
)
dados_q1 = df_total[
    df_total["metrica"].isin(METRICAS.keys())
].copy()
dados_q1["metrica_label"] = dados_q1["metrica"].map(METRICAS)

if dados_q1.empty:
    st.warning("Não há dados do grupo TOTAL para o período selecionado.")
else:
    fig1 = px.line(
        dados_q1,
        x="ano",
        y="valor_verificado",
        color="metrica_label",
        markers=True,
        color_discrete_map=COR_METRICA,
        labels={
            "ano": "Edição da pesquisa",
            "valor_verificado": "Percentual (%)",
            "metrica_label": "Indicador",
        },
        title="Evolução do percentual de uso — Brasil, usuários de internet de 9 a 17 anos",
    )
    fig1.update_yaxes(range=[0, 100], title="Percentual (%)")
    fig1.update_xaxes(tickmode="array", tickvals=anos_periodo)
    fig1.update_layout(hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)
    ordem = dados_q1.pivot_table(
        index="ano", columns="metrica_label", values="valor_verificado"
    ).idxmax(axis=1)
    if ordem.nunique() == 1:
        texto_ordem = (
            f"{ordem.iloc[0]} foi a forma mais usada em todas as edições "
            "do período."
        )
    else:
        texto_ordem = (
            "A forma mais usada mudou entre as edições: "
            + "; ".join(f"{ano}: {nome}" for ano, nome in ordem.items())
            + "."
        )
    st.caption(
        "Interpretação: os indicadores oscilam ao longo das edições, sem "
        "necessariamente seguir uma trajetória contínua de crescimento ou "
        f"redução. {texto_ordem}"
    )


st.markdown("**Comparação das formas de comunicação em cada edição**")
st.markdown(
    "As barras agrupadas comparam, em cada edição, os percentuais de uso "
    "das três formas de comunicação. Selecione um grupo para ver sua "
    "evolução; evite comparar diretamente grupos diferentes."
)
grupo_barras = st.selectbox(
    "Grupo para o gráfico de barras",
    options=GRUPOS_BARRAS,
    index=GRUPOS_BARRAS.index("De 9 a 10 anos"),
    key="grupo_barras_comunicacao",
)
dados_barras = df_periodo[
    (df_periodo["linha"] == grupo_barras)
    & (df_periodo["metrica"].isin(METRICAS.keys()))
].copy()
dados_barras["metrica_label"] = dados_barras["metrica"].map(METRICAS)

if dados_barras.empty:
    st.warning("Não há dados para o grupo selecionado no período escolhido.")
else:
    selecao_forma = alt.selection_point(
        fields=["metrica_label"], bind="legend"
    )
    chart_barras = (
        alt.Chart(dados_barras)
        .mark_bar()
        .encode(
            x=alt.X("ano:O", title="Edição da pesquisa", sort=anos_periodo),
            xOffset=alt.XOffset(
                "metrica_label:N", sort=list(METRICAS.values())
            ),
            y=alt.Y(
                "valor_verificado:Q",
                title="Percentual de uso (%)",
                scale=alt.Scale(domain=[0, 100]),
            ),
            color=alt.Color(
                "metrica_label:N",
                title="Forma de comunicação (clique)",
                scale=alt.Scale(
                    domain=list(COR_METRICA.keys()),
                    range=list(COR_METRICA.values()),
                ),
            ),
            opacity=alt.condition(
                selecao_forma, alt.value(1), alt.value(0.2)
            ),
            tooltip=[
                alt.Tooltip("ano:O", title="Ano"),
                alt.Tooltip("metrica_label:N", title="Forma de comunicação"),
                alt.Tooltip("linha:N", title="Grupo"),
                alt.Tooltip("valor_verificado:Q", title="Percentual", format=".0f"),
            ],
        )
        .add_params(selecao_forma)
        .properties(
            title=alt.TitleParams(
                f"Formas de comunicação por ano — {grupo_barras}",
                subtitle=(
                    "Clique em uma forma na legenda para destacá-la "
                    "(Shift + clique seleciona mais de uma)."
                ),
            ),
            height=420,
        )
    )
    st.altair_chart(
        chart_barras, 
        use_container_width=True,
        theme="streamlit"
    )
    st.caption(
        "Interpretação: compare as formas de comunicação em cada edição, "
        "considerando o grupo selecionado. As barras ficam igualmente "
        "espaçadas, mas entre 2019 e 2021 o intervalo é maior, pois não há "
        "a edição de 2020."
    )

# 10. Pergunta 2 — faixas etárias
st.subheader(f"2. Uso de {nome_metrica} por faixa etária")
st.markdown(
    "Compare os percentuais entre as faixas etárias e observe como as "
    "diferenças se modificam ao longo das edições. Clique em uma faixa na "
    "legenda do gráfico para ocultá-la ou exibi-la; dê um duplo clique para "
    "isolá-la."
)
dados_q2 = df_periodo[
    (df_periodo["metrica"] == metrica_selecionada)
    & (df_periodo["linha"].isin(FAIXAS_ETARIAS))
].copy()
if dados_q2.empty:
    st.warning("Não há dados para as faixas etárias no período selecionado.")
else:
    fig2 = px.line(
        dados_q2,
        x="ano",
        y="valor_verificado",
        color="linha",
        markers=True,
        category_orders={"linha": FAIXAS_ETARIAS},
        labels={
            "ano": "Edição da pesquisa",
            "valor_verificado": "Percentual (%)",
            "linha": "Faixa etária",
        },
        title=f"Evolução do uso de {nome_metrica} por faixa etária",
    )
    fig2.update_yaxes(range=[0, 100], title="Percentual (%)")
    fig2.update_xaxes(tickmode="array", tickvals=anos_periodo)
    fig2.update_layout(hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)
    resumo_faixas = resumo_diferenca("De 15 a 17 anos", "De 9 a 10 anos")
    st.caption(
        "Interpretação: a visualização permite observar se as diferenças "
        "entre as faixas etárias se mantêm ou se modificam ao longo das "
        "edições. "
        + (f"Entre a faixa mais velha e a mais nova: {resumo_faixas} " if resumo_faixas else "")
        + "As variações não permitem, isoladamente, identificar os "
        "fatores que as explicam."
    )


# 11. Pergunta 3 — sexo e área
st.subheader(f"3. Uso de {nome_metrica} por sexo e por área")
st.markdown(
    "Compare meninos e meninas, ou áreas urbanas e rurais, ao longo das "
    "edições. Cada linha do gráfico é uma edição: quanto mais longo o "
    "segmento entre os pontos, maior a diferença entre os grupos."
)
recorte = st.radio(
    "Recorte de comparação",
    options=["Sexo", "Área"],
    horizontal=True,
    key="recorte_sexo_area",
)
if recorte == "Sexo":
    mostrar_comparacao("Masculino", "Feminino")
else:
    mostrar_comparacao("Urbana", "Rural")

# 12. Pergunta 4 — regiões: ranking com total Brasil e mapa de calor (Altair)
st.subheader(f"4. Ranking e evolução do uso de {nome_metrica} por região")
st.markdown(
    "O gráfico de barras compara o percentual de usuários de internet de "
    "9 a 17 anos que usam a forma de comunicação escolhida no filtro "
    "**Métrica** da barra lateral, em cada região. A linha tracejada indica "
    "o percentual do total do Brasil."
)

ano_regiao = st.selectbox(
    "Edição da pesquisa (gráfico de barras)",
    options=anos_periodo,
    index=len(anos_periodo) - 1,
    key="ano_regioes",
)

dados_regiao = df[
    (df["metrica"] == metrica_selecionada)
    & (df["ano"] == ano_regiao)
    & (df["linha"].isin(REGIOES))
][["linha", "valor_verificado"]].rename(
    columns={"linha": "Região", "valor_verificado": "Percentual (%)"}
)
total_brasil = df[
    (df["metrica"] == metrica_selecionada)
    & (df["ano"] == ano_regiao)
    & (df["linha"] == "TOTAL")
]["valor_verificado"]
total_brasil = float(total_brasil.iloc[0]) if not total_brasil.empty else None

if dados_regiao.empty:
    st.warning("Não há dados regionais para a edição selecionada.")
else:
    ordenado = dados_regiao.sort_values("Percentual (%)", ascending=False)
    base_rank = alt.Chart(ordenado).encode(
        x=alt.X(
            "Percentual (%):Q",
            scale=alt.Scale(domain=[0, 100]),
            title="Percentual (%)",
        ),
        y=alt.Y("Região:N", sort="-x", title=None),
    )
    if total_brasil is not None:
        # Cor com propósito: azul = acima do total Brasil; cinza = abaixo
        cor_rank = alt.condition(
            f"datum['Percentual (%)'] >= {total_brasil}",
            alt.value("#1f77b4"),
            alt.value("#9aa5b1"),
        )
        subtitulo_rank = (
            f"Linha tracejada = total Brasil ({total_brasil:.0f}%) · "
            "Azul = acima do total · Cinza = abaixo do total"
        )
    else:
        cor_rank = alt.value("#1f77b4")
        subtitulo_rank = "Total Brasil indisponível para esta edição."
    barras_rank = base_rank.mark_bar().encode(
        color=cor_rank,
        tooltip=["Região", alt.Tooltip("Percentual (%):Q", format=".0f")],
    )
    rotulos_rank = base_rank.mark_text(align="left", dx=4).encode(
        text=alt.Text("Percentual (%):Q", format=".0f")
    )
    camadas = barras_rank + rotulos_rank
    if total_brasil is not None:
        regua = (
            alt.Chart(pd.DataFrame({"total": [total_brasil]}))
            .mark_rule(color="firebrick", strokeDash=[6, 4], strokeWidth=2)
            .encode(
                x=alt.X("total:Q", scale=alt.Scale(domain=[0, 100])),
                tooltip=[
                    alt.Tooltip("total:Q", title="Total Brasil", format=".0f")
                ],
            )
        )
        camadas = camadas + regua
    st.altair_chart(
        camadas.properties(
            title=alt.TitleParams(
                f"Uso de {nome_metrica} por região — {ano_regiao}",
                subtitle=subtitulo_rank,
            ),
            height=300,
        ),
        use_container_width=True,
        theme="streamlit",
    )

    mais = ordenado.iloc[0]
    menos = ordenado.iloc[-1]
    st.caption(
        f"Interpretação: em {ano_regiao}, a região com maior percentual foi "
        f"{mais['Região']} ({mais['Percentual (%)']:.0f}%) e a com menor foi "
        f"{menos['Região']} ({menos['Percentual (%)']:.0f}%). As diferenças "
        "pequenas entre regiões podem estar dentro da margem de erro da "
        "pesquisa."
    )

st.markdown("**A posição das regiões muda ao longo das edições?**")
dados_hm = df_periodo[
    (df_periodo["metrica"] == metrica_selecionada)
    & (df_periodo["linha"].isin(REGIOES))
].copy()

if dados_hm.empty:
    st.warning("Não há dados regionais para o período selecionado.")
else:
    limite_inf = max(0, dados_hm["valor_verificado"].min() - 5)
    limite_sup = min(100, dados_hm["valor_verificado"].max() + 5)
    base_hm = alt.Chart(dados_hm).encode(
        x=alt.X(
            "ano:O",
            title="Edição da pesquisa",
            sort=anos_periodo,
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y(
            "linha:N", 
            sort=REGIOES, 
            title=None,
            axis=alt.Axis(labelOverlap=False)         
            ),
    )
    celulas_hm = base_hm.mark_rect().encode(
        color=alt.Color(
            "valor_verificado:Q",
            scale=alt.Scale(scheme="blues", domain=[limite_inf, limite_sup]),
            title="Percentual (%)",
        ),
        tooltip=[
            alt.Tooltip("linha:N", title="Região"),
            alt.Tooltip("ano:O", title="Edição"),
            alt.Tooltip("valor_verificado:Q", title="Percentual", format=".0f"),
        ],
    )
    numeros_hm = base_hm.mark_text(fontSize=13).encode(
        text=alt.Text("valor_verificado:Q", format=".0f"),
        color=alt.condition(
            alt.datum.valor_verificado > (limite_inf + limite_sup) / 2,
            alt.value("white"),
            alt.value("black"),
        ),
    )
    st.altair_chart(
        (celulas_hm + numeros_hm).properties(
            title=alt.TitleParams(
                f"Uso de {nome_metrica} por região e edição",
                subtitle="Cor mais escura = percentual maior.",
            ),
            height=320,
        ),
        use_container_width=True,
        theme="streamlit",
    )

    lider = dados_hm.loc[
        dados_hm.groupby("ano")["valor_verificado"].idxmax()
    ].set_index("ano")["linha"]
    if lider.nunique() == 1:
        texto_lider = (
            f"{lider.iloc[0]} teve o maior percentual em todas as edições "
            "do período."
        )
    else:
        texto_lider = (
            "A região com maior percentual mudou entre as edições: "
            + "; ".join(f"{ano}: {reg}" for ano, reg in lider.items())
            + "."
        )
    st.caption(
        f"Interpretação: {texto_lider} A escala de cores é a mesma em todas "
        "as células deste gráfico, mas se ajusta aos valores do período e da "
        "métrica selecionados. Entre 2019 e 2021 há um intervalo maior, pois "
        "não há a edição de 2020."
    )

# 13. Fonte e limitações
st.markdown("---")
st.subheader("Fonte dos dados")
st.markdown(
    """
**TIC Kids Online Brasil — Cetic.br/NIC.br.**

O recorte utilizado foi organizado a partir dos indicadores B1B das edições
**2017, 2018, 2019, 2021, 2022, 2023, 2024 e 2025**.

Os dados são agregados e estão organizados no arquivo
`tic_kids_online_b1b_final.csv`.

- [Página oficial da pesquisa](https://cetic.br/pesquisa/kids-online/)
- [Microdados da TIC Kids Online Brasil](https://cetic.br/pesquisa/kids-online/microdados/)
"""
)
st.subheader("Observações sobre a análise")
st.markdown(
    """
- Os percentuais têm como base os usuários de internet de 9 a 17 anos, e
  não todas as crianças e adolescentes dessa faixa etária.
- Os dados são percentuais agregados, sem margem de erro nem tamanho de
  amostra. Diferenças de poucos pontos percentuais entre grupos ou edições
  podem não ser conclusivas.
- O recorte não contém a edição de 2020, então o intervalo entre 2019 e 2021
  é maior que os demais.
- Os recortes disponíveis são total, faixa etária, sexo, área (urbana/rural)
  e região. Não é possível cruzá-los (por exemplo, sexo por região).
- Os dados regionais são agregados por região (Norte, Nordeste, Sudeste, Sul
  e Centro-Oeste), sem detalhamento por estado.
- Os indicadores se restringem a redes sociais, mensagens instantâneas e
  chamadas de vídeo.
- Os grupos se sobrepõem (um mesmo adolescente está em uma faixa etária, em
  um sexo, em uma área e em uma região). Por isso, os grupos não devem ser
  somados nem tratados como categorias excludentes.
- Os cartões de resumo comparam a primeira e a última edição do período
  selecionado. A variação é a diferença simples em pontos percentuais, sem
  margem de erro.
- O dashboard não permite inferir relações de causa e efeito. Diferenças
  entre grupos ou edições devem ser lidas como diferenças observadas nos
  indicadores.
"""
)
st.caption(
    "Fonte: Cetic.br/NIC.br — TIC Kids Online Brasil. "
    "Dashboard desenvolvido para a IA001 — Trabalho Final."
)