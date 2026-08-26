import json

cells = []

def md(text):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)})

def code(text):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                   "outputs": [], "source": text.strip("\n").splitlines(keepends=True)})

# ============================================================
md("""
# Itapema (SC) — Recomendação de investimento imobiliário pra Seazone

Pipeline completo: check dos dados → exploração → junção → proxy de receita/ocupação →
segmentação → cruzamento com VivaReal (yield) → teste da tese do Centro → recomendação final.

Cada seção corresponde a uma fase do processo documentado em `ai-log/ai-log.md` — as decisões
metodológicas (o que incluir, que proxy usar, que corte de amostra aplicar) foram tomadas em
conjunto com o usuário ao longo da conversa, não decididas sozinhas pelo modelo. Consulte o
ai-log pra ver o raciocínio e as alternativas descartadas em cada escolha.

**Como rodar:** ver `README.md` na raiz do repositório.
""")

code("""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

D = "data/"
""")

# ============================================================
md("""
## Fase 0 — Check dos CSVs

Carrega os 5 arquivos, corrige os problemas de qualidade de dado identificados na exploração
inicial: `Hosts_ids_Itapema.csv` tem linhas duplicadas por `owner_id` (só snapshots repetidos
do scraper — mantemos o mais recente), duas colunas 100% nulas (`response_rate_shown`,
`response_time_shown`), e `min_nights` é constante 0 em toda a base (coluna quebrada, ignorada).
""")

code("""
details = pd.read_csv(D+"Details_Itapema.csv", dtype={"airbnb_listing_id": str, "owner_id": str})
mesh = pd.read_csv(D+"Mesh_Ids_Data_Itapema.csv", dtype={"airbnb_listing_id": str})
price = pd.read_csv(D+"Price_AV_Itapema.csv", dtype={"airbnb_listing_id": str})

hosts_raw = pd.read_csv(D+"Hosts_ids_Itapema.csv", dtype={"owner_id": str})
hosts_raw["host_snapshot_date"] = pd.to_datetime(hosts_raw["host_snapshot_date"])
hosts = (hosts_raw.sort_values("host_snapshot_date")
                   .drop_duplicates("owner_id", keep="last")
                   .drop(columns=["response_rate_shown", "response_time_shown"]))

print("Details:", details.shape, " Mesh:", mesh.shape, " Hosts (dedup):", hosts.shape, " Price_AV:", price.shape)

# checagem de integridade das chaves — Details <-> Mesh <-> Hosts
print("Details.airbnb_listing_id em Mesh:", details["airbnb_listing_id"].isin(mesh["airbnb_listing_id"]).mean())
print("Details.owner_id em Hosts:", details["owner_id"].isin(hosts["owner_id"]).mean())
print("Details.airbnb_listing_id em Price_AV (cobertura de preço):",
      details["airbnb_listing_id"].isin(price["airbnb_listing_id"]).mean().round(3))
""")

md("""
**Achado crítico da fase 0:** só 22,6% dos anúncios (1.005 de 4.441) têm dado de preço no
Price_AV — e a cobertura não é aleatória (concentra em anúncios com mais reviews, mais
superhost, hosts mais experientes). Por isso a análise de receita, a partir daqui, cobre só o
segmento "estabelecido" da base — decisão explícita do usuário (turno 2 do ai-log), tratada
como limitação no relatório final, não escondida.

**Outliers de preço:** investigamos os anúncios com preço ≥R$10.000/noite (turno 2/3 do
ai-log) e concluímos que são artefatos (preço de bloqueio constante, ou pico isolado
incompatível com o resto do calendário do próprio anúncio), não luxo real. Excluímos os 4
listings com algum preço ≥R$5.000 (183 de 118.839 linhas, 0,15% da base) do cálculo de preço.
""")

code("""
outlier_ids = set(price.loc[price["price"] >= 5000, "airbnb_listing_id"].unique())
price_clean = price[~price["airbnb_listing_id"].isin(outlier_ids)]
price_med = price_clean.groupby("airbnb_listing_id")["price"].median().rename("preco_noite")
print(f"{len(outlier_ids)} listings-outlier excluídos do cálculo de preço.")
""")

# ============================================================
md("""
## Fase 1 — Exploração inicial

Distribuições básicas de preço, quartos, tipos, bairros, avaliações e hosts — sem compromisso
com um modelo ainda. Separando quem tem dado de preço (`has_price`) de quem não tem, a pedido
do usuário, pra checar se o corte é sistemático (é: quality bias, não bias geográfico/tipológico).
""")

code("""
def tipologia(n):
    if n == 0: return "studio (0q)"
    if n == 1: return "1 quarto"
    if n == 2: return "2 quartos"
    if n == 3: return "3 quartos"
    return "4+ quartos"

df = (details.merge(mesh[["airbnb_listing_id", "suburb"]], on="airbnb_listing_id", how="left")
             .merge(hosts[["owner_id", "years_host", "months_host", "is_superhost"]], on="owner_id", how="left"))
df["tipologia"] = df["number_of_bedrooms"].apply(tipologia)
df["has_price"] = df["airbnb_listing_id"].isin(price_med.index)
df = df.merge(price_med, on="airbnb_listing_id", how="left")
df = df[~df["airbnb_listing_id"].isin(outlier_ids)].copy()

owner_counts = details["owner_id"].value_counts()
df["host_multi_listing"] = df["owner_id"].map(owner_counts) > 1

print("Distribuição de bairros:")
print(df["suburb"].value_counts())
print("\\nDistribuição de tipologia:")
print(df["tipologia"].value_counts())
print("\\nhas_price por faixa de reviews — mostra que a cobertura NÃO é aleatória:")
df["rev_bucket"] = pd.cut(df["number_of_reviews"], [-1, 0, 5, 20, 50, 600], labels=["0", "1-5", "6-20", "21-50", "50+"])
print(df.groupby("rev_bucket", observed=True)["has_price"].agg(["mean", "count"]))
""")

md("""
**Dois achados de contexto guardados pra fase 6 (posicionamento sobre a tese):**
- Centro é bairro minoritário na oferta: 657 de 4.441 anúncios (14,8%), contra 64% em Meia Praia.
- Compactos (0-1 quarto) são 13,6% da oferta Airbnb, mas só 4,9% do estoque à venda no VivaReal
  — o funil de imóveis compráveis já é apertado antes de qualquer análise de receita.

**Padrão de preço por noite (Centro vs Meia Praia, mesma tipologia):** testado com
Mann-Whitney U — Centro precifica ~20-25% mais caro que Meia Praia em 1 e 2 quartos
(p<0.01, estatisticamente significativo); em 3 quartos a diferença não é significativa
(p=0,127, n pequeno). Esse prêmio de preço por noite é real — mas, como a fase 4 mostra, não
vira mais receita anual.
""")

# ============================================================
md("""
## Fase 3 — Proxy de receita e ocupação

Duas formas independentes de estimar ocupação, ambas calculadas e comparadas como checagem
cruzada (decisão do usuário, turno 4-5 do ai-log — nenhuma delas é descartada, a divergência
entre as duas é reportada como limitação, não escondida):

**A) Método review-rate (Inside Airbnb, [insideairbnb.com/data-assumptions](https://insideairbnb.com/data-assumptions/)):**
50% dos hóspedes deixam review, 3 noites por reserva (padrão), ocupação capada em 70%.
`noites_ocupadas/ano ≈ (reviews / anos_ativo) / 0,5 × 3`. Usa o histórico completo do anúncio
— é o proxy PRINCIPAL, usado pra receita anual e yield.

Ajuste pedido pelo usuário: anúncios com preço mas 0 reviews (21 casos — prováveis anúncios
novos e ativos) são marcados "dado insuficiente" (NaN), não zerados — zerar sub-estimaria
anúncios novos de forma incorreta.

**B) Proxy de calendário:** compara a 1ª captura do Price_AV (06 ou 07/jan/2025) com a última
(20/jan/2025) — uma data que tinha preço na 1ª captura e sumiu na 3ª é contada como "provável
reserva" no intervalo. Mede ritmo de reserva em ALTA TEMPORADA (~2 semanas), não dá pra
anualizar direto (extrapolar linearmente daria >100% de ocupação). Usado só como checagem de
robustez, não como receita.

**As duas divergem entre si** (correlação de Spearman ≈ -0,02 — praticamente zero, confirmado
com cross-tab de quartis, não é bug). Interpretação mais provável: medem fenômenos diferentes
(ritmo atual em pico de temporada vs. média histórica de longo prazo).
""")

code("""
df["tenure_anos"] = (df["years_host"] + df["months_host"] / 12).clip(lower=0.25)
df["dado_insuficiente_receita"] = df["has_price"] & (df["number_of_reviews"] == 0)

REVIEW_RATE = 0.5
NOITES_POR_RESERVA = 3
reviews_por_ano = df["number_of_reviews"] / df["tenure_anos"]
occ_rate_raw = (reviews_por_ano / REVIEW_RATE * NOITES_POR_RESERVA / 365).clip(upper=0.70)
df["occ_rate_C"] = np.where(df["dado_insuficiente_receita"], np.nan, occ_rate_raw)
df["receita_anual_C"] = np.where(df["has_price"] & ~df["dado_insuficiente_receita"],
                                  df["occ_rate_C"] * 365 * df["preco_noite"], np.nan)

print("Com receita anual válida:", df["receita_anual_C"].notna().sum(), "de", df["has_price"].sum(), "com preço")
print("Marcados 'dado insuficiente' (não entram no ranking de receita):", df["dado_insuficiente_receita"].sum())
""")

code("""
# Proxy B — calendário: datas visíveis na 1a captura (jan6/jan7) que sumiram na ultima (jan20)
import datetime
price_local = price.copy()
price_local["date"] = pd.to_datetime(price_local["date"])
price_local["capture"] = pd.to_datetime(price_local["aquisition_date"]).dt.date
JAN6, JAN7, JAN20 = datetime.date(2025, 1, 6), datetime.date(2025, 1, 7), datetime.date(2025, 1, 20)
g = price_local.groupby(["airbnb_listing_id", "capture"])["date"].apply(set)

resultados = []
for lid in price_local["airbnb_listing_id"].unique():
    day0 = g.get((lid, JAN6))
    if day0 is None:
        day0 = g.get((lid, JAN7))
    day1 = g.get((lid, JAN20))
    if day0 is None or day1 is None:
        continue
    comparable = {d for d in day0 if d.date() > JAN20}
    if len(comparable) < 10:
        continue
    booked = comparable - day1
    resultados.append((lid, len(comparable), len(booked) / len(comparable)))

occ_janela = pd.DataFrame(resultados, columns=["airbnb_listing_id", "n_comparable", "occ_proxy_janela"])
print("Listings com proxy de calendário calculável:", len(occ_janela))
print(occ_janela["occ_proxy_janela"].describe())

both = df.merge(occ_janela, on="airbnb_listing_id", how="inner")
both = both[both["occ_rate_C"].notna()]
from scipy import stats as sstats
rho, p = sstats.spearmanr(both["occ_rate_C"], both["occ_proxy_janela"])
print(f"\\nCorrelação Spearman entre os dois proxies (n={len(both)}): {rho:.3f} — praticamente zero")
""")

# ============================================================
md("""
## Fase 4 — Segmentação bairro × tipologia

Critério de "melhor perfil" definido com o usuário (turno 5 do ai-log): receita anual
(proxy A) combinada com robustez de amostra. **Só entram na recomendação segmentos com no
mínimo 15 anúncios com dado de preço** — abaixo disso, aparecem na tabela mas ficam marcados
como não-elegíveis (ruído demais pra confiar).
""")

code("""
seg = df.groupby(["suburb", "tipologia"]).agg(
    n_total=("airbnb_listing_id", "count"),
    n_com_price=("has_price", "sum"),
    n_dado_insuficiente=("dado_insuficiente_receita", "sum"),
    n_receita_valida=("receita_anual_C", lambda s: s.notna().sum()),
    receita_anual_mediana=("receita_anual_C", "median"),
    preco_noite_mediano=("preco_noite", "median"),
).reset_index()
seg["usa_para_recomendacao"] = seg["n_com_price"] >= 15
seg = seg.sort_values(["usa_para_recomendacao", "receita_anual_mediana"], ascending=[False, False])

print("Segmentos elegíveis (n_com_price >= 15), ordenados por receita anual mediana:")
print(seg[seg["usa_para_recomendacao"]].to_string(index=False))
""")

md("""
**Achado central (turno 5 do ai-log):** Centro/1-quarto — o coração da tese interna da
Seazone — é o PIOR dos 8 segmentos elegíveis em receita anual, mesmo cobrando o preço por
noite mais alto entre os 1-quartos. O prêmio de preço por noite do Centro não virou mais
receita anual. Mecanismo (confirmado mais abaixo, fase 6): 1-quarto tem o preço/noite mais
baixo de todas as tipologias, e essa perda não é compensada por ocupação maior nem por
desconto proporcional no preço de compra.
""")

# ============================================================
md("""
## Fase 5 — Cruzamento com VivaReal (yield)

Normalização de bairro (acentuação/maiúsculas), filtro pra `listing_type == "apartamento"`
(88-100% de cobertura nos nossos segmentos-alvo). **Dedupe importante:** o VivaReal tem
anúncios repostados (mesmo preço+área+anunciante+título, `listing_id` diferente) — rodamos o
dedupe forte na base INTEIRA antes de segmentar (o usuário pegou dois erros meus aqui: primeiro
eu só checava impacto na mediana, não no N; depois eu tinha deduplicado só o Morretes, o que
tornava a comparação de N injusta com os outros segmentos — ambos corrigidos, ver turnos 9-10
do ai-log).

**Outro achado de qualidade de dado:** as colunas de condomínio e IPTU têm ~30% de valores
placeholder (0 ou 1) misturados com valores reais — tratados como "não informado" antes de
calcular custo anual.
""")

code("""
viva = pd.read_csv(D+"VivaReal_Itapema.csv", dtype={"listing_id": str}).drop_duplicates(
    subset=["listing_id", "sale_price", "aquisition_date"])
viva["sale_price"] = pd.to_numeric(viva["sale_price"], errors="coerce")
condo = pd.to_numeric(viva["monthly_condo_fee"], errors="coerce")
viva["condo_clean"] = condo.where(condo > 1)
iptu = pd.to_numeric(viva["yearly_iptu"], errors="coerce")
viva["iptu_clean"] = iptu.where(iptu > 1)

def norm_bairro(s):
    if pd.isna(s):
        return None
    mapping = {"meia praia": "Meia Praia", "meia praia - frente mar": "Meia Praia",
               "centro": "Centro", "morretes": "Morretes"}
    return mapping.get(str(s).strip().lower(), s)
viva["bairro_norm"] = viva["suburb"].apply(norm_bairro)
viva["tipologia"] = viva["bedrooms"].apply(tipologia)

# dedupe forte na base INTEIRA, antes de segmentar
key_forte = ["sale_price", "usable_area", "advertiser_name", "listing_title"]
n_antes = len(viva)
viva_dedup = viva.drop_duplicates(subset=key_forte).copy()
print(f"Dedupe forte (base inteira): {n_antes} -> {len(viva_dedup)} linhas "
      f"({n_antes - len(viva_dedup)} removidas, {(n_antes - len(viva_dedup)) / n_antes * 100:.1f}%)")

apto = viva_dedup[viva_dedup["listing_type"] == "apartamento"]
""")

code("""
elegiveis = seg[seg["usa_para_recomendacao"]]
rows = []
for _, r in elegiveis.iterrows():
    sub = apto[(apto["bairro_norm"] == r["suburb"]) & (apto["tipologia"] == r["tipologia"])]
    preco_venda = sub["sale_price"].median()
    condo_m = sub["condo_clean"].median()
    iptu_m = sub["iptu_clean"].median()
    receita = r["receita_anual_mediana"]
    yield_bruto = receita / preco_venda * 100
    custo_anual = (condo_m * 12 if pd.notna(condo_m) else 0) + (iptu_m if pd.notna(iptu_m) else 0)
    yield_liq = (receita - custo_anual) / preco_venda * 100
    rows.append(dict(bairro=r["suburb"], tipologia=r["tipologia"], n_vivareal=len(sub),
                      receita_anual=receita, preco_venda=preco_venda, yield_bruto=yield_bruto,
                      condo_mensal=condo_m, iptu_anual=iptu_m, yield_liquido=yield_liq))
yld = pd.DataFrame(rows).sort_values("yield_bruto", ascending=False)
print(yld.to_string(index=False))
""")

md("""
**Morretes/2-quartos dispara na frente** — yield bruto 2,3%, líquido (após condomínio+IPTU)
1,7%, quase o dobro do 2º colocado. Não é a maior amostra do cruzamento (Meia Praia/3q e /4+
quartos têm N maior — confirmado depois do dedupe justo), mas tem amostra robusta (914, muito
acima do mínimo de 15) e o melhor yield por larga margem — tamanho de amostra não é o que
decide esse ranking.

**Centro/1-quarto e Meia Praia/1-quarto são os dois únicos segmentos com yield líquido
negativo** — o problema não é exclusivo do Centro, é do 1-quarto como tipologia, em qualquer
bairro medido com confiança.
""")

# ============================================================
md("""
## Fase 6 — Testando a tese do Centro

A tese interna da Seazone junta duas apostas: **tipo de imóvel** (compacto = studio/1-quarto)
e **localização** (Centro). Testamos as duas separadamente.
""")

code("""
print("=== Mecanismo: preço, receita e ocupação por tipologia (pooled, todos os bairros) ===")
print(df.groupby("tipologia")["preco_noite"].agg(["count", "median"]))
print()
print(df.groupby("tipologia")["receita_anual_C"].agg(["count", "median"]))
print()
occw_all = df.merge(occ_janela, on="airbnb_listing_id", how="left")
print(occw_all.groupby("tipologia")["occ_proxy_janela"].agg(["count", "median"]))
""")

md("""
**Tipo de imóvel (compacto) — REFUTADA.** 1-quarto é a pior tipologia em receita anual
(mediana R$7.628, a menor de todas), apesar de ter a MAIOR taxa de reserva em alta temporada
entre as tipologias confiáveis (14,3% mediana no proxy de calendário) — não é problema de
ocupação, é puramente de preço por noite baixo (R$390 mediana) não compensado por desconto
proporcional no preço de compra (um 1-quarto custa ~77-81% do preço de um 2-quarto pra ganhar
só ~45-56% da receita). O componente "studio" da tese é literalmente intestável — 3 anúncios
no Centro inteiro, 0 com dado de receita.

**Localização (Centro vs Meia Praia, dentro do 1-quarto) — empate, não refutada claramente.**
Centro precifica ~20-25% mais caro por noite (significativo, p<0.01). Em receita anual bruta
Centro perde. Mas no yield líquido — a métrica mais próxima de retorno de investimento —
Centro (-0,07%) e Meia Praia (-0,16%) estão praticamente empatados, os dois no vermelho.

**Posição:** a tese erra mais no "o quê" comprar (tipo compacto) do que no "onde" (Centro).
Recomendar compacto — Centro ou não — não se sustenta nos dados. O Centro não é o vilão
sozinho, é o pior exemplo específico de uma categoria de imóvel que já não funciona bem em
lugar nenhum do dataset com amostra confiável.
""")

# ============================================================
md("""
## Fase 7 — Recomendação final

**Perfil recomendado: apartamento de 2 quartos em Morretes.** Combina receita razoável (2º
lugar entre os 8 segmentos elegíveis, R$18.333/ano) com o preço de compra mais baixo do grupo
(R$790.000 mediana) — é essa combinação, não receita isolada, que faz o yield vencer.

Exemplos concretos próximos da mediana (dois anúncios reais, anunciantes diferentes):
- R$790.000, 68m², condomínio R$350/mês — Nei Costa
- R$790.000, 67m², condomínio R$400/mês, "novo pronto pra morar" — REDE MOI

**Estimativa de retorno, sem inflar:** yield líquido 1,7% → payback de ~59 anos só de aluguel.
Isso é a melhor opção RELATIVA do dataset, não um retorno excelente em termos absolutos — todo
o mercado de Itapema mostrou yield de STR baixo pro padrão do setor (0,6%-2,3% bruto em todos
os 8 segmentos), o que sugere preço de compra inflado na região e/ou proxy de receita
conservador (baseado em desempenho de host mediano, não de operação profissional).

**Duas ressalvas que puxam em direções opostas** (sem forma de saber qual pesa mais):
o preço do VivaReal é o anunciado, não o vendido — no Brasil geralmente vende mais barato, o
retorno real tende a ser um pouco MELHOR; mas o yield líquido calculado só desconta
condomínio e IPTU, não taxa de plataforma, limpeza nem administração — o retorno real tende a
ser um pouco PIOR na prática.

Os gráficos-chave estão em `figures/` e a tabela de apoio completa (65 segmentos, elegíveis e
não) está em `resumo.csv`.
""")

code("""
# Os graficos finais (figures/01 a 05) e o resumo.csv sao gerados por make_charts.py,
# que reusa exatamente as tabelas 'seg' e 'yld' construidas acima.
import os
print("Gráficos disponíveis em figures/:")
for f in sorted(os.listdir("figures")):
    print(" -", f)
""")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

with open("analise.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Notebook criado com {len(cells)} células.")
