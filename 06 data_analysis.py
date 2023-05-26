# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 23:36:30 2023

@author: Georg
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime


# %% Das große File einlesen

df0 = pd.read_pickle("solar_data.pkl")

df0.info()

df0.describe()

# %%
# =============================================================================
# Wichtige dfs erstellen
# =============================================================================

# %%
# Jeden Tag der maximale Ertrag 2015 bis 2020
df_cut = df0.loc["2015":"2022"]
# Tag Spalte für die Unterscheidung nach Tagen
df_cut['Tag'] = df_cut.index.date
# Gruppierung nach Tagen
df_Ertrag_daily = df_cut.groupby('Tag')['Ertrag_kum'].max().reset_index()
# Tag als Index
df_Ertrag_daily.set_index('Tag', inplace=True)
# Noch ein paar Spalten, die nützlich sein könnten
df_Ertrag_daily['Datum'] = pd.to_datetime(df_Ertrag_daily.index)
df_Ertrag_daily['Monat'] = df_Ertrag_daily['Datum'].dt.month
df_Ertrag_daily['Jahr'] = df_Ertrag_daily['Datum'].dt.year


df_Ertrag_daily.info()

# %%
# Für den Vergleich von Wochentagen
df_wochentag = df_Ertrag_daily.copy()
# Wochentag-Spalte einfügen
df_wochentag["Wochentag"] = df_Ertrag_daily["Datum"].dt.strftime("%A")


# %%
# Für Vergleich der Monatstage
df_monatstag = df_Ertrag_daily.copy()
# Spalte "MT" gibt den Tag im Monat an
df_monatstag["MT"] = df_Ertrag_daily["Datum"].dt.day


# %%
# Vergleich der Strings
# Beschränkung auf die Zeiten zwischen 10 Uhr und 16 Uhr
# 10 Uhr um Beschattung auszuschließen
start_time = datetime.time(10, 0)
end_time = datetime.time(16, 0)
df_time = df0.between_time(
    start_time, end_time, inclusive="both")

# Beschränkung auf die Monate mit der besten Einstrahlung,
# hier werden Unterschiede am deutlichsten.
df_strings = pd.concat([df_time.loc[df_time.index.month == 5],
                        df_time.loc[df_time.index.month == 6],
                        df_time.loc[df_time.index.month == 7],
                        df_time.loc[df_time.index.month == 8]])

# Sortieren wieder nach Jahren
df_strings = df_strings.sort_index()
# Löschen der nicht gebrauchten Spalten
df_strings = df_strings.drop(
    columns=["Verbrauch", "Verbrauch_kum", "weekday", "weekday_number"])

# Differenzspalte: 1-2
df_strings["Diff"] = df_strings["Ertrag_S1"] - df_strings["Ertrag_S2"]

df_strings.info()

# %%

# =============================================================================
# Erster Plot eines guten Tages, Ertrag im Tagesverlauf
# =============================================================================

df1 = df0.loc["2015-04-20"]


# Eingrenzen auf den interessanten Bereich
df1_filtered = df1.between_time("06:00:00", "22:00:00")

# Berechnen des Ertrages
ertrag = df1_filtered["Ertrag_kum"].max()/1000

# plot
fig, ax = plt.subplots()

# Linienplot
ax.plot(df1_filtered.index, df1_filtered['Ertrag_gesamt'],
        label=f"Gesamt: {ertrag:.2f} kWh")

# Strings
ax.plot(df1_filtered.index, df1_filtered['Ertrag_S1'],
        label="String 1", color="red")
ax.plot(df1_filtered.index, df1_filtered['Ertrag_S2'],
        label="String 2", color="green")

# Konvertieren der x-Achsen-Daten, damit die Uhrzeiten sauber dargestellt werden
myFmt = mdates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(myFmt)
plt.xticks(rotation=45)

# Ausfüllen des Zwischenraums
ax.fill_between(df1_filtered.index,
                df1_filtered['Ertrag_gesamt'], color='yellow', alpha=0.8)

# Titel und Achsenbeschriftungen
plt.title("Ertragsübersicht 20.April 2015")
ax.set(xlabel='Uhrzeit', ylabel='Ertrag')
ax.legend(loc=1)

plt.show()

# Abspeichern als png
fig.savefig("01 Tagesverlauf.png", dpi=600, bbox_inches='tight')


# %% Versuch einer polynimial regression

df1 = df0.loc["2015-04-20"]
df1_filtered = df1.between_time("06:00:00", "22:00:00")

# Index Reset, weil das Fitten ein Problem mit DateTime hat.
df2 = df1_filtered.reset_index()

# Berechnung Koeffizienten des Polynoms
z = np.polyfit(df2.index, df2["Ertrag_gesamt"], 5)

# Erstelllung des Polynomobjekts
p = np.poly1d(z)

fig, ax = plt.subplots()

# Linienplot
ax.plot(df2.index, df2['Ertrag_gesamt'], label="Daten")

# Plot der Fit-Kurve
ax.plot(df2.index, p(df2.index), label="Fit-Kurve")

# Titel, Achsen und Legende
ax.set(xlabel="Datenpunkte", ylabel="Ertrag in W")
plt.title("Versuch einer Fitkurve")
ax.legend()

plt.show()

# Abspeichern als png
fig.savefig("01a Tagesverlauf fit.png", dpi=600, bbox_inches='tight')

# %%

# =============================================================================
# Ertrag über einen Monat hinweg
# =============================================================================

# Begrenzen auf einen Monat
start_date = datetime.date(2015, 4, 1)
end_date = datetime.date(2015, 4, 30)
df_month = df_Ertrag_daily.loc[start_date:end_date]

# Datum umwandeln, damit man auf der x-Achse nur die Tage hinbekommt
df_month.index = pd.to_datetime(df_month.index)

# Durchschnitt berechnen
mean_max_val = df_month.Ertrag_kum.mean()/1000

# Plot
fig, ax = plt.subplots()

# Balkendiagramm
ax.bar(df_month.index.day, df_month['Ertrag_kum']/1000)

# Durschnittslinie
ax.axhline(mean_max_val, color='green', linestyle='--',
           label=f"Durchschnitt: {mean_max_val:.2f} kWh")
ax.axhline(18.1, color='red', linestyle='--',
           label="Gewünschter Wert 18.1 kWh")

# Achsen, Titel und Legende
ax.set_xlabel('Tag des Monats')
ax.set_ylabel('Ertrag pro Tag in kWh')
ax.set_title('Ertrag im April 2015')
legend = ax.legend(loc='upper center', bbox_to_anchor=(0.1, -0.1))

plt.show()

fig.savefig("03 Monatsverlauf.png", dpi=600, bbox_inches='tight')
# %%

# =============================================================================
# Ertrag über das Jahr 2015 hinweg
# =============================================================================

# df eingrenzen
df_year = df_Ertrag_daily[df_Ertrag_daily['Jahr'] == 2015]

# df gruppieren und summieren
df_monthly = df_year.groupby('Monat')['Ertrag_kum'].sum()

# Durchschnit berechnen
avg_val = df_monthly.mean()/1000


# Plot
fig, ax = plt.subplots()

# Säulendiagramm
ax.bar(df_monthly.index, df_monthly/1000)
# Durchschnittslinie
ax.axhline(avg_val, color='green', linestyle='--',
           label=f"Durchschnitt {avg_val:.2f} kWh")
ax.axhline(433, color='red', linestyle='--',
           label="Erwünschter Wert: 433 kWh")

# Achsen, Titel und Legende
ax.set_xlabel('Monate')
ax.set_ylabel('Ertrag pro Monat in kWh')
ax.set_title('Ertrag pro Monat im Jahr 2015')
legend = ax.legend(loc='upper center', bbox_to_anchor=(0.1, -0.1))


plt.show()
fig.savefig("04 Jahresverlauf.png", dpi=600, bbox_inches='tight')

# %%

# =============================================================================
# Vergleich von mehrern Jahren
# =============================================================================

# df gruppieren und summieren
df_yearly = df_Ertrag_daily.groupby('Jahr')['Ertrag_kum'].sum()

# Durchschnitt
avg_yearly = df_yearly.mean()/1000

# Plot
fig, ax = plt.subplots()

# Säulendiagramm
ax.bar(df_yearly.index, df_yearly/1000)

# Durschnittslinie
ax.axhline(avg_yearly, color='green', linestyle='--',
           label=f"Durchschnitt {avg_yearly:.2f} kWh")

ax.axhline(5200, color='red', linestyle='--',
           label="Erwünschter Wert: 5200 kWh")

# Achsen, Titel und Legende
ax.set_xlabel('Jahre')
ax.set_ylabel('Ertrag pro Jahr in kWh')
ax.set_title('Vergleich 2015 bis 2022')
legend = ax.legend(loc='upper center', bbox_to_anchor=(0.1, -0.1))


plt.show()

fig.savefig("05 Jahresvergleich.png", dpi=600, bbox_inches='tight')

# %%

# =============================================================================
# Vergleich der Wochentage über die Jahre 2015 bis 2022
# =============================================================================

# Dataframe day of week

df_dow = df_wochentag.groupby("Wochentag")["Ertrag_kum"].mean()

# Sortieren nach der korrekten Reihenfolge
df_dow = df_dow.reset_index()
cats = ['Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday']
df_dow['Wochentag'] = pd.Categorical(
    df_dow['Wochentag'], categories=cats, ordered=True)
df_dow = df_dow.sort_values('Wochentag')


# Durchschnitt und Standardanweichung
avg_dow = df_dow["Ertrag_kum"].mean()/1000
std_dow = df_dow["Ertrag_kum"].std()/1000

# Plot
fig, ax = plt.subplots()

# Säulendiagramm, Durchschnitt und Bereich darum
ax.bar(df_dow["Wochentag"], df_dow["Ertrag_kum"]/1000)
ax.axhline(avg_dow, color='red', linestyle='--',
           label=f"Durchschnitt {avg_dow:.2f} kWh ")

ax.axhspan(avg_dow - std_dow, avg_dow + std_dow, color='green',
           alpha=0.6, label="Standardabweichung")

# Achsenbegrenzung zur besseren Sichtbarkeit
ax.set_ylim([14, 16.1])

# Achsen, Titel und Legende
ax.set_xticklabels(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"])
ax.set_xlabel('Wochentage')
ax.set_ylabel('Durchschnittsertrag pro Wochentag in kWh')
ax.set_title('Vergleich Wochentage 2015 bis 2022')
legend = ax.legend(loc='upper center', bbox_to_anchor=(0.1, -0.1))

plt.show()

fig.savefig("06 Wochentage.png", dpi=600, bbox_inches='tight')


# %%

# =============================================================================
# Vergleich der Kalendertage in den Monaten
# =============================================================================

df_dom = df_monatstag.groupby("MT")["Ertrag_kum"].mean()

avg_dom = df_dom.mean()/1000

std_dom = df_dom.std()/1000

# Plot
fig, ax = plt.subplots()

# Säulendiagramm, Durchschnitt und Bereich darum
ax.bar(df_dom.index, df_dom/1000)
ax.axhline(avg_dow, color='red', linestyle='--',
           label=f"Durchschnitt {avg_dow:.2f} kWh ")

ax.axhspan(avg_dow - std_dow, avg_dow + std_dow, color='green',
           alpha=0.6, label="Standardabweichung")

# Achsenbegrenzung zur besseren Sichtbarkeit
ax.set_ylim([13, 18])

# Achsen, Titel und Legende
ax.set_xlabel('Tage im Monat')
ax.set_ylabel('Durchschnittsertrag pro Tag in kWh')
ax.set_title('Vergleich Kalendertage 2015 bis 2022')
legend = ax.legend(loc='upper center', bbox_to_anchor=(0.1, -0.1))

plt.show()

fig.savefig("07 Monatstage.png", dpi=600, bbox_inches='tight')

# %%

# =============================================================================
# String-Vergleichsplot
# =============================================================================

# Auswahle eines "guten" Tags mit viel Sonne

# df3 = df0.loc["2014-06-08"]
df3 = df0.loc["2022-06-14"]

# Eingrenzen auf den interessanten Bereich
df3_filtered = df3.between_time("05:00:00", "22:00:00")

# Plot erstellen

fig, ax = plt.subplots()

ax.plot(df3_filtered.index, df3_filtered['Ertrag_S1']/1000, label="String 1")
ax.plot(df3_filtered.index, df3_filtered['Ertrag_S2']/1000, label="String 2")

# Konvertieren der x-Achsen-Beschriftung in das richtige Format
myFmt = mdates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(myFmt)
plt.xticks(rotation=45)
# plt.title("Stringvergleich 08.Juni 2014")
plt.title("Stringvergleich 14.Juni 2022")
plt.legend()
ax.set(xlabel='Uhrzeit', ylabel='Ertrag in kW')

plt.show()

# Abspeichern als png
# fig.savefig("02a Stringvergleich 2014.png", dpi=600, bbox_inches='tight')
fig.savefig("02b Stringvergleich 2022.png", dpi=600, bbox_inches='tight')

# %%

# =============================================================================
# Vergleich der Strings im Jahr 2014 zu 2022
# Eingeschränkt auf die Monate Mai bis August, da in diesen die
# Sonneneinstrahlung am steilsten ist und somit Unterschiede
# in der Leistung am ehesten sichtbar werden
# =============================================================================

# Summe der Differenzen pro Tag zwischen den Strings: 1 - 2
df_s = df_strings.resample('D').sum(numeric_only=True)
# Entfernen der übrigen Tage
df_s = df_s[df_s["Ertrag_gesamt"] != 0]
# Index resetten, damit der Graph keine Lücken hat
df_s = df_s.reset_index()


# plot
fig, ax = plt.subplots()

ax.plot(df_s.index, df_s["Diff"]/1000)

# Nulllinie
ax.axhline(0, color='red', linestyle='--')

# Achsen und Titel
ax.set_xlabel('Tage')
ax.set_ylabel("Differenleistung S1 - S2 aufsummiert pro Tag")
ax.set_title('Vergleich der Strings 2014 bis 2022')

plt.show()

fig.savefig("08 Stringvergleich_01.png", dpi=600, bbox_inches='tight')

# %%

# =============================================================================
# Das ganze mal realtiv zum Ertrag von String 1
# =============================================================================
df_s["rel"] = df_s["Diff"]/df_s["Ertrag_S1"]

# plot
fig, ax = plt.subplots()

ax.plot(df_s.index, df_s["rel"])

# Nulllinie
ax.axhline(0, color='red', linestyle='--')

# Achsen und Titel
ax.set_xlabel('Tage')
ax.set_ylabel("relative Differenleistung pro Tag")
ax.set_title('Vergleich der Strings 2014 bis 2022')

plt.show()

fig.savefig("08a Stringvergleich_01_rel.png", dpi=600, bbox_inches='tight')

# %%

# =============================================================================
# Rolling Window über die Tage
# =============================================================================
res = df_s.rel.rolling(60).mean()
# Achsen und Titel

fig = res.plot(title="Stringvergleich Rolling Window")

# # Nulllinie
fig.axhline(y=0, color='red', linewidth=2, linestyle="--")

fig.set_xlabel('Tage')
fig.set_ylabel("relative Differenleistung pro Tag")
fig.set_title('Vergleich der Strings rolling')

fig2 = fig.get_figure()


fig2.savefig("08b Stringvergleich rolling", dpi=600)
