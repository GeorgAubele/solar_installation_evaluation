# -*- coding: utf-8 -*-
# Import
# import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt

# %% Einlesen einer Datei

# mit Pandas

# Problem: Die ersten Zeilen haben weniger Items, danach macht er dann NaN
# Anscheinend orientiert sich Pandas nicht an der maximalen Anzahl von Einträgen
# pro Zeile, sondern an der Anzahl der Einträge in den ersten paar Zeilen
# Lösung: skiprows

df0 = pd.read_csv("backup_data_16.04.23.dat", delimiter=";", header=None,
                  skiprows=31, na_values='', parse_dates=[2], dayfirst=True)


# %%
# Ausfiltern der Datensätze, die nicht zum "Stamm" gehören
# Warum auch immer, im alten Format sind die Einträge Strings, im neuen Zahlen
df1 = df0[(df0.iloc[:, 0] == 2) & (df0.iloc[:, 1] == 0)]

# %%

# Umwandeln der  Spalten außer dem Datum, um Speicherplatz zu sparen
# Anlegen einer Hilfsliste mit allen Spalten außer der 2
help_list = [i for i in range(202)]
# droppen der 2
help_list.remove(2)

# Umwandeln in int32, um Speicher zu sparen
df1.iloc[:, help_list] = df1.iloc[:, help_list].astype(int)


# %%
# Löschen der unnötigen Spalten, da diese nur Kontroll-Parameter enthalten

drop_list_raw = [i for i in range(202)]
except_list = [2, 6, 10, 14, 17, 19, 21, 25, 27, 29, 33, 35,
               40, 42, 44, 48, 53, 57, 61, 64, 68, 75, 79, 92,
               134, 136, 138]
drop_list = [i for i in drop_list_raw if i not in except_list]


df1 = df1.drop(df1.columns[drop_list], axis=1)


# # Umbenennen der Spalte mit dem DateTime
df1 = df1.rename(columns={2: 'DateTime'})


# # Setzen des DateTime als Index
df1 = df1.set_index(df1.columns[0])

# Begrenzen für die Graphen, um etwas zu erkennen
# df1_s = df1["2023-03-10"]

# Kopie, damit ich mit der Liste weiter unten arbeiten kann, wenn ich die
# Erstellung der Grpahen überspringe

print_list = [6, 10, 14, 17, 19, 21, 25, 27, 29, 33, 35,
              40, 42, 44, 48, 53, 57, 61, 64, 68, 75, 79, 92,
              134, 136, 138]

# %%

# Erstellen und Speichern der Graphen der übrigen Spalten
# Begrenzen für die Graphen, um etwas zu erkennen
df1_s = df1.loc["16-03-23"]


print_list = [6, 10, 14, 17, 19, 21, 25, 27, 29, 33, 35,
              40, 42, 44, 48, 53, 57, 61, 64, 68, 75, 79, 92,
              134, 136, 138]
for i in print_list:
    fig, ax = plt.subplots()
    x = df1_s.index
    y_1 = df1_s[i]
    # Begrenzen der x-Achse, um Daten besser erkennen zu können.
    # ax.set_xlim(dt.datetime(2023, 3, 10, 6, 0),dt.datetime(2023, 3, 10, 20, 0))
    ax.set_title(str(i))
    ax.plot(x, y_1)
    plt.show()
    dateiname = str(i)+".png"
    fig.savefig(dateiname, dpi=300)


# %% Umbenennen der Spalten, nach dem Herausfinden des Inhalts

# Alte Spalten zum Vergleich
# =============================================================================
# Übrige Spalten:
#     6 -> Verbrauch in W
#     8 -> Verbrauch kumuliert in 10^-2 Wh
#     10 -> Verbrauch kumuliert in Wh
#     15 -> P_Erzeugung Gesamt in W
#     17 -> AC Spannung
#     19 -> Kontroll Parameter, 3 wenn es läuft, 1?
#     23 -> P_Erzeugung String 1 in W
#     25 -> DC Spannung S1 in V
#     27 -> P_Erzeugung String 2 in W
#     29 -> DC Spannung S2 in V
#     31 -> Ertrag kummuliert in Wh
# =============================================================================


# Neue Spalten:
# =============================================================================
# Übrige Spalten:
#     2  -> DateTime
#     6 ->
#     10 -> Verbrauch kumuliert in Wh aus dem Netz
#     14 -> Verbrauch kumuliert in 10^-2 Wh aus dem Netz
#     17 -> Ertrag S1 und S1 in W (mit Verlust?)
#     19 -> Ertrag S1 in W
#     21 -> Ertrag S2 in W
#     25 -> Ertrag kumuliert in Wh
#     27 -> Spannung DC S1 in V
#     29 -> Spannung DC S2 in V
#     33 -> Spannung AC in V
#     35 -> Kontroll Parameter 0,1,3,5
#     40 -> Ladung der Batterie in W
#     42 -> Entladung der Batterie in W
#     44 -> Ladezustand der Batteris in %
#     48 -> Kontrollparameter 1, 4, 6
#     53 -> Verbruch in W
#     57 -> Verbrauch kumuliert aus der Batterie in Wh
#     61 -> Verbrauch kumuliert aus der Batterie in 10xWs
#     64 -> Ertrag S1 und S1 in W (mit Verlust?) - Seltsame Werte bei Nacht, nahezu identisch 17
#     68 -> Größe absolut 27000 Änderung in drei Tagen um 15
#     75 -> ???
#     79 -> ??? Treppenfunktion die um 3 Uhr abfällt
#     92 -> Geht nie unter 70, tagsüber oft auf 100 - Energieverbrauch Solarlog?
#     134 -> Kontrollparameter
#     136 -> ???  Evtl Speicherauslastung
#     138 -> ???  Evtl. Prozessorfreq.
# =============================================================================

# =============================================================================
# Einigung auf bestimmte Spalten für die Auswertung:
#                             Alt     Neu
#     Verbrauch in W:         6       53
#     Verbrauch_kum in Wh:    10      10 + 57
#     Ertrag_Gesamt in W:     15      17
#     Ertrag_S1 in W          23      19
#     Ertrag_S2 in W          27      21
#     Ertrag_kum in Wh        31      25
# =============================================================================

# %%  Umformatieren und Aufräumen der Spalten

new_keep_list = [53, 10, 57, 17, 19, 21, 25]

new_drop_list = [i for i in print_list if i not in new_keep_list]


df2 = df1.drop(new_drop_list, axis=1)

# %% Andere Spalten aufbauen (Verbrauch kum) bzw- Umbenennen

# Verbrauch kumuliert erstellen und einzelne Spalten löschen
df2["Verbrauch_kum"] = df2[10] + df2[57]
df2 = df2.drop([10, 57], axis=1)

# Andere Spalten umbenennen
name_dict = {53: "Verbrauch", 17: "Ertrag_gesamt", 19: "Ertrag_S1",
             21: "Ertrag_S2", 25: "Ertrag_kum"}

df2 = df2.rename(columns=name_dict)

# %%
# Aufspalten des DateTime in verschiedene Spalten, um später evtl.
# einen Multiindex aufbauen zu können

# Reset Index, um den Zugriff beim Ausplitten zu vereinfachen
df2 = df2.reset_index()

# Neue Datumsspalten einfügen
df2['day'] = df2["DateTime"].dt.day
df2['month'] = df2["DateTime"].dt.month
df2['year'] = df2["DateTime"].dt.year
df2['time'] = df2["DateTime"].dt.time
df2['weekday_number'] = df2["DateTime"].dt.weekday
df2['weekday'] = df2["DateTime"].dt.strftime("%A")

# Index wieder auf DateTime umstellen
df2 = df2.set_index("DateTime")
df2['time'] = pd.to_datetime(df2["time"], format="%H:%M:%S")

# Wieder Speicher sparen
df2.iloc[:, [6, 7, 8, 10]] = df1.iloc[:, [6, 7, 8, 10]].astype(int)

# %% Testweises Abspeichern
df2.info()
df2.to_parquet("example.parquet", engine="fastparquet", index=True)


# %% Testweises Laden
df3 = pd.read_parquet("example.parquet")
df3.info()
