# Dashboard Consommation Énergétique & Émissions GES

Ce projet propose un **dashboard interactif** en Python, développé avec **Streamlit** et **Plotly**, permettant d’explorer :  

- La **consommation énergétique** (gaz et électricité) par région, période et type de jour.  
- Les **émissions de gaz à effet de serre (GES)** liées à la consommation d’électricité, avec différentes visualisations (évolution temporelle, répartition par filière, heatmap saisonnalité, etc.).  

---

## Lancement de l'application


### Installer les dépendances
```bash
pip install streamlit plotly pandas 
```
puis : 
```bash
streamlit run code.py
```
### Données utilisées

Le projet utilise deux fichiers CSV :
	1.	Consommation énergétique
	•	consommation-quotidienne-brute-regionale.csv
	•	Contient la consommation brute de gaz et d’électricité par région, au pas horaire.
	2.	Émissions de GES liées à l’électricité
	•	gaz_effet_de_serre_lier_a_la_consommation_d'electricite.csv
	•	Contient les émissions mensuelles par filière.

### NB : Placez ces fichiers dans le même dossier que code.py.

### Dépendances : 

Les principales bibliothèques Python nécessaires :
	•	streamlit → Interface interactive
	•	pandas → Manipulation des données
	•	plotly → Graphiques interactifs

### Fonctionnalités principales : 

1: Consommation énergétique
	•	Filtres par année et par région
	•	KPIs : pic horaire et région la plus consommatrice
	•	Graphiques : consommation régionale, profil horaire, gaz vs électricité, semaine vs week-end

2: Émissions de GES
	•	Filtres par année et filière
	•	Évolution temporelle avec détection des pics
	•	Répartition par filière (aire empilée)
	•	Moyennes annuelles
	•	Heatmap saisonnalité (année vs mois)


