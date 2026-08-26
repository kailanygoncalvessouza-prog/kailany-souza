# Notas pra montar relatorio.md e video (não é o entregável final, é rascunho de continuidade)

## Frases/decisões que o usuário pediu explicitamente pra entrar no relatório

1. VivaReal = preço ANUNCIADO, não o preço de venda real. No Brasil, imóvel geralmente vende mais barato que o anúncio → **retorno real tende a ser um pouco MELHOR** do que o yield bruto calculado sugere.
2. O yield líquido calculado só desconta condomínio + IPTU. NÃO desconta taxa de plataforma (Airbnb), limpeza, nem taxa de administração/gestão → **retorno real tende a ser mais BAIXO** na prática do que o yield líquido calculado sugere.
   (as duas puxam em direções opostas — parcialmente se cancelam, mas não sabemos por quanto)

## Reframe da narrativa da tese (pedido explícito do usuário, fase 6)

NÃO contar como "Centro perdeu". Contar como: **apartamento de 1 quarto rende mal em QUALQUER bairro** — Centro e Meia Praia deram yield líquido negativo os dois. Centro não é o vilão sozinho, é só o pior exemplo de um tipo de imóvel que já não é bom.

## Guardar pra recomendação final (fase 7)

**Morretes / 2 quartos é a resposta pra "o que você compraria hoje"** — yield bruto 2,3%, líquido 1,7% (quase o dobro do 2º colocado), n=1.037 no VivaReal (amostra enorme, alta confiança no preço de compra), 2º lugar em receita anual entre os 8 segmentos elegíveis (R$18.333). Não estava no roteiro original da tese, apareceu como achado orgânico da segmentação.

## Cadeia de evidência sobre a tese (bairro Centro / tipologia compacto)

- Studio no Centro: 3 anúncios no bairro inteiro, 0 com dado de receita — tese, no componente "studio", é literalmente intestável.
- 1-quarto no Centro precifica por noite 25-31% mais caro que Meia Praia (Mann-Whitney significativo, p<0.01) — sinal real de poder de precificação.
- Mas receita anual estimada: Centro 1q (R$6.382) < Meia Praia 1q (R$8.242) — pior lugar entre os 8 segmentos elegíveis.
- Yield bruto: Centro 1q (0,7%) < Meia Praia 1q (0,9%) — os dois no fundo da tabela de 8.
- Yield líquido: Centro 1q (-0,1%) vs Meia Praia 1q (-0,2%) — **praticamente empatados, os dois negativos** (Centro leva por pouco no líquido, pela estrutura de custo menor de condomínio, mas a diferença é pequena).
- Mecanismo: preço/noite do 1-quarto é MUITO mais baixo que dos maiores (mediana R$390 vs R$470-1.100), mas o preço de COMPRA não cai na mesma proporção (77-81% do preço do 2-quarto) — não tem desconto de compra proporcional ao potencial de receita menor. É isso que quebra o yield do 1-quarto, em qualquer bairro.
- Proxy de calendário (checagem robustez): 1-quarto tem, na verdade, a MAIOR taxa de reserva em alta temporada entre as tipologias confiáveis (14,3% mediana) — não é um problema de ocupação, é puramente de preço/noite baixo não compensado por desconto de compra.

## Posição (fase 6, a fechar formalmente)

Tese REFUTADA no componente "tipo de imóvel" (compacto é o pior tipo do dataset em yield, com ou sem Centro). NÃO claramente refutada nem sustentada no componente "localização" (Centro não perde de forma clara pra Meia Praia dentro do 1-quarto — estão tecnicamente empatados no yield líquido, ambos negativos). A tese erra mais no "o quê" comprar do que no "onde".

## Recomendação final concreta (fase 7, fechada)

**Perfil: apartamento de 2 quartos em Morretes.** Yield bruto 2,3%, líquido 1,7% (após condomínio+IPTU) — melhor do grupo de 8 segmentos elegíveis, com folga (quase 2x o 2º colocado).

**Correção 1 (pedida pelo usuário):** o N=1.037 do VivaReal tinha duplicatas óbvias (mesmo preço+área+anunciante+título, só listing_id diferente — mesmo anúncio repostado). Dedupe "forte" só no Morretes/2q reduz pra N=915. MAS a comparação com os outros 7 segmentos (ainda brutos) não era justa.

**Correção 2 (o usuário pegou de novo, certo): dedupe forte precisa rodar na base VivaReal INTEIRA, antes de segmentar, não só no Morretes.** Refiz assim — dedupe (preço+área+anunciante+título idênticos) na base toda: 8.293 → 7.908 linhas (-4,6%, 385 IDs extras removidos, 232 grupos afetados). Números finais, comparação justa entre os 8:

| Bairro | Tipologia | N VivaReal (dedup correto) | Preço venda mediano | Yield bruto | Yield líquido |
|---|---|---|---|---|---|
| Meia Praia | 3 quartos | 1.668 | R$1.887.400 | 0,93% | 0,44% |
| Meia Praia | 4+ quartos | 1.392 | R$3.700.000 | 0,67% | 0,29% |
| **Morretes** | **2 quartos** | **914** | **R$790.000** | **2,32%** | **1,69%** |
| Centro | 3 quartos | 432 | R$2.100.000 | 0,64% | 0,18% |
| Meia Praia | 2 quartos | 234 | R$1.099.520 | 1,27% | 0,64% |
| Centro | 2 quartos | 84 | R$1.195.000 | 0,87% | 0,28% |
| Meia Praia | 1 quarto | 50 | R$850.000 | 0,97% | -0,16% |
| Centro | 1 quarto | 21 | R$890.000 | 0,72% | -0,07% |

Ranking de N confirma: Morretes é a **3ª maior amostra**, não a maior (Meia Praia 3q e 4+ são maiores, mas têm yield muito pior — tamanho de amostra não decide o ranking de yield). Números do Morretes praticamente não mudaram (914 vs 915, mesma mediana de preço, yield igual). Alguns outros segmentos tiveram ajuste pequeno (Meia Praia 1-quarto: preço mediano caiu de R$877.500 pra R$850.000, condomínio subiu — yield líquido foi de -0,17% pra -0,16%, continua negativo). Conclusão final não muda: Morretes/2-quartos seguue como recomendação, com o argumento certo agora sendo "amostra robusta (914, bem acima do mínimo de 15) e de longe o melhor yield", não "a maior amostra".

Gráficos 02, 03 e 04 foram regenerados com os números corrigidos. resumo.csv também.

Exemplos reais próximos da mediana (R$790.000):
- R$790.000, 68m², condomínio R$350/mês — Nei Costa — https://www.vivareal.com.br/imovel/apartamento-2-quartos-morretes-bairros-itapema-com-garagem-68m2-venda-RS790000-id-2694369976/
- R$790.000, 67m², condomínio R$400/mês, "novo pronto pra morar" — REDE MOI — https://www.vivareal.com.br/imovel/apartamento-2-quartos-morretes-bairros-itapema-com-garagem-67m2-venda-RS790000-id-2763648029/

Nota: o anúncio da Nei Costa aparece duplicado sob 4 listing_id diferentes no VivaReal — mais um artefato de scraping (mesmo imóvel, IDs diferentes), não afeta a mediana calculada (baseada em preço, não em contagem de IDs).

Payback simples: ~R$790.000 / R$18.333 receita anual ≈ 43 anos (bruto) / ~R$790.000 / R$13.368 receita líquida ≈ 59 anos (líquido). Números longos — comunicar como "melhor opção relativa no dataset", não como retorno objetivamente excelente. Yield STR abaixo de 2-3%/ano é baixo pro setor — sinal de preço de compra inflado em Itapema e/ou proxy de receita conservador (prováveis os dois).

## Gráficos gerados (figures/)

1. `01_receita_por_segmento.png` — receita anual mediana por bairro x tipologia (8 elegíveis)
2. `02_yield_bruto_liquido.png` — yield bruto vs líquido por segmento, 1-quarto negativo em qualquer bairro
3. `03_mapa_yield.png` — scatter preço de compra x receita anual, Morretes se destaca
4. `04_tese_centro_1quarto.png` — 3 painéis: preço/noite, receita anual, yield líquido, Centro vs Meia Praia no 1-quarto
5. `05_divergencia_proxies.png` — scatter mostrando correlação ~0 entre os dois proxies de ocupação

## Limitações a repetir no relatório final

- Universo de receita = só segmento "estabelecido" (tem Price_AV), não é média de mercado.
- Proxy de receita (review-rate) é conservador — reflete desempenho de host mediano/amador, não o que uma operação profissional (Seazone) conseguiria.
- Divergência entre os dois proxies de ocupação nunca foi resolvida, só documentada.
- Amostra de 1-quarto é a menor entre os segmentos elegíveis (32-82).
- Yields absolutos (0,6%-2,3% bruto) são baixos pra padrão de mercado STR — pode refletir preço de compra inflado em Itapema, subestimação do proxy, ou os dois.
