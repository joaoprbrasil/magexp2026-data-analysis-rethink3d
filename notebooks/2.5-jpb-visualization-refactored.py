# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# %%
# ==========================================
# 1. CONFIGURAÇÕES E CONSTANTES
# ==========================================
try:
    ROOT = Path(__file__).resolve().parents[1]
except NameError:
    ROOT = Path.cwd()

DF_PATH = ROOT / "data" / "processed" / "dataset.csv"
FIG_PATH = ROOT / "reports" / "figures"
IDS_SPAM_PATH = ROOT / "data" / "interim" / "ids_spam.csv"

FIG_PATH.mkdir(parents=True, exist_ok=True) # Garante que a pasta existe

CINZA_ESCURO = "#414040"
plt.rcParams.update({
    "text.color": CINZA_ESCURO,
    "axes.labelcolor": CINZA_ESCURO,
    "xtick.color": CINZA_ESCURO,
    "ytick.color": CINZA_ESCURO,
    "axes.edgecolor": CINZA_ESCURO
})

# %%
# ==========================================
# 2. CARREGAMENTO E PRÉ-PROCESSAMENTO
# ==========================================
df = pd.read_csv(DF_PATH)
df["createdAt"] = pd.to_datetime(df["createdAt"])

# Carregando os IDs de spam do arquivo CSV
df_ids_spam = pd.read_csv(IDS_SPAM_PATH)
# Convertendo a coluna 'id' do CSV em uma lista Python
IDS_SPAM = df_ids_spam["id"].tolist()

# Separando os dados uma única vez
df_spam = df[df["id"].isin(IDS_SPAM)].copy()
df_normais = df[~df["id"].isin(IDS_SPAM)].copy()

# ==========================================
# 3. FUNÇÕES REUTILIZÁVEIS DE PLOTAGEM
# ==========================================

# %%
def plot_histogram_contas(dt_start, dt_end, title, s_normais, s_spam=None, y_max=80):
    """Gera um histograma (simples ou empilhado se s_spam for fornecido)."""
    fig, ax = plt.subplots(figsize=(12, 5))
    bins_horas = pd.date_range(dt_start, dt_end, freq="h")

    dados = [s_normais] if s_spam is None else [s_normais, s_spam]
    cores = ["darkgrey"] if s_spam is None else ["darkgrey", "C0"]
    labels = ["Contas normais"] if s_spam is None else ["Contas normais", "Contas suspeitas (Spam)"]

    ax.hist(
        dados, bins=bins_horas, stacked=True, color=cores,
        edgecolor="white", alpha=0.8, label=labels
    )

    # Rótulos nas barras
    counts_normais, _ = np.histogram(s_normais, bins=bins_horas)
    counts_spam = np.zeros_like(counts_normais) if s_spam is None else np.histogram(s_spam, bins=bins_horas)[0]
    bin_centers = bins_horas[:-1] + pd.Timedelta(minutes=30)

    for center, norm_c, spam_c in zip(bin_centers, counts_normais, counts_spam):

        # Rótulo Normal
        if norm_c > 0:
            if s_spam is None:
                # Se for gráfico simples (sem spam), colocar texto acima da barra
                y_pos_norm = norm_c + 1.5
                cor_texto = 'dimgray'
                tamanho_fonte = 12
            else:
                # Se for gráfico empilhado, tentar centralizar na barra cinza
                y_pos_norm = (norm_c / 2) if norm_c > 9 else (norm_c / 2) + 4
                cor_texto = 'gray'
                tamanho_fonte = 10

            ax.text(center, y_pos_norm, str(int(norm_c)), ha="center", va="center",
                    color=cor_texto, fontsize=tamanho_fonte)

        # Rótulo Spam
        if s_spam is not None and spam_c > 1:
            ax.text(center, norm_c + (spam_c / 2), str(int(spam_c)), ha="center", va="center",
                    color="w", fontweight='bold', fontsize=11)

    # Formatação
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate(rotation=0)

    if s_spam is not None:
        ax.legend()

    ax.set_xlabel("Hora")
    ax.set_title(title, fontsize="14", color="black")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_yticks([])
    ax.set_ylim(0, y_max)

    return fig, ax

# %%
def plot_linha_contas(dt_start, dt_end, title, df_base, df_scatter_normais, df_scatter_spam=None, y_max=10):
    """Gera um gráfico de linha com pontos exatos sobrepostos (scatter)."""
    fig, ax = plt.subplots(figsize=(12, 5))

    # 1. Cria a linha de tendência (15 em 15 min)
    eixo_completo = pd.date_range(dt_start, dt_end, freq="15min")
    por_hora = df_base.set_index("createdAt").resample("15min", label="right").size()
    por_hora = por_hora.reindex(eixo_completo, fill_value=0)
    ax.plot(por_hora.index.to_pydatetime(), por_hora.values, color="lightgrey")

    # Função interna para extrair pontos e Y exato na linha
    def get_scatter_points(df_scatter):
        horarios = [h for h in df_scatter["createdAt"].unique() if por_hora.index.min() <= h <= por_hora.index.max()]
        idx_combinado = por_hora.index.union(horarios)
        interpolado = por_hora.reindex(idx_combinado).interpolate(method="time")
        valores_y = interpolado.loc[horarios].values
        return pd.to_datetime(horarios).to_pydatetime(), valores_y

    # 2. Plotar pontos Normais
    hx_norm, hy_norm = get_scatter_points(df_scatter_normais)
    ax.scatter(hx_norm, hy_norm, color="darkgrey" if df_scatter_spam is not None else "gray",
               s=40, edgecolor=CINZA_ESCURO if df_scatter_spam is not None else "black",
               linewidth=0.3, alpha=0.6 if df_scatter_spam is not None else 0.7, zorder=4,
               label="Contas normais" if df_scatter_spam is not None else None)

    # 3. Plotar pontos Spam (se houver)
    if df_scatter_spam is not None:
        hx_spam, hy_spam = get_scatter_points(df_scatter_spam)
        ax.scatter(hx_spam, hy_spam, color="C0", s=50, edgecolor="black", linewidth=0.3,
                   alpha=0.8, zorder=5, label="Contas suspeitas (Spam)")
        ax.legend()

    # 4. Formatação
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate(rotation=0)

    ax.set_xlabel("Hora")
    ax.set_ylabel("Nº de criação de conta")
    ax.set_title(title, fontsize="14", color="black")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(visible=True, color="gray", linestyle="--", linewidth=0.2, alpha=0.5)

    if df_scatter_spam is None:
        ax.set_ylim(-0.5, y_max)

    return fig, ax


# ==========================================
# 4. GERAÇÃO DOS GRÁFICOS
# ==========================================

# %%
# --- Gráfico 00: Histograma Dia 11 (Com Spam) ---
fig, ax = plot_histogram_contas(
    "2026-07-11 12:00:00", "2026-07-11 21:00:00",
    "Dia 11 - Sábado\nSpam de criação de contas para ganhar tickets",
    df_normais["createdAt"], df_spam["createdAt"], y_max=80
)
ax.text(0.8, 0.5, "Das 143 contas\nregistradas no sábado,", fontsize=13, color="gray", transform=ax.transAxes)
ax.text(0.8, 0.43, "75 delas são spam.", fontsize=13, color="C0", fontweight="medium", transform=ax.transAxes)
fig.savefig(FIG_PATH / "00-spam_account_hist_day11.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()

# %%
# --- Gráfico 01: Linha Dia 11 (Com Spam) ---
fig, ax = plot_linha_contas(
    "2026-07-11 12:00:00", "2026-07-11 21:00:00",
    "Dia 11 - Sábado\nFrequência de spam",
    df, df_normais, df_spam
)
fig.savefig(FIG_PATH / "01-spam_account_line_day11.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()

# %%
# --- Gráfico 02: Linha Dia 11 (Sem Spam) ---
fig, ax = plot_linha_contas(
    "2026-07-11 12:00:00", "2026-07-11 21:00:00",
    "Dia 11 - Sábado\nVolume de criação de contas (Sem Spam)",
    df_normais, df_normais
)
fig.savefig(FIG_PATH / "02-no_spam_account_line_day11.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()

# %%
# --- Gráfico 03: Linha Dia 12 (Volume normal total) ---
fig, ax = plot_linha_contas(
    "2026-07-12 12:00:00", "2026-07-12 21:00:00",
    "Dia 12 - Domingo\nVolume de criação de contas",
    df, df
)
fig.savefig(FIG_PATH / "03-no_spam_account_line_day12.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()

# %%
# --- Gráfico 04: Histograma Dia 11 (Sem Spam) ---
fig, ax = plot_histogram_contas(
    "2026-07-11 12:00:00", "2026-07-11 21:00:00",
    "Dia 11 - Sábado\nCriação de contas filtrada",
    df_normais["createdAt"], y_max=30
)
ax.text(0.8, 0.5, "Total:", fontsize=13, color="gray", transform=ax.transAxes)
ax.text(0.8, 0.43, "68 contas.", fontsize=13, color="dimgray", fontweight="medium", transform=ax.transAxes)
fig.savefig(FIG_PATH / "04-no_spam_account_hist_day11.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()

# %%
# --- Gráfico 05: Histograma Dia 12 ---
fig, ax = plot_histogram_contas(
    "2026-07-12 12:00:00", "2026-07-12 21:00:00",
    "Dia 12 - Domingo",
    df_normais["createdAt"], y_max=30
)
ax.text(0.8, 0.5, "Total:", fontsize=13, color="gray", transform=ax.transAxes)
ax.text(0.8, 0.43, "41 contas.", fontsize=13, color="dimgrey", fontweight="medium", transform=ax.transAxes)
fig.savefig(FIG_PATH / "05-no_spam_account_hist_day12.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.show()

# %%
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 3))
ax1.text(0.1, 0.47, 'Dia 11 - Sábado', fontsize=10, color="gray", transform=ax.transAxes)
ax1.text(0.02, 0.23, '143', fontsize=70, color="gray", transform=ax.transAxes)
ax1.axis('off')

ax2.text(0.8, 0.47, 'Dia 12 - Domingo', fontsize=10, color="gray", transform=ax.transAxes)
ax2.text(0.79, 0.235, '41', fontsize=70, color="gray", transform=ax.transAxes)
ax2.axis('off')

fig.suptitle('Contas registradas na plataforma gamificada.', fontsize=14)
plt.tight_layout()
fig.savefig(FIG_PATH / "06-account-creation-number.png", dpi=300, bbox_inches="tight", facecolor="white")

plt.show()

# %%
fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(7, 2), layout="constrained")

# Ax 1 - Dia 11
ax1.text(0.53, 0.85, 'Dia 11 - Sábado', fontsize=10, color="gray", transform=ax1.transAxes)
ax1.text(0.4, 0.33, '143', fontsize=70, color="gray", transform=ax1.transAxes)
ax1.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
ax1.set_xticks([])
ax1.set_yticks([])
#ax1.axis('off')

# Ax 2 - Dia 12
ax2.text(0.233, 0.85, 'Dia 12 - Domingo', fontsize=10, color="gray", transform=ax2.transAxes)
ax2.text(0.23, 0.33, '41', fontsize=70, color="gray", transform=ax2.transAxes)
ax2.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
ax2.set_xticks([])
ax2.set_yticks([])

fig.suptitle('Contas registradas na plataforma gamificada.', fontsize=14)

fig.savefig(FIG_PATH / "06-account-creation-number.png", dpi=300, bbox_inches="tight")
plt.show()