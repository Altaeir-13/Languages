elq# ============================================================
#  Gerar dataset balanceado a partir de:
#   - train.csv (original)  -> deve ser mantido (opcional)
#   - dataset_completo_final.csv (pool) -> contém o train + outros
#  Requisito:
#   - NÃO reutilizar exemplos que já existem no train.csv original
#   - Balancear adicionando exemplos do "pool" para elevar classes raras
# ============================================================

import re
import numpy as np
import pandas as pd

# -----------------------------
# CONFIG (ajuste aqui)
# -----------------------------
TRAIN_PATH = "train.csv"
POOL_PATH  = "dataset_completo_final.csv"

OUT_FULL_PATH  = "train_balanceado_aug.csv"      # train original + extras balanceados
OUT_EXTRAS_PATH = "extras_balanceados.csv"       # só os extras (sem o train)

LABEL_COLS = ["anger", "disgust", "fear", "joy", "sadness", "surprise"]

INCLUDE_ORIGINAL_TRAIN = True   # True = mantém train e adiciona extras; False = gera dataset só com extras

SEED = 42
np.random.seed(SEED)

# Meta de balanceamento (positivos por classe).
# Sugestão: 250–350 costuma melhorar F1-Macro sem inflar demais o dataset.
TARGET_POS_PER_CLASS = 350

# Limite de segurança: evita explodir o dataset caso você coloque target muito alto
MAX_ADDED_TOTAL = 200_000


# -----------------------------
# Funções auxiliares
# -----------------------------
def normalize_text_series(s: pd.Series) -> pd.Series:
    """
    Normalização leve para deduplicação:
      - lower
      - colapsar espaços
      - strip
    (não remove pontuação, para evitar colapsar frases diferentes por engano)
    """
    s = s.astype(str).str.lower()
    s = s.str.replace(r"\s+", " ", regex=True).str.strip()
    return s


def print_distribution(name: str, df: pd.DataFrame, label_cols=LABEL_COLS):
    y = df[label_cols].astype(int)
    counts = y.sum().sort_values(ascending=False)
    neutral = int((y.sum(axis=1) == 0).sum())
    multi = int((y.sum(axis=1) >= 2).sum())
    total = len(df)

    print(f"\n=== {name} ===")
    print("Total:", total)
    print("1s por classe:\n", counts)
    print("Neutros (all-zero):", neutral, f"({neutral/total*100:.2f}%)")
    print("Multi-label (>=2):", multi, f"({multi/total*100:.2f}%)")


def build_balanced_extras(
    base_df: pd.DataFrame,
    pool_df: pd.DataFrame,
    target_pos: int,
    label_cols=LABEL_COLS,
    max_added_total=MAX_ADDED_TOTAL,
    seed=SEED
) -> pd.DataFrame:
    """
    Seleciona exemplos do pool (já filtrado e deduplicado) para elevar classes abaixo do target_pos.
    Estratégia:
      - para cada classe com déficit, amostra exemplos onde aquela classe = 1
      - prioriza exemplos que também ajudam outras classes com déficit (pesos)
      - nunca reutiliza exemplos já selecionados
    """
    rng = np.random.default_rng(seed)

    current = base_df[label_cols].astype(int).sum().to_dict()
    targets = {c: max(current[c], int(target_pos)) for c in label_cols}  # não reduz maioria, só eleva minorias

    # Vamos trabalhar com um pool indexado (mais fácil remover selecionados)
    pool = pool_df.copy()

    selected_parts = []
    total_added = 0

    def deficits_dict():
        return {c: max(targets[c] - current[c], 0) for c in label_cols}

    while True:
        deficits = deficits_dict()
        # para quando não há mais déficit
        if all(v <= 0 for v in deficits.values()):
            break
        if total_added >= max_added_total:
            print("\n[AVISO] Atingiu MAX_ADDED_TOTAL. Parando para evitar dataset gigante.")
            break

        # ordena classes por maior déficit
        classes_by_need = sorted(deficits.keys(), key=lambda c: deficits[c], reverse=True)

        progress = False

        for cls in classes_by_need:
            need = deficits[cls]
            if need <= 0:
                continue

            subset = pool[pool[cls].astype(int) == 1]
            if subset.empty:
                continue

            take = int(min(need, len(subset), max_added_total - total_added))
            if take <= 0:
                continue

            # pesos: prioriza linhas que cobrem outras classes deficitárias
            dvec = np.array([deficits[c] for c in label_cols], dtype=float)
            # score = soma(deficit_classe * label_da_linha)
            mat = subset[label_cols].astype(int).to_numpy()
            weights = mat @ dvec

            # se tudo zerar (raro), amostra uniforme
            if np.all(weights == 0):
                chosen_idx = rng.choice(subset.index.to_numpy(), size=take, replace=False)
            else:
                # amostragem ponderada sem reposição:
                # converte em prob. e escolhe via "choice" sem reposição
                probs = weights / weights.sum()
                chosen_idx = rng.choice(subset.index.to_numpy(), size=take, replace=False, p=probs)

            chosen = pool.loc[chosen_idx]
            selected_parts.append(chosen)

            # atualiza contadores
            add_counts = chosen[label_cols].astype(int).sum().to_dict()
            for c in label_cols:
                current[c] += int(add_counts[c])

            # remove do pool para não selecionar de novo
            pool = pool.drop(index=chosen_idx)

            total_added += len(chosen)
            progress = True

            print(f"[+{len(chosen):4d}] adicionados para '{cls}' | deficit restante (aprox): {max(targets[cls]-current[cls],0)}")

            # recomputa deficits após adicionar (evita overshoot exagerado)
            deficits = deficits_dict()
            if all(v <= 0 for v in deficits.values()):
                break

        if not progress:
            # não conseguiu avançar (pool insuficiente para classes deficitárias)
            print("\n[AVISO] Não foi possível completar o balanceamento: pool sem exemplos suficientes para algumas classes.")
            break

    extras_df = pd.concat(selected_parts, ignore_index=True) if selected_parts else pool_df.iloc[0:0].copy()
    return extras_df


# -----------------------------
# MAIN
# -----------------------------
def main():
    # 1) Carregar
    train_df = pd.read_csv(TRAIN_PATH)
    pool_df  = pd.read_csv(POOL_PATH)

    # 2) Validar colunas
    required = ["id", "text"] + LABEL_COLS
    for c in required:
        if c not in train_df.columns:
            raise ValueError(f"train.csv não tem a coluna '{c}'")
        if c not in pool_df.columns:
            raise ValueError(f"dataset_completo_final.csv não tem a coluna '{c}'")

    # 3) Normalizar texto (para deduplicação robusta)
    train_df = train_df.copy()
    pool_df  = pool_df.copy()

    train_df["text_norm"] = normalize_text_series(train_df["text"])
    pool_df["text_norm"]  = normalize_text_series(pool_df["text"])

    # 4) Remover do pool tudo que já existe no train original (por id OU por texto)
    train_ids = set(train_df["id"].astype(str))
    train_texts = set(train_df["text_norm"])

    before = len(pool_df)
    pool_df = pool_df[~pool_df["id"].astype(str).isin(train_ids)]
    pool_df = pool_df[~pool_df["text_norm"].isin(train_texts)]
    after = len(pool_df)

    print(f"\nPool: removidos {before-after} exemplos que já estavam no train (por id/texto).")
    print(f"Pool restante: {after}")

    # 5) Remover duplicatas internas do pool (por texto normalizado)
    before = len(pool_df)
    pool_df = pool_df.drop_duplicates(subset=["text_norm"], keep="first")
    print(f"Pool: removidas {before-len(pool_df)} duplicatas internas (por texto).")

    # 6) Escolher base (train ou vazio)
    if INCLUDE_ORIGINAL_TRAIN:
        base_df = train_df.copy()
    else:
        base_df = train_df.iloc[0:0].copy()  # vazio, com mesmas colunas

    # 7) Relatório inicial
    print_distribution("BASE (antes)", base_df, LABEL_COLS)
    print_distribution("POOL (candidatos)", pool_df, LABEL_COLS)

    # 8) Selecionar extras balanceados
    extras_df = build_balanced_extras(
        base_df=base_df,
        pool_df=pool_df,
        target_pos=TARGET_POS_PER_CLASS,
        label_cols=LABEL_COLS,
        max_added_total=MAX_ADDED_TOTAL,
        seed=SEED
    )

    print_distribution("EXTRAS selecionados", extras_df, LABEL_COLS)

    # 9) Montar dataset final
    if INCLUDE_ORIGINAL_TRAIN:
        final_df = pd.concat([base_df, extras_df], ignore_index=True)
    else:
        final_df = extras_df.copy()

    # 10) Segurança: remover duplicatas finais por texto_norm e por id
    before = len(final_df)
    final_df = final_df.drop_duplicates(subset=["text_norm"], keep="first")
    final_df = final_df.drop_duplicates(subset=["id"], keep="first")
    print(f"\nFinal: removidas {before-len(final_df)} duplicatas após concatenação (texto/id).")

    # 11) Salvar (remove coluna auxiliar)
    extras_out = extras_df.drop(columns=["text_norm"], errors="ignore")
    final_out  = final_df.drop(columns=["text_norm"], errors="ignore")

    extras_out.to_csv(OUT_EXTRAS_PATH, index=False)
    final_out.to_csv(OUT_FULL_PATH, index=False)

    print_distribution("FINAL (depois)", final_df, LABEL_COLS)
    print(f"\n✅ Salvo: {OUT_EXTRAS_PATH} (somente extras)")
    print(f"✅ Salvo: {OUT_FULL_PATH} (train + extras balanceados)")


if __name__ == "__main__":
    main()
