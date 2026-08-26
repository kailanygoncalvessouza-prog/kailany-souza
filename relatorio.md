# Recomendação de investimento imobiliário — Itapema (SC)

Hackathon Jovens Talentos AI Builder 2026 — Seazone

## Como chegamos aqui, em uma frase

Cruzamos os anúncios de Airbnb (receita) com os anúncios de venda do VivaReal (custo de compra) para os bairros e tipologias com amostra suficiente, e calculamos yield bruto e líquido por segmento. A metodologia completa, com cada decisão e correção, está em `analise.ipynb` e no `ai-log/`.

## Escopo e proxy de receita — o que dá pra medir com esses dados

Só 23% dos anúncios de Airbnb (995 de ~4.437) têm dado de preço capturado (`Price_AV`). Não tentamos imputar preço para os outros 77% — não valia o tempo do desafio, e imputar preço a partir de reviews/localização introduziria mais ruído do que resolveria. **Toda a análise de receita cobre só o segmento "estabelecido"** (tem preço capturado), não é uma média do mercado inteiro de Itapema. Essa cobertura também não é aleatória: anúncios com 6+ reviews têm 56-80% de chance de ter preço capturado, contra 1-6% para anúncios com 0-5 reviews — ou seja, o recorte com dado de receita já é enviesado para anúncios mais maduros/populares, o que é esperado (scraper captura calendário de quem tem mais tração) mas precisa ficar explícito.

Para estimar receita anual por anúncio, usamos o **método de taxa de conversão de review** (metodologia Inside Airbnb): número de reviews × 2 (taxa de conversão de 50%) × 3 noites por reserva × preço/noite, com teto de 70% de ocupação anual. Os 21 anúncios com preço capturado mas 0 reviews foram marcados como "dado insuficiente" e excluídos do ranking de receita (não zerados — anúncio novo sem review não é o mesmo que anúncio sem demanda).

Como checagem de robustez, também construímos um segundo proxy independente: a taxa de datas que "somem" entre capturas sucessivas do calendário (interpretado como reserva provável), calculado só na janela de alta temporada. Os dois proxies **não se correlacionam** (Spearman ≈ -0,03 em n=630, ver `figures/05_divergencia_proxies.png`) — investigamos se era bug (não era: cross-tab por quartil mostra distribuição uniforme, sem diagonal) e decidimos reportar a divergência como achado, não escondê-la. Isso limita a confiança absoluta nos números de receita, mas como os dois proxies concordam na direção do argumento principal deste relatório (ver seção sobre a tese), a divergência não muda a recomendação — só reduz a precisão do número exato.

## Melhor perfil de imóvel

Segmentando por bairro × tipologia (só combinações com **n ≥ 15** anúncios com preço, para não recomendar em cima de amostra pequena), os 8 segmentos elegíveis por receita anual mediana:

| Bairro | Tipologia | N c/ preço | Receita anual mediana | Preço/noite mediano |
|---|---|---|---|---|
| Meia Praia | 4+ quartos | 67 | R$ 24.967 | R$ 1.100 |
| **Morretes** | **2 quartos** | 59 | **R$ 18.333** | R$ 450 |
| Meia Praia | 3 quartos | 332 | R$ 17.580 | R$ 685 |
| Meia Praia | 2 quartos | 190 | R$ 14.000 | R$ 451 |
| Centro | 3 quartos | 47 | R$ 13.500 | R$ 790 |
| Centro | 2 quartos | 67 | R$ 10.396 | R$ 557 |
| Meia Praia | 1 quarto | 32 | R$ 8.242 | R$ 345 |
| Centro | 1 quarto | 82 | R$ 6.382 | R$ 434 |

Por receita bruta isolada, imóveis maiores (4+ quartos) vencem — esperado, cobem mais gente e cobram mais por noite. Mas receita bruta não é o critério certo para decisão de compra: o que importa é receita **relativa ao capital investido**, o que nos leva à seção de yield abaixo. Ver `figures/01_receita_por_segmento.png`.

## Melhor localização e cruzamento com o preço de compra

Cruzamos cada segmento elegível com o preço de venda mediano do VivaReal (depois de aplicar dedupe forte na base inteira — ver nota metodológica abaixo) para chegar em yield bruto (receita anual / preço de compra) e líquido (descontando condomínio e IPTU):

| Bairro | Tipologia | N VivaReal (dedup) | Preço de venda mediano | Yield bruto | Yield líquido |
|---|---|---|---|---|---|
| Meia Praia | 3 quartos | 1.668 | R$ 1.887.400 | 0,93% | 0,44% |
| Meia Praia | 4+ quartos | 1.392 | R$ 3.700.000 | 0,67% | 0,29% |
| **Morretes** | **2 quartos** | **914** | **R$ 790.000** | **2,32%** | **1,69%** |
| Centro | 3 quartos | 432 | R$ 2.100.000 | 0,64% | 0,18% |
| Meia Praia | 2 quartos | 234 | R$ 1.099.520 | 1,27% | 0,64% |
| Centro | 2 quartos | 84 | R$ 1.195.000 | 0,87% | 0,28% |
| Meia Praia | 1 quarto | 50 | R$ 850.000 | 0,97% | -0,16% |
| Centro | 1 quarto | 21 | R$ 890.000 | 0,72% | -0,07% |

**Morretes vence por larga margem** — yield líquido quase 3× o segundo colocado (Meia Praia 2 quartos, 0,64%). Não é o bairro com maior receita bruta (isso é Meia Praia), mas é onde o preço de compra é baixo o suficiente para essa receita compensar. Ver `figures/02_yield_bruto_liquido.png` e `figures/03_mapa_yield.png` (dispersão preço de compra × receita anual, Morretes se destaca isolado no canto de alto retorno relativo).

Morretes não estava no roteiro original de investigação — surgiu organicamente na segmentação, como 2º colocado em receita anual, e só entrou no cruzamento com VivaReal porque decidimos investigar além de Centro e Meia Praia quando apareceu "do nada" com um número forte. Vale registrar: **Morretes é a resposta para "o que a Seazone compraria hoje"** — ver seção de recomendação final.

## Por que esses imóveis rendem mais — o mecanismo

O que explica a receita e o yield não é só localização: é a relação entre **preço/noite** e **preço de compra**. Olhando pooled por tipologia (todos os bairros juntos):

- 1 quarto: preço/noite mediano R$ 390
- 2 quartos: R$ 470
- 3 quartos: R$ 680
- 4+ quartos: R$ 1.100

O preço/noite sobe de forma razoavelmente proporcional ao tamanho. O problema é que o **preço de compra não segue essa mesma proporção**: um 1-quarto custa 77-81% do preço de um 2-quarto no mesmo bairro, mas gera muito menos que 77-81% da receita — porque o preço/noite de um 1-quarto é desproporcionalmente mais baixo (R$ 390 vs R$ 450-470) para um imóvel que já não é tão mais barato de comprar. É essa desproporção — não ocupação, não localização isolada — que quebra o yield do 1-quarto em qualquer bairro (ver próxima seção). Checamos isso contra o proxy de calendário (robustez): 1-quarto tem, na verdade, a **maior** taxa de reserva em alta temporada entre as tipologias confiáveis (14,3% mediana) — não é problema de ocupação, é puramente preço/noite baixo sem desconto de compra equivalente. Ver `figures/04_tese_centro_1quarto.png`.

## A tese dos compactos no Centro — nossa posição

A tese interna da Seazone (ainda não validada) é que **apartamentos compactos (studio/1 quarto) na região do Centro** seriam a aposta mais eficiente. Testamos com os dados. Nossa posição, com números:

**No componente "tipo de imóvel" (compacto), a tese está REFUTADA.** 1-quarto é a pior tipologia do dataset em yield, **com ou sem Centro**:

- Yield líquido do 1-quarto: **negativo em Centro (-0,07%) e em Meia Praia (-0,16%)** — os dois únicos bairros com amostra suficiente de 1-quarto, e os dois no vermelho.
- Studio no Centro: só 3 anúncios no bairro inteiro, **0 com dado de receita** — a tese, no componente "studio", é literalmente intestável com os dados disponíveis. Não podemos nem refutar nem sustentar; simplesmente não há dado.

**No componente "localização" (Centro), a tese NÃO está claramente refutada nem sustentada** — dentro do 1-quarto, Centro e Meia Praia estão essencialmente empatados no yield líquido (-0,07% vs -0,16%, os dois negativos, Centro levemente à frente por ter condomínio mais baixo). Isolando só o efeito localização, os dados não dão um veredito forte num sentido ou noutro.

Vale registrar um sinal que vai na direção contrária ao yield, mas não muda a conclusão: o 1-quarto no Centro precifica por noite **25-31% mais caro** que Meia Praia (estatisticamente significativo, Mann-Whitney p<0,01) — há poder de precificação real ali. Mas isso não se traduz em receita anual maior (Centro 1q: R$ 6.382 vs Meia Praia 1q: R$ 8.242) nem em yield melhor, porque o volume de reservas e o preço de compra não compensam.

**Reformulando a história:** não é que "o Centro perdeu". É que **apartamento de 1 quarto rende mal em qualquer bairro** — Centro e Meia Praia deram os dois yield líquido negativo. O Centro não é o vilão isolado; ele é só o pior exemplo de um tipo de imóvel que já não é bom em nenhum lugar do dataset. A tese erra mais no **"o quê"** comprar (compacto) do que no **"onde"** (Centro).

## Recomendação final: o que a Seazone compraria hoje

**Perfil: apartamento de 2 quartos em Morretes.**

- Yield bruto: **2,32%** ao ano
- Yield líquido (descontando condomínio + IPTU): **1,69%** ao ano — quase o dobro do segundo colocado entre os 8 segmentos elegíveis
- Receita anual estimada: R$ 18.333 (2º lugar entre os 8 segmentos, atrás só do 4+ quartos de Meia Praia, que exige um capital de compra ~4,7× maior)
- Preço de compra mediano: R$ 790.000
- Amostra: **914 anúncios de venda no VivaReal** (depois de dedupe — ver nota metodológica), 61× o mínimo de 15 que exigimos para confiar num segmento. É a 3ª maior amostra dos 8 segmentos comparados (Meia Praia 3q e 4+ quartos têm mais anúncios à venda, mas rendem 0,44% e 0,29% líquido — menos de 1/3 do Morretes)

**Dois exemplos reais próximos da mediana:**

- R$ 790.000, 68 m², condomínio R$ 350/mês — corretora Nei Costa — [vivareal.com.br/imovel/apartamento-2-quartos-morretes-bairros-itapema-com-garagem-68m2-venda-RS790000-id-2694369976](https://www.vivareal.com.br/imovel/apartamento-2-quartos-morretes-bairros-itapema-com-garagem-68m2-venda-RS790000-id-2694369976/)
- R$ 790.000, 67 m², condomínio R$ 400/mês, "novo pronto pra morar" — REDE MOI — [vivareal.com.br/imovel/apartamento-2-quartos-morretes-bairros-itapema-com-garagem-67m2-venda-RS790000-id-2763648029](https://www.vivareal.com.br/imovel/apartamento-2-quartos-morretes-bairros-itapema-com-garagem-67m2-venda-RS790000-id-2763648029/)

**Payback simples:** R$ 790.000 / R$ 18.333 de receita anual ≈ **43 anos** (bruto) · R$ 790.000 / R$ 13.368 de receita líquida ≈ **59 anos** (líquido, considerando só condomínio+IPTU deduzidos). São números de payback longos — o correto é comunicar isso como **"melhor opção relativa dentro do dataset"**, não como um retorno objetivamente excelente em termos absolutos. Yields brutos abaixo de 2-3%/ano são baixos para o padrão do setor de short-stay — o que sinaliza preço de compra inflado em Itapema, um proxy de receita conservador, ou (mais provável) as duas coisas juntas.

**Duas ressalvas que puxam o retorno real em direções opostas, e que não calculamos, mas precisam entrar na decisão:**

1. O preço do VivaReal é o **preço anunciado**, não o preço de venda efetivo. No Brasil, imóveis geralmente vendem por menos que o anúncio — na prática, o retorno real tende a ser **um pouco melhor** do que o yield calculado sugere.
2. O yield líquido que calculamos só desconta condomínio e IPTU — **não desconta taxa de plataforma (Airbnb), limpeza, nem taxa de administração/gestão** de quem operar o imóvel. Isso puxa na direção contrária: o retorno real tende a ser **mais baixo** na prática do que o yield líquido calculado sugere.

Essas duas forças se cancelam parcialmente, mas não sabemos por quanto — não dá pra assumir que elas se anulam exatamente.

## Nota metodológica: por que o N do Morretes é 914 e não 1.037

Vale documentar porque foi um processo iterativo de correção, e é exatamente o tipo de coisa que dá confiança (ou não) num número usado para decisão. A base bruta do VivaReal tinha **8.293** linhas para os 8 segmentos comparados. Encontramos duplicatas óbvias — mesmo preço + área + anunciante + título, só o `listing_id` mudando (reposts do mesmo anúncio). Aplicamos dedupe "forte" (preço+área+anunciante+título idênticos) na **base inteira, antes de segmentar** — 8.293 → **7.908** linhas (-4,6%, 385 IDs extras removidos em 232 grupos). Testamos também um dedupe "fraco" (só preço+área) e descartamos: ele derrubava demais, porque vários grupos de preço+área idênticos têm múltiplos anunciantes diferentes — padrão normal de um prédio novo com várias unidades sendo vendidas por corretoras diferentes, não duplicata.

Importante: a primeira versão desse dedupe só tinha sido aplicada ao segmento Morretes isoladamente, e comparada contra os outros 7 segmentos ainda brutos — comparação injusta, já que o mesmo padrão de duplicata podia (e provavelmente afetava) os outros segmentos também. Corrigimos rodando o dedupe na base inteira antes de segmentar. O resultado final: Morretes é a **3ª maior amostra** dos 8 (não a maior — Meia Praia 3q e 4+ têm mais anúncios à venda), mas isso não muda a recomendação, porque tamanho de amostra não é o que desempata: os dois segmentos maiores têm yield muito pior. O argumento correto para confiar no Morretes é **"amostra robusta (914, 61× o mínimo)"**, não **"a maior amostra do cruzamento"**.

## Limitações

- A análise de receita cobre só o segmento "estabelecido" do Airbnb (anúncios com `Price_AV` capturado, ~23% da base) — não é uma média de mercado.
- O proxy de receita (taxa de conversão de review) é conservador — reflete desempenho de host mediano/amador com calendário próprio, não o que uma operação profissional como a Seazone conseguiria extrair do mesmo imóvel.
- A divergência entre os dois proxies de ocupação (taxa de review vs. datas que somem no calendário, Spearman ≈ -0,03) nunca foi resolvida, só documentada e verificada como não sendo bug.
- A amostra de 1-quarto é a menor entre os 8 segmentos elegíveis (32-82 anúncios com preço).
- Os yields absolutos (0,6%-2,3% bruto) são baixos para o padrão de mercado de short-stay — pode refletir preço de compra inflado em Itapema, subestimação do proxy de receita, ou os dois.
- O preço do VivaReal é preço anunciado, não preço de venda efetivo; o yield líquido não desconta taxa de plataforma, limpeza nem gestão (ver seção de recomendação final).

## Metodologia completa

Todo o pipeline — carga dos dados, dedupe de hosts, investigação dos outliers de preço R$10-29k/noite (confirmados como artefatos de bloqueio de calendário e picos de captura isolados, não imóveis de luxo genuínos), construção dos dois proxies de receita/ocupação, segmentação bairro×tipologia, dedupe da base VivaReal e cálculo de yield — está em `analise.ipynb`, executável do início ao fim. O processo completo de decisão, incluindo os pontos onde erramos e corrigimos (documentados de forma transparente, sem esconder), está em `ai-log/ai-log.md`.
