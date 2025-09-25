import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

# 1. Charger le fichier CSV
df = pd.read_csv(
    r"C:\Users\PC\Downloads\consommation-quotidienne-brute-regionale.csv",
    sep=";",
    low_memory=False
)

# 2. Garder uniquement les colonnes utiles
df_clean = df[[
    "Date - Heure",
    "Région",
    "Consommation brute gaz (MW PCS 0°C) - NaTran",
    "Consommation brute électricité (MW) - RTE",
    "Consommation brute totale (MW)"
]].dropna()

# 3. Transformer Date en features numériques
df_clean["Date - Heure"] = pd.to_datetime(df_clean["Date - Heure"])
df_clean["hour"] = df_clean["Date - Heure"].dt.hour
df_clean["dayofweek"] = df_clean["Date - Heure"].dt.dayofweek  # 0 = lundi
df_clean["month"] = df_clean["Date - Heure"].dt.month

# 4. Encoder la région
encoder = LabelEncoder()
df_clean["region_encoded"] = encoder.fit_transform(df_clean["Région"])

# 5. Définir X et y
X = df_clean[[
    "hour", "dayofweek", "month", "region_encoded",
    "Consommation brute gaz (MW PCS 0°C) - NaTran",
    "Consommation brute électricité (MW) - RTE"
]]
y = df_clean["Consommation brute totale (MW)"]

# 6. Split train/test (aléatoire, 80% / 20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=True, random_state=42
)

print("Taille train :", len(X_train))
print("Taille test  :", len(X_test))

# 7. Construire et entraîner le modèle XGBoost
model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.1,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# 8. Prédictions
y_pred = model.predict(X_test)

# 9. Évaluation
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mape = mean_absolute_percentage_error(y_test, y_pred) * 100
r2 = r2_score(y_test, y_pred) * 100

print("MAE :", mae)
print("RMSE :", rmse)
print("MAPE : {:.2f}%".format(mape))
print("Fiabilité (100 - MAPE) : {:.2f}%".format(100 - mape))
print("R² Score : {:.2f}%".format(r2))

# 10. Visualisation sur un échantillon de 1000 points
plt.figure(figsize=(15,6))
plt.plot(y_test.values[:1000], label="Valeurs réelles", color="blue")
plt.plot(y_pred[:1000], label="Valeurs prédites (XGBoost)", color="red",linewidth=0.5)
plt.legend()
plt.title("Consommation énergétique - reel vs Prédit (échantillon)")
plt.xlabel("Index")
plt.ylabel("MW")
plt.tight_layout()
plt.show()
