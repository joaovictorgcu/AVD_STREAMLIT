# Justificativa das métricas — Dashboard 2 (Painel do tempo seco)

## Público-alvo e por que ele

**Equipes de vigilância em saúde ambiental e de Defesa Civil do Distrito Federal**, que planejam alertas de
tempo seco, campanhas de hidratação e orientações para escolas e serviços (por exemplo, suspender atividade física
ao ar livre nas horas mais secas).

A escolha saiu da própria EDA:

- o dataset só tem temperatura, umidade relativa e chuva de uma estação de Brasília — o recorte natural é o clima
  como risco para a população, não um uso comercial;
- a umidade é a variável que mais varia e que mais se relaciona com as outras: correlação de −0,68 com a
  temperatura e médias bem menores no inverno e na primavera (EDA da Aula 11);
- a temperatura e, portanto, a umidade seguem um ciclo diário forte, o que torna a **hora do dia** uma informação
  útil para quem precisa decidir quando restringir atividades;
- a chuva fica concentrada em poucos meses (quase toda hora tem 0 mm), o que cria longos períodos sem chuva.

Esse público não precisa ler histograma ou correlação. Ele precisa de **contagens em dias e horas**, comparação com
o "normal" e a época do ano em que o problema se concentra.

**Faixas usadas.** Classificação de umidade relativa baixa adotada pela Defesa Civil: **atenção** de 21% a 30%,
**alerta** de 12% a 20% e **emergência** abaixo de 12%. Um dia é classificado pela menor umidade horária registrada
nele. "Dia sem chuva" = chuva total do dia abaixo de 1,0 mm.

**Widgets que controlam o painel** (definidos antes do rascunho): *Ano em foco* (um ano ou a média 2014–2023) e
*Meses considerados* (ano inteiro, período seco mai–set ou período chuvoso out–abr). Com um ano em foco, cada KPI
mostra a diferença para a média dos 10 anos, calculada com o mesmo recorte de meses.

**Critérios comuns.** Horários em hora local de Brasília (UTC−3; os arquivos do INMET vêm em UTC). Um dia só entra
nas contagens diárias se tiver pelo menos 20 horas de umidade medida. Fórmulas implementadas em
[`src/indicadores.py`](../src/indicadores.py) e testadas em [`tests/test_calculos.py`](../tests/test_calculos.py).

Os valores citados abaixo são os do painel com o filtro padrão (2014–2023, ano inteiro).

---

## Métrica 1: Dias secos por ano

- **Variável:** `umidade` (umidade relativa horária, %) → resumida em `umidade_min` (mínima de cada dia).
- **O que mede:** quantidade de dias em que a umidade mínima ficou em **30% ou menos** (atenção ou pior), dividida
  pelo número de anos do recorte. Com um ano em foco, é a contagem daquele ano. Unidade: dias/ano (ou dias).
- **Por que foi escolhida:** é a forma mais direta de dimensionar o problema: "quantos dias por ano exigem algum
  cuidado". Usa a mínima do dia porque basta algumas horas de ar muito seco para o dia exigir orientação.
- **Público-alvo:** vigilância em saúde e Defesa Civil do DF.
- **Qual decisão pode ser apoiada por essa métrica?** Dimensionar campanhas e equipes para o período seco e
  avaliar se um ano está fora do padrão (ex.: 2015 teve 114 dias, contra média de 88,5).
- **O que comunica ao público-alvo:** "Em um ano típico, Brasília passa cerca de 88 dias com o ar em estado de
  atenção ou pior em algum momento do dia."

## Métrica 2: Dias em alerta por ano

- **Variável:** `umidade_min`.
- **O que mede:** dias com umidade mínima de **20% ou menos** (alerta ou emergência), por ano. Unidade: dias/ano.
- **Por que foi escolhida:** separa o desconforto comum (atenção) dos dias realmente graves, em que a
  recomendação muda de "hidrate-se" para "suspenda atividades ao ar livre". Média 2014–2023: 22,9 dias/ano.
- **Público-alvo:** vigilância em saúde e Defesa Civil do DF.
- **Qual decisão pode ser apoiada por essa métrica?** Acionar protocolos mais rígidos (escolas, eventos,
  trabalhadores ao ar livre) e priorizar recursos nos anos com mais dias críticos.
- **O que comunica ao público-alvo:** quantos dias por ano chegam ao nível que justifica alerta oficial.

## Métrica 3: Horas de ar seco

- **Variável:** `umidade` (horária).
- **O que mede:** fração das horas medidas com umidade de **30% ou menos**. Com um ano em foco, a diferença para a
  média aparece em pontos percentuais (p.p.). Média 2014–2023: 7,2% das horas.
- **Por que foi escolhida:** as métricas 1 e 2 dizem *quantos dias*; esta diz *quanto tempo* de exposição, já que um
  dia pode ter 1 ou 8 horas de ar seco.
- **Público-alvo:** vigilância em saúde e Defesa Civil do DF.
- **Qual decisão pode ser apoiada por essa métrica?** Comparar a intensidade entre anos e entre período seco e
  chuvoso (12,5% das horas no período seco contra 3,4% no chuvoso).
- **O que comunica ao público-alvo:** "cerca de 1 em cada 14 horas do ano tem ar seco."

## Métrica 4: Maior estiagem

- **Variável:** `precipitacao` (horária) → `chuva_total` (soma do dia).
- **O que mede:** a maior sequência de **dias consecutivos** com chuva abaixo de 1 mm no recorte. Um dia sem dado
  interrompe a sequência (não presumo que foi seco). Unidade: dias. Maior do período: 133 dias, de 07/05/2022 a
  16/09/2022.
- **Por que foi escolhida:** a umidade baixa vem junto de longos períodos sem chuva, que também aumentam o risco de
  queimadas e a poeira no ar. A duração diz por quanto tempo as medidas precisam ser mantidas.
- **Público-alvo:** Defesa Civil (queimadas, abastecimento) e vigilância em saúde.
- **Qual decisão pode ser apoiada por essa métrica?** Planejar a duração das campanhas e de brigadas de incêndio.
- **O que comunica ao público-alvo:** "no pior ano, Brasília ficou mais de quatro meses sem uma chuva de pelo
  menos 1 mm."

## Métrica 5: Hora mais seca do dia

- **Variáveis:** `umidade` e `hora` (hora local).
- **O que mede:** a hora do dia com a maior fração de horas com umidade de 30% ou menos, e essa fração. No período
  todo: **15h**, com 21,3% das horas das 15h abaixo do limiar.
- **Por que foi escolhida:** transforma o ciclo diário visto na EDA em uma orientação prática de horário.
- **Público-alvo:** vigilância em saúde, secretarias de educação e de esporte.
- **Qual decisão pode ser apoiada por essa métrica?** Definir a janela em que atividades físicas ao ar livre devem
  ser evitadas (o mapa mês × hora mostra a janela completa: em agosto e setembro, mais de 40% das horas entre 12h e 18h estão em 30% ou menos).
- **O que comunica ao público-alvo:** "o pior horário é o meio da tarde."

---

## Visualizações de apoio

| Gráfico | Pergunta que responde |
|---|---|
| Mapa de calor mês × hora (% das horas com UR ≤ 30%) | Em que meses e horas o ar fica seco? |
| Barras empilhadas de dias por nível em cada mês | Em que meses aparecem dias de atenção, alerta e emergência, e quantos? |
| Barras de dias secos por ano, com a média | O ano escolhido foi atípico? |
| Ciclo diário da umidade (mediana e percentil 10) | Como a umidade se comporta ao longo do dia, inclusive nos dias mais secos? |

## Limitações

- Uma única estação (A001, Plano Piloto). Outras regiões do DF podem ser mais secas ou mais úmidas.
- 10 anos de dados: a média 2014–2023 é uma referência descritiva, não uma "normal climatológica" de 30 anos.
- As métricas descrevem o que aconteceu; não são previsão.
