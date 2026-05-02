import os
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

diretorio_script = os.path.dirname(os.path.abspath(__file__))

path_gt  = os.path.join(diretorio_script, "truth.csv")
path_sub = os.path.join(diretorio_script, "submissao_corrigida.csv")  # <-- confira o nome!d

label_cols = ['anger', 'disgust', 'fear', 'joy', 'sadness', 'surprise']

df_gt = pd.read_csv(path_gt)
df_sub = pd.read_csv(path_sub)

# --- checagens básicas ---
print("GT rows:", len(df_gt), " | SUB rows:", len(df_sub))
print("IDs únicos GT:", df_gt["id"].nunique(), " | SUB:", df_sub["id"].nunique())

# garante que colunas existem
for c in ["id"] + label_cols:
    if c not in df_gt.columns:
        raise ValueError(f"Faltando coluna '{c}' no truth.csv")
    if c not in df_sub.columns:
        raise ValueError(f"Faltando coluna '{c}' na submissão")

# detecta duplicatas de id (isso é MUITO comum e estraga o merge)
dups_gt = df_gt["id"].duplicated().sum()
dups_sub = df_sub["id"].duplicated().sum()
print("IDs duplicados - GT:", dups_gt, " | SUB:", dups_sub)

# --- merge com diagnóstico de cobertura de IDs ---
merged = df_gt.merge(df_sub, on="id", how="outer", indicator=True, suffixes=("_true", "_pred"))

print("\nCobertura do merge (_merge):")
print(merged["_merge"].value_counts())

# se tiver linhas em left_only ou right_only, você NÃO está comparando o mesmo conjunto
left_only = (merged["_merge"] == "left_only").sum()
right_only = (merged["_merge"] == "right_only").sum()
if left_only or right_only:
    print("\n⚠️ Atenção: há IDs sem correspondência.")
    print("IDs só no GT:", left_only, " | IDs só na SUB:", right_only)

# fica só com os pares que existem nos dois
merged = merged[merged["_merge"] == "both"].copy()

# --- extrai y_true e y_pred, força 0/1 int e trata NaN ---
y_true = merged[[c + "_true" for c in label_cols]].apply(pd.to_numeric, errors="coerce").fillna(0).astype(int).to_numpy()
y_pred = merged[[c + "_pred" for c in label_cols]].apply(pd.to_numeric, errors="coerce").fillna(0).astype(int).to_numpy()

# garante binário (se tiver coisa fora de {0,1}, avisa)
def check_binary(arr, name):
    vals = np.unique(arr)
    bad = [v for v in vals if v not in (0, 1)]
    if bad:
        print(f"⚠️ {name} tem valores fora de 0/1:", bad[:20])

check_binary(y_true, "y_true")
check_binary(y_pred, "y_pred")

# --- métricas ---
f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
f1_micro = f1_score(y_true, y_pred, average="micro", zero_division=0)
f1_each  = f1_score(y_true, y_pred, average=None, zero_division=0)

print("\nF1-Macro:", f"{f1_macro:.4f}")
print("F1-Micro:", f"{f1_micro:.4f}")

print("\nF1 por classe:")
for c, s in zip(label_cols, f1_each):
    print(f"{c:8s}: {s:.4f}")

# --- sanity checks úteis ---
print("\nQtd de 1s por classe (GT):", dict(zip(label_cols, y_true.sum(axis=0))))
print("Qtd de 1s por classe (PRED):", dict(zip(label_cols, y_pred.sum(axis=0))))
print("All-zero (GT):", int((y_true.sum(axis=1) == 0).sum()))
print("All-zero (PRED):", int((y_pred.sum(axis=1) == 0).sum()))