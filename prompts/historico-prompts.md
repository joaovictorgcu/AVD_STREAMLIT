# Prompts por etapa do trabalho

> **Sobre este arquivo.** É uma sequência de prompts organizada por etapa, escrita em primeira pessoa para registrar
> como a IA foi usada como apoio em cada fase. Ela **não é a transcrição literal** de conversas: o desenvolvimento
> foi feito com o Claude Code a partir de um pedido único e abrangente, que está copiado na íntegra em
> [declaracao-uso-ia.md](declaracao-uso-ia.md). Cada prompt abaixo corresponde a uma parte que existe de fato no
> repositório (indicada em "Resultado no repositório").

## 1. Exploração inicial do dataset

> Estou começando a atividade de Streamlit da disciplina de AVD e vou usar o mesmo dataset da minha EDA da Aula 11:
> dados horários da estação A001 do INMET em Brasília, de 2014 a 2023, com temperatura, umidade relativa e
> precipitação. Me ajude a revisar o notebook original e listar o que ele já mostra (tratamentos, distribuições,
> correlações) e o que ainda falta para eu montar dois dashboards. Não quero alterar a análise original, só
> entender o ponto de partida.

**Resultado no repositório:** `notebooks/eda.ipynb` mantido como foi entregue.

## 2. Aprofundando a EDA para o app

> Na EDA eu vi que o pico de temperatura aparecia às 17h–18h. Os arquivos do INMET vêm em UTC? Se vierem, como
> converto para a hora de Brasília sem bagunçar o período de 2014 a 2023? Também quero criar uma separação entre
> período seco e chuvoso e uma variável derivada que ajude a separar "ar seco" de "ar quente". Explique a fórmula
> antes de eu implementar e me diga como conferir se os números continuam batendo com a EDA original.

**Resultado no repositório:** `notebooks/eda-com-downloads.ipynb` (conferência com a EDA, hora local, período
seco/chuvoso, ponto de orvalho pela fórmula de Magnus e exportação de `data/clean/dataset.csv`).

## 3. Variáveis e correlações

> Quais variáveis quantitativas fazem sentido no laboratório de correlação? Estou pensando em usar as horárias e
> também resumos por dia (máxima, mínima, amplitude, umidade mínima, chuva do dia). A chuva quase sempre é zero:
> isso atrapalha a correlação de Pearson? Vale oferecer Spearman também? E o que fazer com a regra do IQR, que na
> EDA marcava toda hora com chuva como outlier?

**Resultado no repositório:** `src/variaveis.py`, `src/estatisticas.py` e o aviso de IQR nulo na tabela do
Dashboard 1.

## 4. Planejamento do Dashboard 1

> Vou desenhar o rascunho do Dashboard 1 antes de codar. Os requisitos são: heatmap de correlação, histograma de
> cada variável avaliada, seletor de variáveis e slider de intervalo na barra lateral. Me ajude a organizar a
> página em blocos com uma finalidade clara para cada um e a pensar nos casos de borda (nenhuma variável, só uma,
> filtro sem registros, variável constante).

**Resultado no repositório:** `entregas/rascunho-dashboard1.png` e a primeira parte de `entregas/rascunhos.md`.

## 5. Público-alvo do Dashboard 2

> Para o segundo dashboard preciso escolher um público específico. Com temperatura, umidade e chuva de Brasília,
> pensei em equipes de vigilância em saúde e Defesa Civil do DF, por causa do tempo seco. Isso se sustenta com o
> que a EDA mostrou? Quais perguntas esse público precisa responder e quais faixas de umidade baixa são usadas
> oficialmente para atenção, alerta e emergência?

**Resultado no repositório:** seção "Público-alvo e por que ele" em `entregas/justificativa-metricas.md`.

## 6. KPIs

> Quero de 3 a 5 KPIs para esse público, com nome, unidade e fórmula claros, sem inventar nada que o dataset não
> permita calcular. Minha ideia: dias com umidade mínima ≤ 30%, dias em alerta, fração das horas com ar seco,
> maior sequência de dias sem chuva e a hora mais seca do dia. Como comparo um ano com a média dos outros de forma
> justa? E como tratar dias com poucas horas medidas?

**Resultado no repositório:** `src/indicadores.py` e as cinco métricas de `entregas/justificativa-metricas.md`.

## 7. Implementação no Streamlit

> A partir dos dois rascunhos, me ajude a montar o `app.py` com `st.tabs` e um módulo por dashboard em `src/`.
> Gráficos em Altair, dados agregados no pandas antes de ir para o gráfico e cache com `@st.cache_data`. No
> Dashboard 2 quero os KPIs com `st.metric`, comparação com a média 2014–2023 e quatro gráficos: mapa mês × hora,
> dias por nível em cada mês, série anual e ciclo diário.

**Resultado no repositório:** `app.py`, `src/data_loader.py`, `src/dashboard1.py`, `src/dashboard2.py`.

## 8. Revisão visual e de usabilidade

> Rodei o app e alguns pontos me incomodaram: os histogramas não mostram as barras, os rótulos do heatmap se
> sobrepõem no celular, os nomes dos KPIs estão cortados e a umidade aparece com um efeito de "pente". Me ajude a
> corrigir isso e a definir um tema claro/escuro consistente no `config.toml`, com cor de destaque só para o que é
> risco.

**Resultado no repositório:** commit `style:` (tema em `.streamlit/config.toml`, ajustes nos gráficos e nos KPIs).

## 9. Testes e correção de problemas

> Quero testar o app de verdade, não só ver se abre. Como uso o `streamlit.testing` para simular os widgets (0 e 1
> variável, intervalo de um único valor, nenhuma estação, cada ano em foco)? Também quero conferir as fórmulas dos
> KPIs com contas feitas à mão e garantir que o `requirements.txt` funciona num ambiente limpo.

**Resultado no repositório:** pasta `tests/` e a inclusão do `scipy` no `requirements.txt` (sem ele a correlação de
Spearman falhava num ambiente novo).

## 10. Revisão final dos entregáveis

> Confira comigo se o repositório atende ao roteiro das Aulas 21 a 23: notebooks, `app.py`, `entregas/` com os
> dois rascunhos e a justificativa, `prompts/`, `README.md` com o link do app e `requirements.txt`. Revise também
> se não há dado sensível versionado e se o app publicado é a versão mais recente.

**Resultado no repositório:** `README.md` e o checklist de publicação.
