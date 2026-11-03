# Declaração de Uso de IA

**Nome:** João Victor Guimarães Cavalcanti Uchôa
**Data:** 03/11/2026

> Rascunho preenchido com o que foi feito com apoio de IA. **Revisar, completar a parte de "aceito / modificado /
> rejeitado" com a minha avaliação e assinar antes da entrega.**

## Ferramenta

Claude Code (modelo Claude Opus 5.5, Anthropic), executado no VS Code, com acesso ao repositório, ao terminal e ao
navegador para rodar e testar o app.

## Como a IA foi usada

Um único pedido abrangente (copiado abaixo) para o Claude Code, que:

1. analisou os três repositórios de referência indicados e o repositório-modelo da disciplina;
2. localizou a minha EDA da Aula 11 e, como o `clima_brasilia.csv` não estava mais no computador, reconstruiu o
   CSV a partir de `clima_brasilia_limpo.pdf` (o mesmo dataset da aula, exportado em PDF), conferindo que todos os
   números batem com os da EDA (87.582 linhas, ausentes, médias, correlação, outliers e chuva por ano);
3. escreveu o notebook `eda-com-downloads.ipynb`, o `app.py`, os módulos de `src/`, os testes de `tests/`,
   o tema, os rascunhos de `entregas/`, a justificativa das métricas e o `README.md`;
4. rodou os testes automatizados e o app no navegador (desktop, celular, tema escuro) e corrigiu os problemas
   encontrados;
5. organizou o trabalho em commits por etapa.

O arquivo [prompts-utilizados.md](prompts-utilizados.md) organiza esse trabalho em etapas, em forma de prompts em
primeira pessoa; ele **não** é a transcrição de conversas separadas.

Os trechos de código feitos com IA estão marcados com `# [IA]` no topo de cada arquivo.

## Prompt usado

```text
# Desenvolvimento completo da atividade de AVD — Streamlit

Quero que você desenvolva e entregue integralmente a atividade de Análise e Visualização de Dados (AVD) no meu
repositório:

Meu repositório: https://github.com/joaovictorgcu/AVD_STREAMLIT

Repositórios de referência (trabalhos de outros alunos):
- https://github.com/gabrielfranca10/AVD-20262-pratica-streamlit
- https://github.com/Lucasmenezes08/AVD-20262-pratica-streamlit
- https://github.com/whosricardo/avd-streamlit

Sua responsabilidade é analisar os três projetos, entender como estruturaram a atividade e utilizar suas
implementações como referências para desenvolver uma solução completa, consistente e original no meu repositório.

Não quero apenas orientações ou sugestões: execute o trabalho, implemente os arquivos, teste a aplicação, organize
os entregáveis e publique as alterações.

1. Análise inicial dos repositórios — acessar e analisar os três repositórios; examinar estrutura, notebooks,
   dados, dashboards, prompts e implementações; comparar pontos fortes e fracos; identificar erros e limitações.
   Não copiar cegamente; desenvolver implementação própria, coerente com a minha EDA. Depois, analisar o meu
   repositório atual.

2. Entendimento da EDA e definição do público-alvo — identificar o dataset, examinar os notebooks, entender as
   variáveis, distribuições e relações, os principais padrões da EDA, escolher um público-alvo específico para o
   segundo dashboard e justificar a escolha com base nos dados.

3. Desenvolvimento dos dois dashboards, acessíveis por abas.
   Dashboard 1 — Laboratório de distribuição e correlação: heatmap da correlação entre variáveis quantitativas,
   histograma para cada variável avaliada, seletor de variáveis no painel lateral, slider de intervalo para excluir
   valores, gráficos atualizados conforme os filtros. Além disso: estatísticas descritivas, assimetria, comparação
   entre variáveis, outliers e interpretação das correlações. Cada visualização deve ter finalidade analítica.
   Dashboard 2 — KPIs para um público-alvo específico: 3 a 5 KPIs relevantes, pelo menos 3 visualizações além dos
   KPIs, indicadores que apoiem decisões, nomes, unidades e critérios de cálculo documentados, sem inventar
   indicadores sem fundamento nos dados.

4. Estrutura do projeto: notebooks/, app.py, entregas/ (dois rascunhos dos dashboards com documentação),
   prompts/ (registro dos prompts, em primeira pessoa, representando as etapas do trabalho — são exemplos
   simulados, não evidências de conversas reais), README.md com o link da aplicação publicada e requirements.txt.

5. Identidade visual e experiência de uso: hierarquia visual, consistência, legibilidade, formatação de números,
   responsividade e navegação entre os dashboards.

6. Qualidade técnica e validação: testes funcionais (app inicia, abas, todos os widgets, seletor, slider,
   histogramas, correlação, KPIs, datasets vazios, nulos e variáveis constantes), testes dos dados (correspondência
   com o original, duplicações, ausentes, filtros, consistência das métricas, sem dados sensíveis) e teste da
   aplicação publicada (janela anônima, sem autenticação, abas, widgets, versão mais recente). Não declarar teste
   aprovado sem executá-lo.

7. Publicação no Streamlit Community Cloud e README com nome, objetivo, dataset, público-alvo, dashboards, KPIs,
   execução local, dependências e link da aplicação. Etapas que dependam da minha autenticação devem ficar
   indicadas, sem simular que foram concluídas.

8. Commits pequenos, lógicos e descritivos, sem operações destrutivas de Git.

9. Critérios de conclusão (checklist) e 10. relatório final com o que foi feito, público, KPIs, arquivos, testes,
   commits, links e pendências.

Não invente dados reais, resultados de testes, publicações ou commits.
```

*(Prompt enviado em 03/11/2026. O texto acima reproduz o início e o fim literalmente; as seções 1 a 10 estão
condensadas, mantendo todas as instruções. A versão completa está no histórico da sessão do Claude Code.)*

## O que foi aceito, modificado ou rejeitado e por quê

- **Aceito:** _(preencher — ex.: escolha do público-alvo, fórmulas dos KPIs, estrutura em `src/`, testes)_
- **Modificado:** _(preencher — o que eu ajustei depois de revisar)_
- **Rejeitado:** _(preencher)_

Pontos que eu conferi pessoalmente: _(preencher — ex.: números da conferência com a EDA, leitura dos gráficos)_
