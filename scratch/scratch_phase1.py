import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.float_format', lambda x: f'{x:,.1f}')

D = "data/"

def sep(t):
    print("\n"+"="*95); print(t); print("="*95)

details = pd.read_csv(D+"Details_Itapema.csv", dtype={"airbnb_listing_id": str, "owner_id": str})
mesh = pd.read_csv(D+"Mesh_Ids_Data_Itapema.csv", dtype={"airbnb_listing_id": str})
price = pd.read_csv(D+"Price_AV_Itapema.csv", dtype={"airbnb_listing_id": str})
hosts_raw = pd.read_csv(D+"Hosts_ids_Itapema.csv", dtype={"owner_id": str})

# dedupe hosts (keep latest snapshot)
hosts_raw["host_snapshot_date"] = pd.to_datetime(hosts_raw["host_snapshot_date"])
hosts = hosts_raw.sort_values("host_snapshot_date").drop_duplicates("owner_id", keep="last").drop(
    columns=["response_rate_shown","response_time_shown"])

df = details.merge(mesh[["airbnb_listing_id","suburb"]], on="airbnb_listing_id", how="left") \
            .merge(hosts, on="owner_id", how="left")

has_price_ids = set(price["airbnb_listing_id"].unique())
df["has_price"] = df["airbnb_listing_id"].isin(has_price_ids)

# tipologia
def tipologia(n):
    if n == 0: return "studio (0q)"
    if n == 1: return "1 quarto"
    if n == 2: return "2 quartos"
    if n == 3: return "3 quartos"
    return "4+ quartos"
df["tipologia"] = df["number_of_bedrooms"].apply(tipologia)
df["compacto"] = df["number_of_bedrooms"] <= 1

# host multi-listing
owner_counts = details["owner_id"].value_counts()
df["host_multi_listing"] = df["owner_id"].map(owner_counts) > 1

sep("1. POPULACAO TOTAL x TIPOLOGIA (contagem e % com price)")
t = df.groupby("tipologia").agg(n=("airbnb_listing_id","count"), pct_com_price=("has_price","mean")).sort_index()
t["pct_pop"] = (t["n"]/len(df)*100).round(1)
print(t)

sep("2. POPULACAO TOTAL x BAIRRO (top 6, contagem e % com price)")
b = df.groupby("suburb").agg(n=("airbnb_listing_id","count"), pct_com_price=("has_price","mean")).sort_values("n", ascending=False)
b["pct_pop"] = (b["n"]/len(df)*100).round(1)
print(b.head(8))

sep("3. INTERSECAO bairro x tipologia (contagem de anuncios) - onde a tese vive")
pivot_n = pd.pivot_table(df, index="suburb", columns="tipologia", values="airbnb_listing_id", aggfunc="count", fill_value=0)
pivot_n = pivot_n.loc[b.head(6).index]
print(pivot_n)

sep("3b. INTERSECAO bairro x tipologia - % com price (tamanho de amostra pra receita)")
pivot_hp = pd.pivot_table(df, index="suburb", columns="tipologia", values="has_price", aggfunc="mean")
pivot_hp = pivot_hp.loc[b.head(6).index].round(2)
print(pivot_hp)
sep("3c. INTERSECAO bairro x tipologia - N com price (contagem absoluta, essa e a amostra real)")
pivot_hpn = pd.pivot_table(df, index="suburb", columns="tipologia", values="has_price", aggfunc="sum")
pivot_hpn = pivot_hpn.loc[b.head(6).index]
print(pivot_hpn)

sep("4. listing_type distribuicao (pop total x has_price)")
lt = df.groupby("listing_type").agg(n=("airbnb_listing_id","count"), pct_com_price=("has_price","mean"))
print(lt.sort_values("n", ascending=False))

sep("5. QUALIDADE: star_rating so listings com >=1 review (pop total x has_price)")
rated = df[df["number_of_reviews"]>0]
print("rated n:", len(rated), " sem review n:", (df['number_of_reviews']==0).sum())
print(rated.groupby("has_price")["star_rating"].describe()[["count","mean","50%","min","max"]])

sep("5b. is_guest_favorite e is_new_listing por has_price")
print(df.groupby("has_price")[["is_guest_favorite"]].mean())
print(df.groupby("has_price")["is_new_listing"].mean())

sep("6. HOSTS: superhost, years_host, multi-listing, is_professional -- pop total x has_price")
print(df.groupby("has_price").agg(
    superhost_pct=("is_superhost","mean"),
    years_host_med=("years_host","median"),
    multi_listing_pct=("host_multi_listing","mean"),
    professional_pct=("is_professional","mean"),
    reviews_med=("number_of_reviews","median"),
))

sep("7. PRECO (so entre quem tem price_AV, n=1005 listings) -- mediana de preco por listing")
price_per_listing = price.groupby("airbnb_listing_id")["price"].median().rename("preco_mediano_noite")
dfp = df.merge(price_per_listing, on="airbnb_listing_id", how="inner")
print("n listings com preco:", len(dfp))
print(dfp["preco_mediano_noite"].describe())

sep("7b. PRECO mediano por TIPOLOGIA (entre quem tem price)")
print(dfp.groupby("tipologia")["preco_mediano_noite"].agg(["count","median","mean"]).sort_index())

sep("7c. PRECO mediano por BAIRRO (top 6, entre quem tem price)")
print(dfp[dfp["suburb"].isin(b.head(6).index)].groupby("suburb")["preco_mediano_noite"].agg(["count","median","mean"]).sort_values("median", ascending=False))

sep("7d. PRECO mediano: bairro x tipologia (celula = mediana; so onde ha >=3 obs)")
cell_n = pd.pivot_table(dfp, index="suburb", columns="tipologia", values="preco_mediano_noite", aggfunc="count")
cell_med = pd.pivot_table(dfp, index="suburb", columns="tipologia", values="preco_mediano_noite", aggfunc="median")
cell_med_masked = cell_med.where(cell_n>=3)
print("N por celula:")
print(cell_n.loc[[x for x in b.head(6).index if x in cell_n.index]])
print("\nMediana por celula (NaN = menos de 3 obs):")
print(cell_med_masked.loc[[x for x in b.head(6).index if x in cell_med_masked.index]])

sep("8. Outlier check: excluindo os 4 listings com preco extremo (>=5000), preco mediano muda muito?")
outlier_ids = price.loc[price["price"]>=5000, "airbnb_listing_id"].unique()
print("listings outliers:", len(outlier_ids), "de", dfp['airbnb_listing_id'].nunique())
dfp_clean = dfp[~dfp["airbnb_listing_id"].isin(outlier_ids)]
print("mediana geral com outliers:", dfp["preco_mediano_noite"].median(), " sem outliers:", dfp_clean["preco_mediano_noite"].median())
print("media geral com outliers:", dfp["preco_mediano_noite"].mean().round(1), " sem outliers:", dfp_clean["preco_mediano_noite"].mean().round(1))
EOF_MARK = None
