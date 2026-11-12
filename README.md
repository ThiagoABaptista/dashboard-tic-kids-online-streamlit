# Dashboard Exploratório — TIC Kids Online Brasil (2017–2025)

Aplicação web interativa desenvolvida em Python e Streamlit para explorar a evolução histórica dos hábitos de comunicação e uso de redes sociais por crianças e adolescentes brasileiros (9 a 17 anos), com base nos dados oficiais do **Cetic.br / NIC.br**.

🔗 **Acesse o Dashboard Online:** [Link do Streamlit Community Cloud]

---

## 🎯 Problema e Objetivo

Compreender como o comportamento digital infantojuvenil evoluiu no Brasil exige cruzar recortes demográficos e geográficos de forma dinâmica. Este projeto consolida séries históricas da pesquisa **TIC Kids Online Brasil** (indicador B1B) em painéis visuais interativos, permitindo filtrar tendências por região, área (urbana/rural), sexo e faixa etária.

* **Fonte dos Dados:** [Cetic.br — TIC Kids Online Brasil](https://cetic.br/pesquisa/kids-online/)
* **Recorte Analisado:** Série temporal de 2017 a 2025 sobre uso de redes sociais, mensagens instantâneas e chamadas de vídeo.

---

## 📊 Funcionalidades

* **Filtros Dinâmicos:** Segmentação interativa por ano, região geográfica, área de residência, sexo e faixa etária.
* **Análise Temporal:** Gráficos de evolução histórica comparando diferentes canais de comunicação digital.
* **Comparação Demográfica:** Visualização lado a lado das disparidades regionais e socioeconômicas no acesso digital.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.12+**
* **Streamlit:** Construção da interface web e controles interativos.
* **Pandas:** Limpeza, tratamento e agregação das séries históricas.
* **Plotly / Altair:** Geração de gráficos interativos responsivos.

---

## 🚀 Como Executar Localmente

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/ThiagoABaptista/dashboard-tic-kids-online-streamlit.git
   cd dashboard-tic-kids-online-streamlit
2. **Crie e ative um ambiente virtual:**
    ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
3. **Instale as dependências:**
    ```bash
   pip install -r requirements.txt
4. **Execute a aplicação:**
   ```bash
   streamlit run app.py
