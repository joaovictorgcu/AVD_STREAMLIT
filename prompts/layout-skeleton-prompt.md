# Template: rascunho de layout → esqueleto do app

Preencha cada bloco e envie à ferramenta de IA.

## Contexto

Sou aluno da disciplina de Análise e Visualização de Dados (CESAR School, 2026.2) e estou construindo um app em
Streamlit a partir da minha EDA da Aula 11 sobre o clima de Brasília (INMET, estação automática A001, dados
horários de 2014 a 2023). O dado tratado está em `data/clean/dataset.csv` (87.579 linhas, hora local UTC−3) com
`temperatura` (°C), `umidade` (%), `precipitacao` (mm), `ponto_orvalho` (°C) e as colunas de calendário `ano`,
`mes`, `hora`, `data`, `estacao` e `periodo` (seco mai–set / chuvoso out–abr).

O app tem duas abas (`st.tabs`):

- **Dashboard 1 — Laboratório de distribuição e correlação:** heatmap de correlação e histogramas das variáveis
  quantitativas, em granularidade horária ou diária (resumos do dia: máxima, mínima, amplitude, umidade mínima,
  chuva do dia).
- **Dashboard 2 — Painel do tempo seco:** KPIs de umidade baixa para vigilância em saúde e Defesa Civil do DF.

## Entrada

Rascunhos anexados: `entregas/rascunho-dashboard1.png` e `entregas/rascunho-dashboard2.png` (descrição de cada
elemento em `entregas/rascunhos.md`).

- **Dashboard 1:** sidebar com granularidade, `st.multiselect` de variáveis, slider de anos, `st.pills` de
  estações, `st.selectbox` + `st.slider` de intervalo para excluir valores, método da correlação e opções do
  histograma; na área principal, uma faixa de `st.metric` de contexto, heatmap + leitura rápida lado a lado,
  grade de histogramas, tabela de estatísticas e uma seção de comparação X × Y.
- **Dashboard 2:** sidebar com "Ano em foco" e "Meses considerados"; 5 `st.metric` (dias secos/ano, dias em
  alerta/ano, horas de ar seco, maior estiagem, hora mais seca) e 4 gráficos (mapa mês × hora, dias por nível em
  cada mês, série anual e ciclo diário).

## Restrições

- Usar `streamlit` e `altair` (`st.altair_chart`); nada de bibliotecas extras além de pandas/numpy.
- Carregar o dado só por `src/data_loader.py`, com `@st.cache_data`, e por caminho relativo.
- Agregar no pandas antes de mandar para o Altair (não passar as 87 mil linhas para os gráficos).
- Tratar os cenários de borda: 0, 1 e 2+ variáveis; filtro sem registros; variável constante no recorte.
- Números no padrão brasileiro (vírgula decimal) e horários em hora local.

## Formato de saída

Código do `app.py` só com a estrutura das abas, e um módulo por dashboard em `src/` (`dashboard1.py`,
`dashboard2.py`), com as contas separadas em funções sem Streamlit para eu conseguir testar. Comentários curtos em
cada bloco para eu ajustar as métricas e os gráficos manualmente.
