# %%
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

try:
    ROOT = Path(__file__).resolve().parents[1]
except NameError:
    ROOT = Path.cwd()

DF_PATH = ROOT / "data" / "processed" / "dataset.csv"
FIG_PATH = ROOT / "reports" / "figures"
IDS_SPAM_PATH = ROOT / "data" / "interim" / "ids_spam.csv"
df = pd.read_csv(DF_PATH)

# %%
# Garante a conversão para datetime
df["createdAt"] = pd.to_datetime(df["createdAt"])


# %%

df = pd.read_csv(DF_PATH)
df["createdAt"] = pd.to_datetime(df["createdAt"])

# Carregando os IDs de spam do arquivo CSV
df_ids_spam = pd.read_csv(IDS_SPAM_PATH)
# Convertendo a coluna 'id' do CSV em uma lista Python
ids_para_remover = df_ids_spam["id"].tolist()


# %%
CINZA_ESCURO = "#414040"
plt.rcParams["text.color"] = CINZA_ESCURO
plt.rcParams["axes.labelcolor"] = CINZA_ESCURO
plt.rcParams["xtick.color"] = CINZA_ESCURO
plt.rcParams["ytick.color"] = CINZA_ESCURO
plt.rcParams["axes.edgecolor"] = CINZA_ESCURO
# %%
# Garantir que a coluna está no formato datetime
df["createdAt"] = pd.to_datetime(df["createdAt"])

# --- 2. FILTRAR OS DATETIMES BRUTOS (Suspeitos vs Normais) ---
horas_suspeitas = df[df["id"].isin(ids_para_remover)]["createdAt"]
horas_normais = df[~df["id"].isin(ids_para_remover)]["createdAt"]

# --- 3. DEFINIR OS INTERVALOS (BINS) DO HISTOGRAMA ---
bins_horas = pd.date_range(
    "2026-07-11 12:00:00",
    "2026-07-11 21:00:00",
    freq="h",
)

# --- 4. CONSTRUIR O GRÁFICO ---
fig, ax = plt.subplots(figsize=(12, 5))

# Plotando o histograma empilhado
ax.hist(
    [horas_normais, horas_suspeitas],
    bins=bins_horas,
    stacked=True,
    color=["darkgrey", "C0"],
    edgecolor="white",
    alpha=0.8,
    label=["Contas normais", "Contas suspeitas (Spam)"],
)

# --- 5. CALCULAR E ADICIONAR OS RÓTULOS DE TEXTO EM CADA COLUNA ---
# Calculamos a quantidade exata por bin para posicionar os textos
counts_normais, _ = np.histogram(horas_normais.values, bins=bins_horas.values)
counts_suspeitas, _ = np.histogram(
    horas_suspeitas.values, bins=bins_horas.values
)

# Encontra o centro de cada barra no eixo X para centralizar o texto
bin_centers = bins_horas[:-1] + pd.Timedelta(minutes=30)

for center, norm_c, spam_c in zip(bin_centers, counts_normais, counts_suspeitas):
    # Texto para Contas Normais (Cinza Escuro, no centro do bloco cinza)
    if norm_c > 9:
        y_pos_norm = norm_c / 2
        txt_norm = ax.text(
            center,
            y_pos_norm,
            str(int(norm_c)),
            ha="center",
            va="center",
            color='gray',
            fontsize=10,
        )
    elif norm_c > 0:
        y_pos_norm = (norm_c / 2) + 4
        txt_norm = ax.text(
            center,
            y_pos_norm,
            str(int(norm_c)),
            ha="center",
            va="center",
            color='gray',
            fontsize=10,
        )
        # Borda branca invisível/suave para garantir leitura


    # Texto para Contas Spam (Vermelho, no centro do bloco vermelho)
    if spam_c > 1:
        y_pos_spam = norm_c + (spam_c / 2)
        txt_spam = ax.text(
            center,
            y_pos_spam,
            str(int(spam_c)),
            ha="center",
            va="center",
            color="w",
            fontweight='bold',
            fontsize=11,
        )


# --- 6. FORMATAÇÃO DOS EIXOS E TEXTOS ---
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate(rotation=0)

ax.legend()
ax.set_xlabel("Hora")

ax.set_title(
    "Dia 11 - Sábado\nSpam de criação de contas para ganhar tickets", fontsize="14", color="black"
)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_yticks([])
ax.set_ylim(0, 80)

ax.text(
    0.8, 0.5,
    "Das 143 contas\nregistradas no sábado,",
    fontsize=13,
    color="gray",
    transform=ax.transAxes
)
ax.text(
    0.8, 0.43,
    "75 delas são spam.",
    fontsize=13,
    color="C0",
    fontweight="medium",
    transform=ax.transAxes
)


plt.show()

fig.savefig(
    FIG_PATH/ "00-spam_account_hist_day11.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)

# %%
por_hora = df.set_index("createdAt").resample("15min", label="right").size()

eixo_completo = pd.date_range(
    "2026-07-11 12:00:00",
    "2026-07-11 21:00:00",
    freq="15min",
)

por_hora = por_hora.reindex(eixo_completo, fill_value=0)

# --- 2. GRÁFICO BASE ---
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(por_hora.index.to_pydatetime(), por_hora.values, color="lightgrey")


# --- 3. FILTRAR OS IDs (Suspeitos vs Normais) ---
# df_remocao pega quem ESTÁ na lista
df_remocao = df[df["id"].isin(ids_para_remover)].copy()
# df_normais pega quem NÃO ESTÁ na lista (usando o ~)
df_normais = df[~df["id"].isin(ids_para_remover)].copy()


# --- 4. HORÁRIOS EXATOS DENTRO DO LIMITE DO GRÁFICO ---
horarios_suspeitos_unicos = df_remocao["createdAt"].unique()
horarios_normais_unicos = df_normais["createdAt"].unique()

horarios_suspeitos_validos = [
    h
    for h in horarios_suspeitos_unicos
    if por_hora.index.min() <= h <= por_hora.index.max()
]
horarios_normais_validos = [
    h
    for h in horarios_normais_unicos
    if por_hora.index.min() <= h <= por_hora.index.max()
]


# --- 5. INTERPOLAÇÃO UNIFICADA PARA AMBOS OS GRUPOS ---
# Combinamos o índice original com os horários de spam E os horários normais
indice_combinado = (
    por_hora.index.union(horarios_suspeitos_validos).union(
        horarios_normais_validos
    )
)
por_hora_interpolado = por_hora.reindex(indice_combinado).interpolate(
    method="time"
)

valores_na_linha_suspeitos = por_hora_interpolado.loc[
    horarios_suspeitos_validos
].values
valores_na_linha_normais = por_hora_interpolado.loc[
    horarios_normais_validos
].values


# --- 6. PLOTAR OS PONTOS EXATOS SOBRE A LINHA ---

# Pontos Cinzas: Contas Normais (zorder=4 para ficar logo abaixo do vermelho se coincidirem)
ax.scatter(
    pd.to_datetime(horarios_normais_validos).to_pydatetime(),
    valores_na_linha_normais,
    color="darkgrey",
    s=40,
    edgecolor=CINZA_ESCURO,
    linewidth=0.3,
    alpha=0.6,
    zorder=4,
    label="Contas normais",
)

ax.scatter(
    pd.to_datetime(horarios_suspeitos_validos).to_pydatetime(),
    valores_na_linha_suspeitos,
    color="C0",
    s=50,
    edgecolor="black",
    linewidth=0.3,
    alpha=0.8,
    zorder=5,
    label="Contas suspeitas (Spam)",
)


# --- 7. FORMATAÇÃO DO EIXO X E DO GRÁFICO ---
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate(rotation=0)

ax.legend()
ax.set_xlabel("Hora")
ax.set_ylabel("Nº de criação de conta")
ax.set_title(
    "Dia 11 - Sábado\nFrequência de spam", fontsize="14", color="black"
)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(visible=True, color="gray", linestyle="--", linewidth=0.2, alpha=0.5)
plt.show()

fig.savefig(
    FIG_PATH/ "01-spam_account_line_day11.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)

# %%
# --- 1. FILTRAR OS DADOS PRIMEIRO ---
# Descartamos o spam logo no início para que a linha represente apenas o tráfego orgânico
df_normais = df[~df["id"].isin(ids_para_remover)].copy()


# --- 2. CALCULAR O VOLUME APENAS DO TRÁFEGO NORMAL ---
por_hora = df_normais.set_index("createdAt").resample("15min", label="right").size()

eixo_completo = pd.date_range(
    "2026-07-11 12:00:00",
    "2026-07-11 21:00:00",
    freq="15min",
)

por_hora = por_hora.reindex(eixo_completo, fill_value=0)


# --- 3. GRÁFICO BASE (LINHA) ---
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(por_hora.index.to_pydatetime(), por_hora.values, color="lightgrey")


# --- 4. HORÁRIOS EXATOS DENTRO DO LIMITE DO GRÁFICO ---
horarios_normais_unicos = df_normais["createdAt"].unique()

horarios_normais_validos = [
    h
    for h in horarios_normais_unicos
    if por_hora.index.min() <= h <= por_hora.index.max()
]


# --- 5. INTERPOLAÇÃO ---
indice_combinado = por_hora.index.union(horarios_normais_validos)
por_hora_interpolado = por_hora.reindex(indice_combinado).interpolate(method="time")

valores_na_linha_normais = por_hora_interpolado.loc[horarios_normais_validos].values


# --- 6. PLOTAR OS PONTOS EXATOS SOBRE A LINHA ---
ax.scatter(
    pd.to_datetime(horarios_normais_validos).to_pydatetime(),
    valores_na_linha_normais,
    color="gray",
    s=40,
    edgecolor="black",
    linewidth=0.3,
    alpha=0.7,
    zorder=4,
)

# --- 7. FORMATAÇÃO DO EIXO X E DO GRÁFICO ---
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate(rotation=0)

ax.set_xlabel("Hora")
ax.set_ylabel("Nº de criação de conta")

# O título muda, pois agora estamos mostrando o cenário sem anomalias
ax.set_title(
    "Dia 11 - Sábado\nVolume de criação de contas (Sem Spam)", fontsize="14", color="black"
)

ax.spines[["top", "right"]].set_visible(False)
ax.grid(visible=True, color="gray", linestyle="--", linewidth=0.2, alpha=0.5)

ax.set_ylim(-0.5,10)

# --- 8. SALVAR (SEMPRE ANTES DO SHOW) E EXIBIR ---
fig.savefig(
    FIG_PATH / "02-no_spam_account_line_day11.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)

plt.show()

# %%
# Agrupamento base a cada 15 min (marcado à direita para criar o efeito de subida)
por_hora = df.set_index("createdAt").resample("15min", label="right").size()

# Garantir que o eixo X cubra todo o período desejado
eixo_completo = pd.date_range(
    "2026-07-12 12:00:00",
    "2026-07-12 21:00:00",
    freq="15min",
)
por_hora = por_hora.reindex(eixo_completo, fill_value=0)

# --- 2. GRÁFICO BASE (A LINHA) ---
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(por_hora.index.to_pydatetime(), por_hora.values, color="lightgrey")


# --- 3. HORÁRIOS EXATOS DENTRO DO LIMITE DO GRÁFICO ---
# Sem filtros de spam, pegamos simplesmente todos os horários únicos de criação
horarios_unicos = df["createdAt"].unique()

# Filtramos apenas os que estão dentro da janela do gráfico (13h às 21h)
horarios_validos = [
    h
    for h in horarios_unicos
    if por_hora.index.min() <= h <= por_hora.index.max()
]


# --- 4. INTERPOLAÇÃO (Para colar os pontos na linha) ---
# Unimos o índice de 15 em 15 min com os horários quebrados das criações
indice_combinado = por_hora.index.union(horarios_validos)

# Interpolamos para achar a altura Y exata de cada ponto no meio do caminho
por_hora_interpolado = por_hora.reindex(indice_combinado).interpolate(
    method="time"
)

# Extraímos as alturas finais
valores_na_linha = por_hora_interpolado.loc[horarios_validos].values


# --- 5. PLOTAR OS PONTOS EXATOS SOBRE A LINHA ---
ax.scatter(
    pd.to_datetime(horarios_validos).to_pydatetime(),
    valores_na_linha,
    color="gray",  # Azul padrão para destacar a nuvem de criações normais
    s=40,
    edgecolor="black",
    linewidth=0.3,
    alpha=0.7,
    zorder=4,
)


# --- 6. FORMATAÇÃO DO EIXO X E DO GRÁFICO ---
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate(rotation=0)

ax.set_xlabel("Hora")
ax.set_ylabel("Nº de criação de conta")

# Título ajustado para um cenário sem anomalias
ax.set_title(
    "Dia 12 - Domingo\nVolume de criação de contas",
    fontsize="14",
    color="black"
)

ax.set_ylim(-0.5,10)

ax.spines[["top", "right"]].set_visible(False)
ax.grid(visible=True, color="gray", linestyle="--", linewidth=0.2, alpha=0.5)

plt.show()

fig.savefig(
    FIG_PATH/ "03-no_spam_account_line_day12.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)

# %%
# Garantir que a coluna está no formato datetime
df["createdAt"] = pd.to_datetime(df["createdAt"])

# --- 2. FILTRAR OS DATETIMES BRUTOS (Suspeitos vs Normais) ---
horas_normais = df[~df["id"].isin(ids_para_remover)]["createdAt"]

# --- 3. DEFINIR OS INTERVALOS (BINS) DO HISTOGRAMA ---
bins_horas = pd.date_range(
    "2026-07-11 12:00:00",
    "2026-07-11 21:00:00",
    freq="h",
)

# --- 4. CONSTRUIR O GRÁFICO ---
fig, ax = plt.subplots(figsize=(12, 5))

# Plotando o histograma empilhado
ax.hist(
    horas_normais,
    bins=bins_horas,
    stacked=True,
    color="darkgrey",
    edgecolor="white",
    alpha=0.8,
)

# --- 5. CALCULAR E ADICIONAR OS RÓTULOS DE TEXTO EM CADA COLUNA ---
# Calculamos a quantidade exata por bin para posicionar os textos
counts_normais, _ = np.histogram(horas_normais.values, bins=bins_horas.values)


# Encontra o centro de cada barra no eixo X para centralizar o texto
bin_centers = bins_horas[:-1] + pd.Timedelta(minutes=30)

for center, norm_c in zip(bin_centers, counts_normais):
    if norm_c > 0:
        y_pos_norm = norm_c + 1
        txt_norm = ax.text(
            center,
            y_pos_norm,
            str(int(norm_c)),
            ha="center",
            va="center",
            color='dimgray',
            fontsize=10,
        )


# --- 6. FORMATAÇÃO DOS EIXOS E TEXTOS ---
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate(rotation=0)


ax.set_xlabel("Hora")

ax.set_title(
    "Dia 11 - Sábado\nCriação de contas filtrada", fontsize="14", color="black"
)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_yticks([])
ax.set_ylim(0, 30)

ax.text(
    0.8, 0.5,
    "Total:",
    fontsize=13,
    color="gray",
    transform=ax.transAxes
)
ax.text(
    0.8, 0.43,
    "68 contas.",
    fontsize=13,
    color="dimgray",
    fontweight="medium",
    transform=ax.transAxes
)


plt.show()

fig.savefig(
    FIG_PATH/ "04-no_spam_account_hist_day11.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)

# %%
# Garantir que a coluna está no formato datetime
df["createdAt"] = pd.to_datetime(df["createdAt"])

# --- 2. FILTRAR OS DATETIMES BRUTOS (Suspeitos vs Normais) ---
horas_suspeitas = df[df["id"].isin(ids_para_remover)]["createdAt"]
horas_normais = df[~df["id"].isin(ids_para_remover)]["createdAt"]

# --- 3. DEFINIR OS INTERVALOS (BINS) DO HISTOGRAMA ---
bins_horas = pd.date_range(
    "2026-07-12 12:00:00",
    "2026-07-12 21:00:00",
    freq="h",
)

# --- 4. CONSTRUIR O GRÁFICO ---
fig, ax = plt.subplots(figsize=(12, 5))

# Plotando o histograma empilhado
ax.hist(
    [horas_normais],
    bins=bins_horas,
    stacked=True,
    color=["darkgrey"],
    edgecolor="white",
    alpha=0.8,
)

# --- 5. CALCULAR E ADICIONAR OS RÓTULOS DE TEXTO EM CADA COLUNA ---
# Calculamos a quantidade exata por bin para posicionar os textos
counts_normais, _ = np.histogram(horas_normais.values, bins=bins_horas.values)


# Encontra o centro de cada barra no eixo X para centralizar o texto
bin_centers = bins_horas[:-1] + pd.Timedelta(minutes=30)

for center, norm_c, spam_c in zip(bin_centers, counts_normais, counts_suspeitas):
    # Texto para Contas Normais (Cinza Escuro, no centro do bloco cinza)
    if norm_c > 0:
        y_pos_norm = norm_c + 2
        txt_norm = ax.text(
            center,
            y_pos_norm,
            str(int(norm_c)),
            ha="center",
            va="center",
            color='gray',
            fontsize=12,
        )


# --- 6. FORMATAÇÃO DOS EIXOS E TEXTOS ---
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
fig.autofmt_xdate(rotation=0)

ax.set_xlabel("Hora")

ax.set_title(
    "Dia 12 - Domingo", fontsize="14", color="black"
)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_yticks([])
ax.set_ylim(0, 30)

ax.text(
    0.8, 0.5,
    "Total:",
    fontsize=13,
    color="gray",
    transform=ax.transAxes
)

ax.text(
    0.8, 0.43,
    "41 contas.",
    fontsize=13,
    color="dimgrey",
    fontweight="medium",
    transform=ax.transAxes
)


plt.show()

fig.savefig(
    FIG_PATH/ "05-no_spam_account_hist_day12.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)
