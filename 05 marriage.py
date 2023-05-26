# =============================================================================
#
# Vereinigung der Dateien
#
# =============================================================================

# =============================================================================
# Lücke in den Daten (Backups unvollständig)
# vom 29.10.2018 0:00 bis zum 07.11.2018 23:59
# =============================================================================


import pandas as pd


# %%


df1 = pd.read_pickle("solar_data_01.pkl")

df2 = pd.read_pickle("solar_data_02.pkl")

df_con = pd.concat([df1, df2])
df_clean = df_con.drop_duplicates()

df_clean.to_pickle("solar_data.pkl")
