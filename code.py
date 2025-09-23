import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# CONSOMMATION ENERGETIQUE

st.set_page_config(layout="wide", page_title="Dashboard Énergie & Pollution")
st.title("Dashboard Consommation Énergétique & Pollution")

df = pd.read_csv("consommation-quotidienne-brute-regionale.csv", sep=";", low_memory=False)

# Nettoyage 
cols_numeriques = [
    "Consommation brute gaz (MW PCS 0°C) - NaTran",
    "Consommation brute gaz (MW PCS 0°C) - Teréga",
    "Consommation brute gaz totale (MW PCS 0°C)",
    "Consommation brute électricité (MW) - RTE",
    "Consommation brute totale (MW)"
]
df[cols_numeriques] = df[cols_numeriques].apply(pd.to_numeric, errors="coerce").fillna(0)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Année"] = df["Date"].dt.year
df["Mois"] = df["Date"].dt.month
df["Jour"] = df["Date"].dt.day
df["Heure"] = pd.to_datetime(df["Heure"], format="%H:%M", errors="coerce").dt.hour
df["DateTime"] = pd.to_datetime(df["Date"].astype(str) + " " + df["Heure"].astype(str) + ":00", errors="coerce")

df["dayofweek"] = df["DateTime"].dt.dayofweek
df["is_weekend"] = df["dayofweek"].isin([5,6])

# Filtres Sidebar
st.sidebar.header("Filtres Consommation")
annees = sorted(df["Année"].dropna().unique())
regions = sorted(df["Région"].dropna().unique())

annee = st.sidebar.selectbox("Année", annees, index=len(annees)-1)
region = st.sidebar.multiselect("Région", regions, default=regions)

df_filtre = df[(df["Année"] == annee) & (df["Région"].isin(region))]

# KPIs
col1, col2 = st.columns(2)
col1.metric("Pic horaire (MW)", f"{df_filtre.groupby('Heure')['Consommation brute totale (MW)'].mean().max():,.0f}")
col2.metric("Région max", df_filtre.groupby("Région")["Consommation brute totale (MW)"].sum().idxmax())

# Graphes

# Consommation totale par région 
st.subheader("Consommation énergétique totale par région")
conso_region = df_filtre.groupby("Région")["Consommation brute totale (MW)"].sum().sort_values()
fig1 = px.bar(conso_region, x=conso_region.values, y=conso_region.index, orientation='h',
              labels={"x":"MW", "y":"Région"}, color=conso_region.values, color_continuous_scale="Blues")
st.plotly_chart(fig1, use_container_width=True)

# horaire moyen 
st.subheader("Consommation moyenne par heure")
profil_horaire = df_filtre.groupby("Heure")["Consommation brute totale (MW)"].mean()
fig2 = px.line(x=profil_horaire.index, y=profil_horaire.values, markers=True,
               labels={"x":"Heure", "y":"MW"})
st.plotly_chart(fig2, use_container_width=True)

# Gaz vs Électricité par région
st.subheader("Comparaison Gaz vs Électricité par région")
gaz = df_filtre.groupby("Région")["Consommation brute gaz totale (MW PCS 0°C)"].sum()
elec = df_filtre.groupby("Région")["Consommation brute électricité (MW) - RTE"].sum()
comparaison = pd.DataFrame({"Gaz (MW)": gaz, "Électricité (MW)": elec}).reset_index()
fig4 = px.bar(comparaison, x="Région", y=["Gaz (MW)", "Électricité (MW)"],
              barmode="group")
st.plotly_chart(fig4, use_container_width=True)

# Consommation semaine vs week-end
st.subheader("Consommation : semaine vs week-end")
weekend_avg = df_filtre.groupby("is_weekend")["Consommation brute totale (MW)"].mean()
week_labels = ["Semaine", "Week-end"]
fig5 = px.bar(x=week_labels, y=weekend_avg.values, color=week_labels, color_discrete_sequence=["blue","orange"],
              labels={"x":"Type de jour", "y":"MW"})
st.plotly_chart(fig5, use_container_width=True)


# EMISSIONS GES

st.title("Émissions de gaz à effet de serre liées à l’électricité")

df_emissions = pd.read_csv("gaz_effet_de_serre_lier_a_la_consommation_d'electricite.csv", sep=";")
df_emissions.columns = df_emissions.columns.str.strip()
df_emissions["Date"] = pd.to_datetime(df_emissions["Date"], format="%Y-%m", errors="coerce")
df_emissions["Valeur (Mt)"] = df_emissions["Valeur (Mt)"].astype(str).str.replace(",", ".", regex=False).astype(float)
df_emissions["Année"] = df_emissions["Date"].dt.year
df_emissions["Mois"] = df_emissions["Date"].dt.month

# Filtres
st.sidebar.header("Filtres GES")
annees_ges = sorted(df_emissions["Année"].dropna().unique())
filieres = df_emissions["Filière"].dropna().unique()
annee_select = st.sidebar.multiselect("Années GES", annees_ges, default=annees_ges)
filiere_select = st.sidebar.multiselect("Filières GES", filieres, default=filieres)

df_filtre_ges = df_emissions[
    (df_emissions["Année"].isin(annee_select)) & (df_emissions["Filière"].isin(filiere_select))
]

# Graphes

# Évolution totale
st.subheader("Évolution des émissions totales de GES")
df_total = df_filtre_ges.groupby("Date")["Valeur (Mt)"].sum().reset_index()

fig_ges1 = px.line(
    df_total,
    x="Date",
    y="Valeur (Mt)",
    markers=True,
    labels={"Valeur (Mt)": "Émissions (Millions de tonnes)"}
)

# pics 
df_total["is_peak"] = (
    (df_total["Valeur (Mt)"] > df_total["Valeur (Mt)"].shift(1)) &
    (df_total["Valeur (Mt)"] > df_total["Valeur (Mt)"].shift(-1))
)

df_total["label"] = df_total.apply(
    lambda row: round(row["Valeur (Mt)"], 2) if row["is_peak"] else "",
    axis=1
)

# labels des pics
fig_ges1.update_traces(
    mode="lines+markers+text",
    text=df_total["label"],
    textposition="top center"
)

st.plotly_chart(fig_ges1, use_container_width=True)

# Émissions par filière
st.subheader("Répartition des émissions par filière")
df_filiere = df_filtre_ges.pivot_table(
    index="Date", columns="Filière", values="Valeur (Mt)", aggfunc="sum"
).reset_index()
fig_ges2 = px.area(
    df_filiere, 
    x="Date", 
    y=df_filiere.columns[1:], 
    labels={"value": "Émissions (Millions de tonnes)"}
)
st.plotly_chart(fig_ges2, use_container_width=True)


# Moyenne annuelle
st.subheader("Émissions moyennes annuelles")
df_year = df_filtre_ges.groupby("Année")["Valeur (Mt)"].mean().reset_index()
fig_ges3 = px.bar(
    df_year, 
    x="Année", 
    y="Valeur (Mt)", 
    text=df_year["Valeur (Mt)"].round(2),  
    labels={"Valeur (Mt)": "Émissions (Millions de tonnes)"}
)
fig_ges3.update_traces(textposition="outside")  
st.plotly_chart(fig_ges3, use_container_width=True)

# Heatmap 
st.subheader("Saisonnalité des émissions (année vs mois)")
df_heatmap = df_filtre_ges.groupby(["Année","Mois"])["Valeur (Mt)"].sum().unstack()

mois_fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
           "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

df_heatmap = df_heatmap.reindex(columns=range(1,13), fill_value=0)

fig_ges4 = go.Figure(data=go.Heatmap(
    z=df_heatmap.values,
    x=mois_fr,
    y=df_heatmap.index,
    colorscale='Reds'
))

fig_ges4.update_layout(
    title="Saisonnalité des émissions de GES",
    xaxis_title="Mois",
    yaxis_title="Année"
)

st.plotly_chart(fig_ges4, use_container_width=True)
