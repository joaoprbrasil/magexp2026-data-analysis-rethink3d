# %%
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt


pd.set_option("display.max_columns", None)   # mostra todas as colunas
pd.set_option("display.width", None)         # não quebra pela largura do terminal
pd.set_option("display.max_rows", 100)       # opcional, se as linhas também cortarem

try:
    ROOT = Path(__file__).resolve().parents[1]
except NameError:
    ROOT = Path.cwd()

DF_PATH = ROOT / "data" / "processed" / "dataset.csv"
FIG_PATH = ROOT / "reports" / "figures"
df = pd.read_csv(DF_PATH)

