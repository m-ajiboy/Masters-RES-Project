"""Reproduces Amiris_Inputdata.xlsx with all German headings translated to English,
preserving data, formulas, merged cells, and formatting. Translation is a straight
find-and-replace on known header cell text, applied only to header rows.
"""
import openpyxl

SRC = "Amiris_Inputdata.xlsx"
OUT = "Amiris_Inputdata_EN.xlsx"

TRANSLATE = {
    # Section titles (Capacity sheet, row 1, merged)
    "Brutto Stromerzeugungskapazitäten - GW": "Gross Electricity Generation Capacity - GW",
    "Brutto Stromerzeugung - TWh": "Gross Electricity Generation - TWh",
    "Brutto Stromnachfrage - TWh": "Gross Electricity Demand - TWh",
    # Capacity sheet, row 2 (column headers)
    "Jahr": "Year",
    "Kernkraft": "Nuclear",
    "Braunkohle": "Lignite",
    "Steinkohle": "Hard Coal",
    "Gas": "Natural Gas",
    "Öl": "Oil",
    "Sonstige Fossile": "Other Fossil",
    "Reservoir": "Reservoir Hydro",
    "Wind Onshore": "Wind Onshore",
    "Wind Offshore": "Wind Offshore",
    "Laufwasserkraftwerke": "Run-of-River Hydro",
    "Sonstige EE": "Other Renewables",
    "Solar Netzeinspeisung": "Solar (Grid Feed-in)",
    "Solar Prosuming": "Solar (Prosumer/Self-consumption)",
    "Pumpspeicher": "Pumped Hydro Storage",
    "Jahreshöchstlast": "Annual Peak Load",
    "Leistung Großbatteriespeicher": "Large-Scale Battery Storage Power",
    "(Lauf-)Wasserkraft": "Run-of-River Hydro",
    "Inflexible Bruttostromnachfrage": "Inflexible Gross Electricity Demand",
    "Elektrolyse": "Electrolysis (Hydrogen Production)",
    "Elektromobilität": "Electric Mobility (EV Charging)",
    "Wärmepumpen": "Heat Pumps",
    "Netto-Exporte": "Net Exports",
    "Pumpspeicher Verluste": "Pumped Storage Losses",
    # Variable_cost sheet
    "real, 2024": "real (2024 EUR prices)",
    "Datum": "Date",
    "Steinkohle [USD/t]": "Hard Coal [USD/tonne]",
    "Rohöl Brent [USD/bbl]": "Crude Oil Brent [USD/barrel]",
    "Gas-TTF [EUR/MWh]": "Natural Gas TTF (Netherlands hub) [EUR/MWh]",
    "Gas-UK [ppt]": "Natural Gas UK NBP [pence/therm]",
    "Gas-IT [EUR/MWh]": "Natural Gas Italy [EUR/MWh]",
    "Gas-ES [EUR/MWh]": "Natural Gas Spain [EUR/MWh]",
    "Gas-DE [EUR/MWh]": "Natural Gas Germany [EUR/MWh]",
    "USD Wechselkurs [USD/EUR]": "USD Exchange Rate [USD/EUR]",
    "GBP Wechselkurs [GBP/EUR]": "GBP Exchange Rate [GBP/EUR]",
    "EUA [EUR/tCO2]": "EUA - EU Emission Allowance [EUR/tCO2]",
    # emission_factor sheet
    "Emission_Gas": "Emission_Natural_Gas",
    "Emission_Oil": "Emission_Oil",
    "Emission_Steinkohle": "Emission_Hard_Coal",
    "Emission_Braunkohle": "Emission_Lignite",
    "Emission_Electricity_2025": "Emission_Electricity_Grid_2025",
}

wb = openpyxl.load_workbook(SRC, data_only=False)
changed = 0
untranslated_seen = set()

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                key = cell.value.strip()
                if key in TRANSLATE:
                    cell.value = TRANSLATE[key]
                    changed += 1
                elif any(ch in key for ch in "äöüÄÖÜß") and key not in TRANSLATE:
                    untranslated_seen.add((ws.title, key))

wb.save(OUT)
print(f"Saved {OUT} - {changed} header cells translated")
if untranslated_seen:
    print("WARNING - German text found with no translation entry:")
    for sheet, text in sorted(untranslated_seen):
        print(f"  [{sheet}] {text!r}")
else:
    print("No untranslated German text remains.")
