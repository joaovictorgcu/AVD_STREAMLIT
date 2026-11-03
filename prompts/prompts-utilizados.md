# Prompts utilizados no desenvolvimento do projeto

### 1. Entendendo os dados

Estou trabalhando em um projeto de análise de dados com informações meteorológicas de Brasília, retiradas do INMET, entre 2014 e 2023. Quero que você analise meu notebook de EDA e me ajude a entender melhor os dados. Veja quais variáveis são mais interessantes, se existem muitos valores ausentes e quais relações entre elas podem render análises legais para o trabalho. Não quero mudar o que já fiz sem necessidade, mas queria encontrar algumas coisas que possam ser exploradas melhor.

### 2. Melhorando o tratamento dos dados

Dá uma olhada no tratamento que fiz no dataset. Tenho algumas dúvidas sobre os valores -9999, os horários e a conversão de UTC para o horário de Brasília. Quero garantir que as datas estejam corretas antes de começar a desenvolver os dashboards. Também veja se vale a pena criar algumas colunas novas, como estação do ano, período seco e chuvoso e ponto de orvalho.

### 3. Explorando melhor as correlações

Quero aprofundar um pouco a parte de correlação da minha EDA. Principalmente entre temperatura, umidade relativa e precipitação. Veja se faz sentido usar Pearson ou Spearman para essas variáveis e me explique as diferenças. Também queria entender melhor como identificar outliers nesse dataset, porque a precipitação tem muitos valores zerados e acho que isso pode atrapalhar a análise.

### 4. Pensando no primeiro dashboard

Agora preciso começar a transformar minha análise em uma aplicação Streamlit. Pensei em fazer o primeiro dashboard como um laboratório para explorar os dados. Queria colocar histogramas, um mapa de calor de correlação e alguns filtros para o usuário conseguir escolher as variáveis e os intervalos que deseja analisar. Me ajude a organizar essa tela e pensar em quais informações seriam mais interessantes de mostrar, sem deixar tudo muito carregado.

### 5. Escolhendo o público do segundo dashboard

Estou com dificuldade para definir o público-alvo do segundo dashboard. Como o dataset é sobre o clima de Brasília, pensei em fazer algo voltado para vigilância em saúde ambiental ou Defesa Civil, principalmente por conta dos períodos de umidade muito baixa. Analise essa ideia e veja se ela realmente combina com os dados que tenho. Quero que o segundo painel tenha uma finalidade mais prática, e não seja só mais um conjunto de gráficos meteorológicos.

### 6. Criando os indicadores

Para o segundo dashboard, queria trabalhar com indicadores relacionados à umidade baixa e aos períodos de estiagem. Pensei em mostrar a quantidade de dias com umidade abaixo de 30%, os dias em situação de alerta ou emergência, a porcentagem de horas com umidade baixa, a maior sequência de dias sem chuva e os horários em que a umidade costuma ficar menor.

Me ajude a definir os cálculos desses indicadores e confira se eles fazem sentido. Tome cuidado com valores ausentes e com os dias que não possuem medições suficientes, porque não quero apresentar números errados.

### 7. Desenvolvendo os gráficos do segundo painel

Quero que o segundo dashboard fique mais voltado para quem precisa acompanhar os períodos de baixa umidade em Brasília. Além dos indicadores, pensei em colocar um mapa de calor mostrando os meses e horários com menor umidade, um gráfico com os níveis de alerta ao longo dos meses e uma comparação entre os anos.

Também queria mostrar o comportamento da umidade durante o dia. Implemente essas visualizações usando Altair e pandas, tentando manter os gráficos fáceis de entender e sem muita informação desnecessária.

### 8. Melhorando a aparência da aplicação

A aplicação já está tomando forma, mas quero melhorar a parte visual. Dê uma revisada nas duas abas e veja o que pode ficar mais organizado. Quero um visual mais moderno, com os gráficos bem distribuídos, indicadores destacados e filtros fáceis de encontrar. Também gostaria de ter um tema escuro e outro claro. Tome cuidado para não prejudicar a leitura dos gráficos, principalmente do mapa de calor e das cores usadas para representar os níveis de umidade.

### 9. Revisando os cálculos e os filtros

Quero que você faça uma revisão dos cálculos do dashboard, principalmente dos indicadores de estiagem e umidade baixa. Crie alguns exemplos pequenos de dados para testar os resultados esperados e compare com o que a aplicação está calculando. Teste também os filtros com diferentes anos e meses, valores ausentes e intervalos em que não existam registros. Veja se os gráficos e os KPIs continuam funcionando nessas situações.

### 10. Revisando o projeto inteiro

Agora quero que você faça uma revisão geral do repositório antes da entrega. Confira se a estrutura está organizada, se os notebooks estão funcionando e se a aplicação consegue ser executada em outro ambiente. Veja também se o README explica bem o projeto, a origem dos dados e o funcionamento dos dois dashboards. Confira se os dois rascunhos estão na pasta entregas e se os arquivos necessários para executar o Streamlit estão presentes.

Por fim, faça uma última bateria de testes e veja se existe algum problema que possa aparecer quando outra pessoa acessar a aplicação.
