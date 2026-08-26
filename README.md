[VÍDEO — LINK DO GOOGLE DRIVE AQUI ANTES DE ENTREGAR] · ⚠️ placeholder: gravar e colar o link nesta linha antes da submissão final (permissão "qualquer pessoa com o link").

# Hackathon Jovens Talentos AI Builder 2026 — Seazone

Recomendação de investimento imobiliário em Itapema (SC) para a Seazone, a partir do cruzamento de anúncios de Airbnb (Details/Hosts/Mesh/Price_AV) e de venda (VivaReal).

**A recomendação final e a posição sobre a tese "compactos no Centro" estão em [`relatorio.md`](relatorio.md).**

## Como rodar

Requisitos: Python 3.11+, `pandas`, `matplotlib`, `scipy`.

```bash
pip install pandas matplotlib scipy
```

1. Os 5 CSVs originais já estão em `data/` (mesma base do desafio, sem alteração).
2. Abra `analise.ipynb` e rode as células em ordem (de cima para baixo, sem pular). O notebook é o pipeline completo: carrega os dados, faz o join, dedupe, constrói o proxy de receita/ocupação, segmenta bairro × tipologia, cruza com o VivaReal e calcula yield.
3. Os gráficos finais já estão gerados em `figures/` (o notebook reproduz os números por trás deles; a geração das imagens em si está em `make_charts.py`, que lê o resultado do notebook).
4. `resumo.csv` é a tabela de apoio com os 8 segmentos bairro×tipologia elegíveis (n≥15 anúncios com preço), todas as métricas usadas na decisão.

## Onde está a resposta de cada pergunta do desafio

Todas as 4 perguntas são respondidas com detalhe em `relatorio.md`. Resumo de onde encontrar cada uma:

1. **Melhor perfil de imóvel** → seção "Melhor perfil" do relatório + `analise.ipynb` (Fase 4, segmentação) + `figures/01_receita_por_segmento.png`.
2. **Melhor localização por receita** → seção "Melhor localização" do relatório + mesma segmentação + `figures/01_receita_por_segmento.png` e `figures/03_mapa_yield.png`.
3. **Características que explicam a melhor receita** → seção "Por que esses imóveis rendem mais" do relatório + análise de mecanismo em `analise.ipynb` (Fase 6) + `figures/04_tese_centro_1quarto.png`.
4. **O que comprar hoje + retorno estimado** → seção "Recomendação final" do relatório (Morretes / 2 quartos, yield bruto e líquido, payback, 2 exemplos reais de anúncio) + `analise.ipynb` (Fase 5-7) + `figures/02_yield_bruto_liquido.png` e `figures/03_mapa_yield.png`.
5. **Posição sobre a tese "compactos no Centro"** → seção dedicada "A tese dos compactos no Centro" do relatório, com a evidência completa (preço/noite, receita, yield, mecanismo) + `figures/04_tese_centro_1quarto.png`.

## Estrutura do repositório

```
data/                 os 5 CSVs originais do desafio, sem alteração
analise.ipynb         pipeline completo (join, dedupe, proxy de receita/ocupação, segmentação, cruzamento com VivaReal, yield)
figures/               os 5 gráficos-chave referenciados no relatório
resumo.csv             tabela de apoio com os 8 segmentos bairro×tipologia elegíveis e todas as métricas
relatorio.md           recomendação final, posição sobre a tese, limitações
roteiro_video.md       roteiro falado do vídeo (≤180s), com deixa de qual gráfico/tela mostrar em cada momento
apoio_visual.html      apoio visual pra gravação — 6 telas sincronizadas com os timestamps do roteiro (uma delas é a linha do tempo com os 9 momentos da investigação), com cronômetro embutido
ai-log/ai-log.md       conversa completa com a IA (texto integral, sem cortes) usada para chegar na recomendação
make_charts.py         gera os 5 PNGs de figures/ a partir dos resultados do notebook
build_notebook.py      script que gerou analise.ipynb (ambiente sem suporte a nbformat/jupyter — notebook montado como JSON nbformat v4 direto)
build_apoio_visual.py  script que gerou apoio_visual.html
scratch/                notas de continuidade e exploração inicial dos dados (fases 0-1) — não é o pipeline final, é rastro do processo
```

`make_charts.py`, `build_notebook.py` e `build_apoio_visual.py` são scripts de geração, não precisam ser executados pra avaliar a entrega — os artefatos que eles produzem (`figures/*.png`, `analise.ipynb`, `apoio_visual.html`) já estão no repositório, prontos.

## Limitações a ter em mente ao ler os números

Estão detalhadas em `relatorio.md`, mas resumindo: a estimativa de receita cobre só o segmento "estabelecido" do Airbnb (anúncios com dado de preço capturado, ~23% da base); o proxy de receita é conservador (baseado em taxa de conversão de review, reflete desempenho de host mediano/amador); o preço de venda do VivaReal é o preço anunciado, não o preço de venda real; e o yield líquido calculado desconta condomínio e IPTU, mas não desconta taxa de plataforma, limpeza nem gestão. Tudo isso está explicado com mais contexto no relatório.
