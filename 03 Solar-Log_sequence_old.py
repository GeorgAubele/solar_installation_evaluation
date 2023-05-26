# -*- coding: utf-8 -*-
# =============================================================================
# Serialisieren des Einlesens, S�uberns und Anh�ngens an eine bestehende Datei
#
# Plotten wird ausgelassen
# =============================================================================

# =============================================================================
#
# =============================================================================

# Import
# import numpy as np
import datetime as dt
import pandas as pd
import pyarrow
import glob
from os.path import exists

# %% Erstellen einer Liste aller Backup-Dateien

data_files = glob.glob("./Backups_old/*")

# %% Zusammenfassen der SChritte für eine Datei
# Genauere Kommentare in den anderen Scripten (input)


def read_dat_file(filename):
    return pd.read_csv(filename, delimiter=";", header=None,
                       skiprows=6, na_values='', parse_dates=[2], dayfirst=True)
# %%
# Ausfiltern der Datensätze, die nicht zum "Stamm" gehören


def clean_up(df0):
    """
    Aufr�umen und umbenennen
    Detailiertere Erklärungen im anderen File (input)
    """
    df1 = df0[(df0.iloc[:, 0] == "2") & (df0.iloc[:, 1] == "0")]
    # df1[[0, 1]] = df1[[0, 1]].astype(str)
    # Umwandeln der  Spalten in int außer dem Datum
    help_list = [i for i in range(32)]
    help_list.remove(2)
    df1.iloc[:, help_list] = df1.iloc[:, help_list].astype(int)

    # L�schen der unn�tigen Spalten, da diese nur Kontroll-Parameter enthalten

    drop_list_raw = [i for i in range(32)]
    # except_list = [2, 6, 8, 10, 15, 17, 19, 23, 25, 27, 29, 31]
    except_list = [2, 6, 10, 15, 23, 27, 31]
    drop_list = [i for i in drop_list_raw if i not in except_list]

    df2 = df1.drop(df1.columns[drop_list], axis=1)

    # # Umbenennen der Spalte mit dem DateTime
    df2 = df2.rename(columns={2: 'DateTime'})

    # # Setzen des DateTime als Index
    # df2 = df2.set_index(df2.columns[0])

    # print_list = [6, 8, 10, 15, 17, 19, 23, 25, 27, 29, 31]

    # # Umformatieren und Aufräumen der Spalten
    # new_keep_list = [6, 10, 15, 23, 27, 31]
    # new_drop_list = [i for i in print_list if i not in new_keep_list]
    # df2 = df1.drop(new_drop_list, axis=1)

    # Spalten Umbenennen

    name_dict = {6: "Verbrauch", 10: "Verbrauch_kum", 15: "Ertrag_gesamt",
                 23: "Ertrag_S1", 27: "Ertrag_S2", 31: "Ertrag_kum"}

    df2 = df2.rename(columns=name_dict)

    # Aufspalten des DateTime in verschiedene Spalten, um später evtl.
    # einen Multiindex aufbauen zu können

    # Reset Index, um den Zugriff beim Ausplitten zu vereinfachen
    # df2 = df2.reset_index()

    # Neue Datumsspalten einfügen
    df2['day'] = df2["DateTime"].dt.day
    df2['month'] = df2["DateTime"].dt.month
    df2['year'] = df2["DateTime"].dt.year
    df2['time'] = df2["DateTime"].dt.time
    df2['weekday_number'] = df2["DateTime"].dt.weekday
    df2['weekday'] = df2["DateTime"].dt.strftime("%A")

    # Index wieder auf DateTime umstellen
    df2 = df2.set_index("DateTime")
    # df2['time'] = pd.to_datetime(df2["time"], format="%H:%M:%S")

    # Wieder Speicher sparen
    # df2.iloc[:, [6, 7, 8, 10]] = df1.iloc[:, [6, 7, 8, 10]].astype(int)
    return df2

# %%


def read_data():
    try:
        # return pd.read_parquet("solar_data_01.parquet")
        return pd.read_pickle("solar_data_01.pkl")
    except:
        pass

# %%


def combine_and_clean_data(df1: pd.DataFrame(), df2: pd.DataFrame()):
    df_con = pd.concat([df1, df2])
    # Dups rauswerfen
    df_clean = df_con.drop_duplicates()
    return df_clean


# %%

def write_data(df):
    # df.to_parquet("solar_data_01.parquet", engine="pyarrow", index=True)
    df.to_pickle("solar_data_01.pkl")

# %%


# Jetzt geht's los!
counter = 0
for file in data_files:
    # if counter == 1:
    #     break
    counter += 1
    #     break
    # Einlesen
    df0 = read_dat_file(file)
    # Säubern
    df1 = clean_up(df0)
    # Falls noch nichts angelegt, schreiben, ...
    if not exists("solar_data_01.pkl"):
        write_data(df1)
    # ... ansonsten lesen, anhängen, dups entfernen und wieder schreiben
    else:
        df2 = read_data()
        df_clean = combine_and_clean_data(df1, df2)
        df_clean.sort_index(inplace=True)
        write_data(df_clean)
        # counter += 1


df4 = read_data()

# df0 = read_dat_file(data_files[1])
# df2 = clean_up(df0)
# df3 = write_data(df2)
