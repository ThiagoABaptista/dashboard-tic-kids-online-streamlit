# Dashboard Interativo — TIC Kids Online Brasil (Trabalho Final — IA001)

Este repositório contém o dashboard interativo desenvolvido com **Streamlit** para o Trabalho Final da disciplina IA001 — Análise e Visualização de Dados com Python e Ferramentas Assistidas por IA.

O projeto investiga o uso de **redes sociais, mensagens instantâneas e chamadas de vídeo** por crianças e adolescentes brasileiros de 9 a 17 anos usuários de internet, com base nos dados oficiais da pesquisa **TIC Kids Online Brasil** (Cetic.br/NIC.br).

---

## Estrutura do Projeto

```text
atividade02/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── tic_kids_online_b1b_final.csv
└── atividade02_dashboard_streamlit.ipynb
```

- `app.py`: código principal da aplicação Streamlit.
- `data/tic_kids_online_b1b_final.csv`: conjunto de dados utilizado no dashboard, organizado a partir dos indicadores B1B da pesquisa.
- `requirements.txt`: dependências e bibliotecas Python necessárias para executar a aplicação.
- `README.md`: documentação e instruções de execução do projeto.
- `atividade02_dashboard_streamlit.ipynb`: notebook com a análise exploratória e preparação dos dados.

---

## Fonte dos Dados e Download

Os dados utilizados são provenientes da pesquisa **TIC Kids Online Brasil**, disponibilizada pelo Cetic.br/NIC.br. 

O recorte contempla as edições de **2017, 2018, 2019, 2021, 2022, 2023, 2024 e 2025** (a edição de 2020 não foi realizada no recorte utilizado).

- **Download da Base do Projeto:** Caso necessite baixar o arquivo CSV tratado diretamente da internet, utilize o link: [Base de Dados `tic_kids_online_b1b_final.csv` no GitHub Gist](https://gist.github.com/ThiagoABaptista/4877d0168e99700078060f59b75e3842).
- **Página Oficial:** [TIC Kids Online Brasil — Cetic.br](https://cetic.br/pesquisa/kids-online/)
- **Microdados:** [Página de microdados oficiais](https://cetic.br/pesquisa/kids-online/microdados/)

---

## Perguntas Investigadas

O dashboard analisa quatro perguntas centrais sobre o comportamento digital dos jovens brasileiros:

1. **Evolução Geral:** Quais formas de comunicação digital são mais usadas por crianças e adolescentes de 9 a 17 anos no Brasil e como seus percentuais variaram entre as edições da pesquisa?
2. **Faixa Etária:** O percentual de uso difere entre as faixas etárias e a distância entre a faixa mais nova (9 a 10 anos) e a mais velha (15 a 17 anos) mudou ao longo do tempo?
3. **Perfil Demográfico e Área:** Há diferença no uso entre meninos e meninas e entre áreas urbanas e rurais, e essa diferença se manteve ao longo das edições?
4. **Disparidades Regionais:** Quais regiões apresentam os maiores e menores percentuais de uso e como a posição das regiões oscilou ao longo do período?

---

## Visualizações do Dashboard

A aplicação combina **Plotly** e **Altair** para oferecer gráficos interativos com suporte a temas dinâmicos (Light/Dark Mode):

- **Cartões de Indicadores Resumidos:** Destaque dos valores mais recentes (2025) e suas variações em pontos percentuais (p.p.) desde 2017.
- **Gráfico de Linhas (Plotly):** Evolução histórica do total do Brasil por indicador.
- **Gráfico de Barras Agrupadas (Altair):** Comparação entre as formas de comunicação selecionáveis por grupo.
- **Gráfico por Faixa Etária (Plotly):** Trajetória comparativa entre as 4 faixas etárias.
- **Gráfico de Halteres / Dumbbell Chart (Altair):** Comparação direta entre recortes (Masculino x Feminino e Urbana x Rural) com marcação de diferença.
- **Ranking Regional e Mapa de Calor / Heatmap (Altair):** Ranking comparativo por edição com linha de referência do Total Brasil e matriz de evolução histórica das 5 regiões.

---

## Controles Interativos

Na barra lateral e ao longo das seções, o usuário pode:
- **Filtrar o período temporal:** ajustar o intervalo de edições (2017 a 2025).
- **Selecionar a métrica:** alternar entre *Redes sociais*, *Mensagens instantâneas* ou *Chamadas de vídeo*.
- **Alternar recortes demográficos:** escolher entre o perfil por Sexo (*Masculino/Feminino*) ou por Área (*Urbana/Rural*).
- **Filtrar a edição do ranking regional:** selecionar um ano específico para analisar as posições das regiões frente ao total nacional.

---

## Como Executar o Dashboard

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.10 ou superior** instalado.

### 2. Obter o Repositório
Clone ou baixe o repositório em sua máquina e navegue até a pasta raiz do projeto.

### 3. Criar o Ambiente Virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux ou macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instalar as Dependências
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Executar a Aplicação
No terminal, na raiz do projeto, execute:
```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no seu navegador padrão no endereço `http://localhost:8501`.

---

## Limitações da Análise

- A base de referência contempla apenas crianças e adolescentes que são **usuários de internet** de 9 a 17 anos (não a população total nessa faixa etária).
- Os dados são agregados e declaratórios, sem disponibilização de margens de erro no arquivo utilizado.
- A edição da pesquisa de 2020 não está presente no conjunto de dados.
- As análises têm caráter descritivo e exploratório, não sendo possível inferir relações causais.

---

## Integrantes

- **Thiago Aschebrock Baptista**

**Disciplina:** IA001 — Análise e Visualização de Dados com Python e Ferramentas Assistidas por IA.  
**Atividade:** Trabalho Final.