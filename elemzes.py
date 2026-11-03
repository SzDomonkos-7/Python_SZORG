"""
Robotos sci-fi könyvek elemzése (Goodreads adatok – sf_robots.csv)

Használt könyvtárak: NumPy, Pandas, Plotly
Futtatás:  py elemzes.py
Az ábrák az `abrak/` mappába kerülnek interaktív HTML fájlként.
"""

import ast
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ADAT = Path(__file__).parent / "sf_robots.csv"
ABRAK = Path(__file__).parent / "abrak"
ABRAK.mkdir(exist_ok=True)

MIN_SZAVAZAT = 10


def cim(szoveg):
    print("\n" + "=" * 80)
    print(szoveg)
    print("=" * 80)


def mentes(fig, nev):
    utvonal = ABRAK / f"{nev}.html"
    fig.write_html(utvonal, include_plotlyjs="cdn")
    print(f"  -> ábra mentve: {utvonal.relative_to(Path(__file__).parent)}")


# ---------------------------------------------------------------------------
# Adatok betöltése és tisztítása
# ---------------------------------------------------------------------------
cim("Adatok betöltése és tisztítása")

df = pd.read_csv(ADAT)
print(f"Nyers adathalmaz: {df.shape[0]} sor, {df.shape[1]} oszlop")

# A 0-s megjelenési év hiányzó adatot jelent
df["Year_published"] = df["Year_published"].replace(0, np.nan)

# A műfaj oszlop szótárként tárolt szöveg: {'Science Fiction': 6502, ...}
df["Genres_dict"] = df["Genres"].apply(
    lambda s: {k.strip(): v for k, v in ast.literal_eval(s).items()}
)

# Származtatott oszlopok
df["log_votes"] = np.log10(df["Rating_votes"].clip(lower=1))
df["Decade"] = (df["Year_published"] // 10 * 10).astype("Int64")
df["Review_ratio"] = np.where(
    df["Rating_votes"] > 0, df["Review_number"] / df["Rating_votes"], np.nan
)

# Megbízható értékelésű könyvek
megb = df[df["Rating_votes"] >= MIN_SZAVAZAT].copy()
print(f"Legalább {MIN_SZAVAZAT} szavazattal rendelkező könyvek: {len(megb)}")
print(f"Hiányzó megjelenési év: {df['Year_published'].isna().sum()} könyv")


# ---------------------------------------------------------------------------
# 1. kérdés: Népszerűség és értékelés
# ---------------------------------------------------------------------------
cim("1. Jobb értékelést kapnak-e a népszerűbb (több szavazatot kapott) könyvek?")

r_lin = np.corrcoef(megb["Rating_votes"], megb["Rating_score"])[0, 1]
r_log = np.corrcoef(megb["log_votes"], megb["Rating_score"])[0, 1]
print(f"Pearson-korreláció (szavazatszám ~ értékelés):        r = {r_lin:.3f}")
print(f"Pearson-korreláció (log10 szavazatszám ~ értékelés):  r = {r_log:.3f}")

# Népszerűségi kategóriák: az értékelés szórása hogyan változik?
megb["Nepszeruseg"] = pd.cut(
    megb["Rating_votes"],
    bins=[9, 100, 1_000, 10_000, np.inf],
    labels=["10–100", "100–1 000", "1 000–10 000", "10 000+"],
)
nep_tabla = megb.groupby("Nepszeruseg", observed=True)["Rating_score"].agg(
    ["count", "mean", "std", "min", "max"]
).round(3)
print(nep_tabla)

meredekseg, tengely = np.polyfit(megb["log_votes"], megb["Rating_score"], 1)
x = np.linspace(megb["log_votes"].min(), megb["log_votes"].max(), 100)

fig = px.scatter(
    megb, x="log_votes", y="Rating_score", hover_name="Book_Title",
    hover_data=["Author_Name", "Rating_votes"], opacity=0.55,
    labels={"log_votes": "Szavazatok száma (log10)", "Rating_score": "Átlagos értékelés"},
    title=f"Népszerűség és értékelés kapcsolata (r = {r_log:.2f})",
)
fig.add_trace(go.Scatter(x=x, y=meredekseg * x + tengely, mode="lines",
                         name="Lineáris trend", line=dict(color="red")))
mentes(fig, "1_nepszeruseg_ertekeles")

fig = px.box(megb, x="Nepszeruseg", y="Rating_score", points="outliers",
             labels={"Nepszeruseg": "Szavazatok száma", "Rating_score": "Átlagos értékelés"},
             title="Az értékelések szóródása népszerűségi kategóriánként")
mentes(fig, "1b_nepszeruseg_boxplot")

print(
    "\nVálasz: mérsékelt pozitív kapcsolat van (log skálán r ≈ 0,33). A 10 000+ szavazatos"
    "\nkönyvek átlaga ~4,06, a 100 alattiaké ~3,78. Emellett a SZÓRÁS is csökken:"
    "\nkevés szavazatnál az értékelés szélsőségesebb, sok szavazatnál stabilizálódik."
)


# ---------------------------------------------------------------------------
# 2. kérdés: Időbeli változás
# ---------------------------------------------------------------------------
cim("2. Hogyan változott a robotos könyvek száma és értékelése az évtizedek során?")

evt = (
    megb.dropna(subset=["Decade"])
    .groupby("Decade")
    .agg(konyvek=("Book_Title", "count"),
         atlag_ertekeles=("Rating_score", "mean"),
         median_szavazat=("Rating_votes", "median"))
    .round(2)
)
print(evt)

regi = megb[megb["Year_published"] < 2000]["Rating_score"]
uj = megb[megb["Year_published"] >= 2000]["Rating_score"]
print(f"\n2000 előtti könyvek: n={len(regi)}, átlag={regi.mean():.3f}")
print(f"2000 utáni könyvek:  n={len(uj)}, átlag={uj.mean():.3f}")
print(f"2000 után jelent meg a könyvek {len(uj) / (len(uj) + len(regi)):.0%}-a")

evt_plot = evt.reset_index()
evt_plot["Decade"] = evt_plot["Decade"].astype(int)
fig = go.Figure()
fig.add_bar(x=evt_plot["Decade"], y=evt_plot["konyvek"], name="Könyvek száma", yaxis="y")
fig.add_scatter(x=evt_plot["Decade"], y=evt_plot["atlag_ertekeles"], name="Átlagos értékelés",
                mode="lines+markers", yaxis="y2", line=dict(color="red"))
fig.update_layout(
    title="Robotos könyvek száma és átlagos értékelése évtizedenként",
    xaxis=dict(title="Évtized", dtick=10),
    yaxis=dict(title="Könyvek száma"),
    yaxis2=dict(title="Átlagos értékelés", overlaying="y", side="right", range=[3, 4.5]),
    legend=dict(x=0.01, y=0.99),
)
mentes(fig, "2_evtizedek")

print(
    "\nVálasz: a robotos irodalom a 2000-es, 2010-es években robbant be – a könyvek 82%-a"
    "\nezután jelent meg. Az átlagos értékelés közben stabil (~3,9); kiemelkedik az 1950-es"
    "\névek (Asimov-korszak, 4,11). Az újabb könyvek egyenként jóval kevesebb szavazatot"
    "\nkapnak: több a könyv, így szétoszlik a figyelem (és a régieknek több idejük volt)."
)


# ---------------------------------------------------------------------------
# 3. kérdés: Műfajok
# ---------------------------------------------------------------------------
cim("3. Melyik (al)műfajba tartozó robotos könyveket értékelik a legjobbra?")

mufaj_sorok = [
    {"Mufaj": m, "Rating_score": r, "Rating_votes": v}
    for d, r, v in zip(megb["Genres_dict"], megb["Rating_score"], megb["Rating_votes"])
    for m in d
]
mufaj_df = pd.DataFrame(mufaj_sorok)
mufaj_stat = (
    mufaj_df.groupby("Mufaj")
    .agg(db=("Rating_score", "size"), atlag=("Rating_score", "mean"),
         median_szavazat=("Rating_votes", "median"))
)
mufaj_stat = mufaj_stat[mufaj_stat["db"] >= 40].sort_values("atlag", ascending=False).round(3)
osszatlag = megb["Rating_score"].mean()
mufaj_stat["elteres"] = (mufaj_stat["atlag"] - osszatlag).round(3)

print(f"Összesített átlag: {osszatlag:.3f}")
print("\nLegjobban értékelt műfajok (min. 40 könyv):")
print(mufaj_stat.head(8))
print("\nLeggyengébben értékelt műfajok:")
print(mufaj_stat.tail(8))

ms = mufaj_stat.reset_index().sort_values("elteres")
fig = px.bar(ms, x="elteres", y="Mufaj", orientation="h", color="elteres",
             color_continuous_scale="RdBu", color_continuous_midpoint=0,
             hover_data=["db", "atlag"],
             labels={"elteres": "Eltérés az összátlagtól", "Mufaj": "Műfaj"},
             title=f"Műfajok átlagos értékelése az összátlaghoz ({osszatlag:.2f}) képest")
fig.update_layout(height=900)
mentes(fig, "3_mufajok")

print(
    "\nVálasz: a képregények/grafikus regények/mangák és a klasszikusok kapják a legjobb"
    "\nértékeléseket. A leggyengébbek a kisgyerekeknek szóló képeskönyvek (Picture Books,"
    "\nStorytime), a tini YA, valamint a kifejezetten 'Robots'/'Aliens' címkés könyvek."
)


# ---------------------------------------------------------------------------
# 4. kérdés: Szavazat vs. szöveges kritika
# ---------------------------------------------------------------------------
cim("4. Milyen kapcsolat van a szavazatok és a szöveges kritikák száma között,\n"
    "   és ír-e több kritikát az olvasó az újabb könyvekről?")

r_vr = np.corrcoef(megb["Rating_votes"], megb["Review_number"])[0, 1]
r_vr_log = np.corrcoef(np.log10(megb["Rating_votes"]),
                       np.log10(megb["Review_number"].clip(lower=1)))[0, 1]
print(f"Korreláció szavazat ~ kritika:              r = {r_vr:.3f}")
print(f"Korreláció log(szavazat) ~ log(kritika):    r = {r_vr_log:.3f}")
print(f"Medián kritika/szavazat arány: {megb['Review_ratio'].median():.3f}"
      f"  (kb. minden {1 / megb['Review_ratio'].median():.0f}. értékelő ír kritikát)")

idoszak = pd.cut(megb["Year_published"], bins=[1800, 1980, 2000, 2010, 2025],
                 labels=["1980 előtt", "1980–1999", "2000–2009", "2010 után"])
arany_tabla = megb.groupby(idoszak, observed=True)["Review_ratio"].agg(
    ["count", "median", "mean"]
).round(3)
print("\nKritika/szavazat arány megjelenési időszak szerint:")
print(arany_tabla)

fig = px.scatter(
    megb[megb["Review_number"] > 0], x="Rating_votes", y="Review_number",
    color="Year_published", log_x=True, log_y=True, hover_name="Book_Title",
    color_continuous_scale="Viridis",
    labels={"Rating_votes": "Szavazatok száma", "Review_number": "Kritikák száma",
            "Year_published": "Megjelenés éve"},
    title=f"Szavazatok és szöveges kritikák (log-log, r = {r_vr_log:.2f})",
)
mentes(fig, "4_szavazat_kritika")

fig = px.box(megb.assign(Idoszak=idoszak).dropna(subset=["Idoszak"]),
             x="Idoszak", y="Review_ratio", points=False,
             labels={"Idoszak": "Megjelenés", "Review_ratio": "Kritika / szavazat"},
             title="Hány szöveges kritika jut egy szavazatra?")
fig.update_yaxes(range=[0, 0.3])
mentes(fig, "4b_kritika_arany")

print(
    "\nVálasz: nagyon erős kapcsolat van – ahol sok a szavazat, ott sok a kritika is."
    "\nAz arány viszont időben változik: az újabb könyveknél jóval többen írnak"
    "\nszöveges kritikát, a régi klasszikusokat inkább csak 'csillagozzák'."
)


# ---------------------------------------------------------------------------
# 5. kérdés: Szerzők termékenysége
# ---------------------------------------------------------------------------
cim("5. Jobbak vagy népszerűbbek-e a termékeny szerzők robotos könyvei?")

szerzo = megb.groupby("Author_Name").agg(
    konyvek=("Book_Title", "count"),
    atlag_ertekeles=("Rating_score", "mean"),
    ossz_szavazat=("Rating_votes", "sum"),
    median_szavazat=("Rating_votes", "median"),
)
szerzo["Kategoria"] = pd.cut(szerzo["konyvek"], bins=[0, 1, 3, np.inf],
                             labels=["1 könyv", "2–3 könyv", "4+ könyv"])
kat_tabla = szerzo.groupby("Kategoria", observed=True).agg(
    szerzok=("konyvek", "size"),
    atlag_ertekeles=("atlag_ertekeles", "mean"),
    median_szavazat=("median_szavazat", "median"),
).round(3)
print(kat_tabla)

r_sz = np.corrcoef(szerzo["konyvek"], szerzo["atlag_ertekeles"])[0, 1]
print(f"\nKorreláció könyvszám ~ átlagos értékelés: r = {r_sz:.3f}")

# Az összes szavazat mekkora részét viszi el a top 10 szerző?
top = szerzo.sort_values("ossz_szavazat", ascending=False)
reszesedes = top["ossz_szavazat"].head(10).sum() / top["ossz_szavazat"].sum()
print(f"A top 10 szerző viszi el az összes szavazat {reszesedes:.0%}-át "
      f"({len(szerzo)} szerzőből).")
print(top.head(10)[["konyvek", "atlag_ertekeles", "ossz_szavazat"]].round(2))

fig = px.scatter(
    szerzo.reset_index(), x="konyvek", y="atlag_ertekeles", size="ossz_szavazat",
    size_max=50, hover_name="Author_Name", log_x=True, color="Kategoria",
    labels={"konyvek": "Könyvek száma az adathalmazban",
            "atlag_ertekeles": "Szerző átlagos értékelése", "Kategoria": "Termékenység"},
    title="Szerzők termékenysége és átlagos értékelése (buborékméret = összes szavazat)",
)
mentes(fig, "5_szerzok")

print(
    "\nVálasz: a termékeny szerzők értékelése stabilan átlag körüli/feletti, és"
    "\nkönyveik jellemzően népszerűbbek. A figyelem rendkívül koncentrált:"
    "\nnéhány szerző (pl. Asimov, Meyer, Wells) gyűjti be a szavazatok nagy részét."
)

print("\nAz ábrák az 'abrak' mappában találhatók.")
