# -*- coding: utf-8 -*-
# =============================================================================
# Serialisieren des Einlesens, Säuberns und Anhängens an eine bestehende Datei
#
# Plotten wird ausgelassen
# =============================================================================

# =============================================================================
# Lücke in den Daten (Backups unvollständig)
# vom 29.10.2018 0:00 bis zum 07.11.2018 23:59
# =============================================================================


# Import
# import numpy as np
import datetime as dt
import pandas as pd
import glob
from os.path import exists

# %% Erstellen einer Liste aller Backup-Dateien


data_files = glob.glob("./Backups_new/*")


# %% Zusammenfassen der SChritte für eine Datei
# Genauere Kommentare in den anderen Scripten (input)

def read_dat_file(filename):
    return pd.read_csv(filename, delimiter=";", header=None,
                       skiprows=31, warn_bad_lines=True, error_bad_lines=False,
                       na_values='', parse_dates=[2], dayfirst=True)

# %%
# Ausfiltern der Datensätze, die nicht zum "Stamm" gehören


def clean_up(df0):
    """
    Aufräumen und umbenennen 
    Detailiertere Erklärungen im anderen File (input)
    """

    df1 = df0[(df0.iloc[:, 0] == 2) & (df0.iloc[:, 1] == 0)]

    # Umwandeln der Spalten in int außer Datum
    help_list = [i for i in range(202)]
    help_list.remove(2)
    df1.iloc[:, help_list] = df1.iloc[:, help_list].astype(int)

    # Löschen der unnötigen Spalten, da diese nur Kontroll-Parameter enthalten
    drop_list_raw = [i for i in range(202)]
    except_list = [2, 10, 57, 17, 19, 21, 25, 53]

    drop_list = [i for i in drop_list_raw if i not in except_list]

    df1 = df1.drop(df1.columns[drop_list], axis=1)

    # # Umbenennen der Spalte mit dem DateTime
    df2 = df1.rename(columns={2: 'DateTime'})

    # # Setzen des DateTime als Index
    # df2 = df2.set_index(df2.columns[0])

    # Verbrauch kumuliert erstellen und einzelne Spalten löschen
    df2["Verbrauch_kum"] = df2[10] + df2[57]
    df2 = df2.drop([10, 57], axis=1)

    # Andere Spalten umbenennen
    name_dict = {53: "Verbrauch", 17: "Ertrag_gesamt", 19: "Ertrag_S1",
                 21: "Ertrag_S2", 25: "Ertrag_kum"}

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
    #df2.iloc[:, [6, 7, 8, 10]] = df2.iloc[:, [6, 7, 8, 10]].astype(int)
    return df2

# %%


def read_data():
    try:
        return pd.read_pickle("solar_data_02.pkl")
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
    df.to_pickle("solar_data_02.pkl")


# %%

# Jetzt geht's los!
# counter = 0
for file in data_files:
    # if counter == 4:
    #     break
    # Einlesen
    df0 = read_dat_file(file)
    # Säubern
    df1 = clean_up(df0)
    # Falls noch nichts angelegt, schreiben, ...
    if not exists("solar_data_02.pkl"):
        write_data(df1)
    # ... ansonsten lesen, anhängen, dups entfernen und wieder schreiben
    else:
        df2 = read_data()
        df_clean = combine_and_clean_data(df1, df2)
        df_clean.sort_index(inplace=True)
        write_data(df_clean)
        # counter += 1


# df4 = read_data()
