import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ---- paleta (references/palette.md, modo light) ----
SURFACE   = "#fcfcfb"
INK_PRI   = "#0b0b0b"
INK_SEC   = "#52514e"
INK_MUTED = "#898781"
GRID      = "#e1e0d9"
BASELINE  = "#c3c2b7"
BLUE      = "#2a78d6"   # slot 1
ORANGE    = "#eb6834"   # slot 2
AQUA      = "#1baf7a"   # slot 3
RED       = "#e34948"   # diverging pole / negativo
GOOD      = "#0ca30c"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "text.color": INK_PRI,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_SEC,
    "xtick.color": INK_SEC,
    "ytick.color": INK_SEC,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})

BAIRRO_COLOR = {"Meia Praia": BLUE, "Centro": ORANGE, "Morretes": AQUA}

def clean_ax(ax, keep_left=False):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if not keep_left:
        ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    if keep_left:
        ax.spines["left"].set_color(BASELINE)
    ax.tick_params(length=0)

# =========================================================
# Dados
# =========================================================
seg = pd.read_csv("/tmp/segmentacao_fase4.csv")
elig = seg[seg["usa_para_recomendacao"]].copy()
elig["label"] = elig["suburb"] + " · " + elig["tipologia"]
elig = elig.sort_values("receita_anual_mediana", ascending=True)

yld = pd.read_csv("/tmp/yield_fase5_dedup_correto.csv")  # dedupe forte aplicado na base VivaReal inteira antes de segmentar
yld["n_vivareal"] = yld["n_vivareal_dedup"]
yld["label"] = yld["bairro"] + " · " + yld["tipologia"]
yld = yld.sort_values("yield_liquido", ascending=True)

# =========================================================
# GRAFICO 1 - Receita anual mediana por segmento (bairro x tipologia)
# =========================================================
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=200)
colors = [BAIRRO_COLOR.get(b, INK_MUTED) for b in elig["suburb"]]
bars = ax.barh(elig["label"], elig["receita_anual_mediana"], color=colors, height=0.62)
for b, v, n in zip(bars, elig["receita_anual_mediana"], elig["n_com_price"]):
    ax.text(v + 400, b.get_y() + b.get_height()/2, f"R$ {v:,.0f}".replace(",", "."),
            va="center", ha="left", fontsize=9.5, color=INK_PRI)
ax.set_xlim(0, elig["receita_anual_mediana"].max()*1.22)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{x/1000:.0f}k"))
ax.set_xlabel("Receita anual mediana estimada (R$) — método review-rate")
clean_ax(ax)
ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
handles = [plt.Rectangle((0,0),1,1, color=c) for c in [BLUE, ORANGE, AQUA]]
ax.legend(handles, ["Meia Praia", "Centro", "Morretes"], loc="lower right", frameon=False, fontsize=9.5)
ax.set_title("Receita anual estimada por bairro × tipologia\n(só segmentos com ≥15 anúncios com dado de preço)",
             loc="left", fontsize=12.5, color=INK_PRI, pad=14)
plt.tight_layout()
plt.savefig("figures/01_receita_por_segmento.png")
plt.close()

# =========================================================
# GRAFICO 2 - Yield bruto vs liquido por segmento
# =========================================================
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=200)
y_pos = np.arange(len(yld))
h = 0.34
ax.barh(y_pos+h/2, yld["yield_bruto"], height=h, color=INK_MUTED, label="Yield bruto")
liq_colors = [GOOD if v >= 0 else RED for v in yld["yield_liquido"]]
ax.barh(y_pos-h/2, yld["yield_liquido"], height=h, color=liq_colors, label="Yield líquido (–condomínio –IPTU)")
ax.axvline(0, color=BASELINE, linewidth=1)
ax.set_yticks(y_pos); ax.set_yticklabels(yld["label"])
for yi, vb, vl in zip(y_pos, yld["yield_bruto"], yld["yield_liquido"]):
    ax.text(vb + 0.05, yi+h/2, f"{vb:.1f}%", va="center", fontsize=8.5, color=INK_SEC)
    ax.text((vl + 0.05) if vl>=0 else (vl-0.05), yi-h/2, f"{vl:.1f}%", va="center",
            ha="left" if vl>=0 else "right", fontsize=8.5, color=INK_PRI)
ax.set_xlabel("Yield anual (%) sobre preço de venda mediano do VivaReal")
clean_ax(ax)
ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
import matplotlib.patches as mpatches
handles = [mpatches.Patch(color=INK_MUTED, label="Yield bruto"),
           mpatches.Patch(color=GOOD, label="Yield líquido ≥ 0"),
           mpatches.Patch(color=RED, label="Yield líquido < 0")]
ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=9)
ax.set_title("Yield bruto e líquido por segmento\n1-quarto é o único grupo que fica negativo no líquido — em qualquer bairro",
             loc="left", fontsize=12.5, color=INK_PRI, pad=14)
plt.tight_layout()
plt.savefig("figures/02_yield_bruto_liquido.png")
plt.close()

# =========================================================
# GRAFICO 3 - Preco de compra x Receita anual (mapa de yield)
# =========================================================
m = yld.merge(elig[["suburb","tipologia","n_com_price"]], left_on=["bairro","tipologia"], right_on=["suburb","tipologia"], how="left")
fig, ax = plt.subplots(figsize=(9.5, 6.4), dpi=200)
for bairro, sub in m.groupby("bairro"):
    ax.scatter(sub["preco_venda"], sub["receita_anual"], s=sub["n_vivareal"].clip(upper=800)/2 + 60,
               color=BAIRRO_COLOR.get(bairro, INK_MUTED), alpha=0.85, edgecolor="white", linewidth=0.8,
               label=bairro, zorder=3)
    for _, r in sub.iterrows():
        ax.annotate(r["tipologia"].replace(" quartos","q").replace(" quarto","q").replace("studio (0q)","studio"),
                    (r["preco_venda"], r["receita_anual"]), textcoords="offset points", xytext=(7,4),
                    fontsize=8.3, color=INK_SEC)
# linhas de yield de referencia (isolinhas simples)
xs = np.linspace(1, m["preco_venda"].max()*1.05, 50)
for y_ref, lbl in [(0.023, "yield 2,3%"), (0.009, "yield 0,9%")]:
    ax.plot(xs, xs*y_ref, linestyle="--", linewidth=0.9, color=GRID, zorder=1)
    ax.text(xs[-1], xs[-1]*y_ref, lbl, fontsize=7.5, color=INK_MUTED, ha="right", va="bottom")
ax.set_xlabel("Preço de venda mediano — VivaReal (R$)")
ax.set_ylabel("Receita anual estimada (R$)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{x/1e6:.1f}M" if x>=1e6 else f"{x/1000:.0f}k"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"{x/1000:.0f}k"))
clean_ax(ax, keep_left=True)
ax.grid(color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
ax.legend(loc="upper left", frameon=False, fontsize=9.5)
ax.set_title("Preço de compra × receita anual — o mapa do yield\nMorretes/2q: receita média, imóvel mais barato do grupo (bolha = nº à venda)",
             loc="left", fontsize=11.3, color=INK_PRI, pad=14)
plt.tight_layout()
plt.savefig("figures/03_mapa_yield.png")
plt.close()

# =========================================================
# GRAFICO 4 - A tese: Centro vs Meia Praia no 1-quarto
# =========================================================
c1 = elig[(elig["suburb"]=="Centro") & (elig["tipologia"]=="1 quarto")].iloc[0]
m1 = elig[(elig["suburb"]=="Meia Praia") & (elig["tipologia"]=="1 quarto")].iloc[0]
y_c1 = yld[(yld["bairro"]=="Centro") & (yld["tipologia"]=="1 quarto")].iloc[0]
y_m1 = yld[(yld["bairro"]=="Meia Praia") & (yld["tipologia"]=="1 quarto")].iloc[0]

fig, axes = plt.subplots(1, 3, figsize=(11, 4.3), dpi=200)
paineis = [
    ("Preço por noite\n(mediana, R$)", [c1["preco_noite_mediano"], m1["preco_noite_mediano"]], "R$"),
    ("Receita anual estimada\n(R$)", [c1["receita_anual_mediana"], m1["receita_anual_mediana"]], "R$"),
    ("Yield líquido\n(%)", [y_c1["yield_liquido"], y_m1["yield_liquido"]], "%"),
]
labels = ["Centro\n1 quarto", "Meia Praia\n1 quarto"]
cores = [ORANGE, BLUE]
for ax, (titulo, valores, unidade) in zip(axes, paineis):
    bars = ax.bar(labels, valores, color=cores, width=0.55, zorder=3)
    if unidade == "%":
        ax.axhline(0, color=BASELINE, linewidth=1)
    for b, v in zip(bars, valores):
        va = "bottom" if v >= 0 else "top"
        off = (max(map(abs,valores))*0.04) * (1 if v>=0 else -1)
        txt = f"{v:.1f}%" if unidade=="%" else f"R$ {v:,.0f}".replace(",", ".")
        ax.text(b.get_x()+b.get_width()/2, v+off, txt, ha="center", va=va, fontsize=9.5, color=INK_PRI)
    ax.set_title(titulo, fontsize=10.5, color=INK_SEC)
    clean_ax(ax)
    ax.set_yticks([])
fig.suptitle("A tese do Centro, no 1-quarto: preço maior não virou receita nem yield melhor",
             fontsize=12.5, color=INK_PRI, x=0.02, ha="left", y=1.02)
plt.tight_layout()
plt.savefig("figures/04_tese_centro_1quarto.png", bbox_inches="tight")
plt.close()

# =========================================================
# GRAFICO 5 (metodologico) - divergencia dos dois proxies de ocupacao
# =========================================================
df = pd.read_csv("/tmp/df_listing_level_fase4.csv", dtype={"airbnb_listing_id":str})
occw = pd.read_csv("/tmp/occ_proxy_check.csv", dtype={"airbnb_listing_id":str})
both = df.merge(occw[["airbnb_listing_id","occ_proxy_janela"]], on="airbnb_listing_id", how="inner")
both = both[both["occ_rate_C"].notna()]

fig, ax = plt.subplots(figsize=(8.5, 6.4), dpi=200)
ax.scatter(both["occ_rate_C"]*100, both["occ_proxy_janela"]*100, s=26, color=BLUE, alpha=0.45,
           edgecolor="none", zorder=3)
from scipy import stats as sstats
rho, p = sstats.spearmanr(both["occ_rate_C"], both["occ_proxy_janela"])
ax.set_xlabel("Ocupação anual estimada — método reviews (%)")
ax.set_ylabel("Taxa de reserva — janela de calendário, 2 semanas (%)")
clean_ax(ax, keep_left=True)
ax.grid(color=GRID, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
ax.text(0.97, 0.95, f"correlação (Spearman) = {rho:.2f}\n(praticamente zero)", transform=ax.transAxes,
        ha="right", va="top", fontsize=10, color=INK_SEC,
        bbox=dict(boxstyle="round,pad=0.4", facecolor=SURFACE, edgecolor=GRID))
ax.set_title("Os dois proxies de ocupação não concordam entre si\ncada ponto é um anúncio (n=%d) — usados como checagem cruzada, nunca um sozinho" % len(both),
             loc="left", fontsize=11, color=INK_PRI, pad=14)
plt.tight_layout()
plt.savefig("figures/05_divergencia_proxies.png")
plt.close()

print("Gráficos salvos em figures/:")
import os
for f in sorted(os.listdir("figures")):
    print(" -", f)
