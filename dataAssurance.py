import pandas as pd
import numpy as np

# ---------------------------------------------------------
# 1. Charger le fichier (Excel ou CSV)
# ---------------------------------------------------------

def load_file(path):
    if path.endswith(".csv"):
        return pd.read_csv(path)
    elif path.endswith(".xlsx"):
        return pd.read_excel(path)
    else:
        raise ValueError("Format non supporté : utilisez CSV ou XLSX")

df = load_file("dataAssurance.csv")


# ---------------------------------------------------------
# 2. Nettoyage général du dataset
# ---------------------------------------------------------

# Standardiser les noms de colonnes
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

# Supprimer les doublons éventuels
df = df.drop_duplicates()

# Convertir automatiquement les types
df = df.convert_dtypes()

# Nettoyage généralisé des valeurs numériques
def clean_numeric(series):
    """Nettoie une série numérique potentiellement sale (texte, virgules, espaces)."""
    return (
        series.astype(str)
              .str.replace(",", ".", regex=False)
              .str.replace(r"[^0-9.\-]", "", regex=True)
              .replace("", np.nan)
              .astype(float)
    )

# Nettoyer certaines colonnes si besoin
num_cols = ["age", "bmi", "charges"]

for col in num_cols:
    if col in df.columns:
        df[col] = clean_numeric(df[col])


# ---------------------------------------------------------
# 3. Catégorisation des colonnes
# ---------------------------------------------------------

# --- 3.1 Catégorisation de l'âge (bornes fixes)
def categorize_age(age):
    if pd.isna(age):
        return np.nan
    if 18 <= age <= 35:
        return "bas"
    elif 36 <= age <= 55:
        return "moyen"
    elif age >= 56:
        return "haut"
    return np.nan

df["age_cat"] = df["age"].apply(categorize_age)


# --- 3.2 Catégorisation BMI (automatique par quantiles)
if "bmi" in df.columns:
    quant_bmi = df["bmi"].quantile([0.33, 0.66])
    q1_bmi, q2_bmi = quant_bmi[0.33], quant_bmi[0.66]

    def categorize_bmi(bmi):
        if pd.isna(bmi):
            return np.nan
        if bmi <= q1_bmi:
            return "bas"
        elif bmi <= q2_bmi:
            return "moyen"
        else:
            return "haut"

    df["bmi_cat"] = df["bmi"].apply(categorize_bmi)


# --- 3.3 Catégorisation des charges (automatique par quantiles)
if "charges" in df.columns:
    quant_charges = df["charges"].quantile([0.33, 0.66])
    q1_charges, q2_charges = quant_charges[0.33], quant_charges[0.66]

    def categorize_charges(x):
        if pd.isna(x):
            return np.nan
        if x <= q1_charges:
            return "bas"
        elif x <= q2_charges:
            return "moyen"
        else:
            return "haut"

    df["charges_cat"] = df["charges"].apply(categorize_charges)


# ---------------------------------------------------------
# 4. Sauvegarde du fichier propre
# ---------------------------------------------------------

df.to_excel("dataAssurance_clean.xlsx", index=False)
df.to_csv("dataAssurance_clean.csv", index=False)

print("Nettoyage terminé ✔ Fichiers enregistrés : dataAssurance_clean.xlsx & .csv")
