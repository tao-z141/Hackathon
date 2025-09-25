import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from xgboost import XGBRegressor

df = pd.read_csv(
    r"C:\Users\PC\Downloads\consommation-quotidienne-brute-regionale.csv",
    sep=";",
    low_memory=False
)

# 2 Garder uniquement les colonnes utiles
df_clean = df[[
    "Date - Heure",
    "Région",
    "Consommation brute gaz (MW PCS 0°C) - NaTran",
    "Consommation brute électricité (MW) - RTE",
    "Consommation brute totale (MW)"
]].dropna()

# Transformer Date en features numériques
df_clean["Date - Heure"] = pd.to_datetime(df_clean["Date - Heure"])
df_clean["hour"] = df_clean["Date - Heure"].dt.hour
df_clean["dayofweek"] = df_clean["Date - Heure"].dt.dayofweek
df_clean["month"] = df_clean["Date - Heure"].dt.month
df_clean["year"] = df_clean["Date - Heure"].dt.year

#  Encoder la région
encoder = LabelEncoder()
df_clean["region_encoded"] = encoder.fit_transform(df_clean["Région"])

# Définir X et y
X = df_clean[[
    "hour", "dayofweek", "month", "year", "region_encoded",
    "Consommation brute gaz (MW PCS 0°C) - NaTran",
    "Consommation brute électricité (MW) - RTE"
]]
y = df_clean["Consommation brute totale (MW)"]

# Split train/test (avant 2025 = train, 2025 = test)
train_mask = df_clean["year"] < 2025
test_mask = df_clean["year"] == 2025

X_train, y_train = X[train_mask], y[train_mask]
X_test, y_test = X[test_mask], y[test_mask]
dates_test = df_clean.loc[test_mask, "Date - Heure"]

print("Taille train :", len(X_train))
print("Taille test  :", len(X_test))

# Construire et entraîner le modèle
model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.1,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)


mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mape = mean_absolute_percentage_error(y_test, y_pred) * 100
r2 = r2_score(y_test, y_pred) * 100

print("MAE :", mae)
print("RMSE :", rmse)
print("MAPE : {:.2f}%".format(mape))
print("Fiabilité (100 - MAPE) : {:.2f}%".format(100 - mape))
print("R² Score : {:.2f}%".format(r2))

df_test = pd.DataFrame({
    "Date": dates_test,
    "Réel": y_test.values,
    "Prédit": y_pred
})

# visutaliation Quotidienne pour Janvier 2025 
mask_jan = (df_test["Date"].dt.month == 1)
df_jan = df_test[mask_jan].groupby(df_test[mask_jan]["Date"].dt.date).mean()

plt.figure(figsize=(15,6))
plt.plot(df_jan.index, df_jan["Réel"], label="Valeurs réelles (Janvier)", color="blue", linewidth=2)
plt.plot(df_jan.index, df_jan["Prédit"], label="Valeurs prédites (Janvier)", color="red", linestyle="--", linewidth=2)
plt.legend()
plt.title("Consommation énergétique - Vrai vs Prédit (moyennes journalières - Janvier 2025)")
plt.xlabel("Date")
plt.ylabel("MW")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# visualisation Mensuel pour toute l'année 2025 
df_monthly = df_test.groupby(df_test["Date"].dt.to_period("M")).mean()
df_monthly.index = df_monthly.index.to_timestamp()

plt.figure(figsize=(12,6))
plt.plot(df_monthly.index, df_monthly["Réel"], label="Valeurs réelles", color="blue", marker="o", linewidth=2)
plt.plot(df_monthly.index, df_monthly["Prédit"], label="Valeurs prédites (XGBoost)", color="red", marker="s", linestyle="--", linewidth=2)
plt.legend()
plt.title("Consommation énergétique - Vrai vs Prédit (moyennes mensuelles - 2025)")
plt.xlabel("Mois")
plt.ylabel("MW")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
