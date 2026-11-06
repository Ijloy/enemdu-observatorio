"""
Validación de la capa oro contra cifras oficiales del INEC.
Genera data/oro/validacion_inec.csv (se muestra en el dashboard).

Uso:  python src/04_validacion.py
"""
import pandas as pd

from config import ORO

ANUAL = "INEC, ENEMDU anual (boletín técnico)"
MENSUAL = "INEC, boletín ENEMDU mensual"
CIUDAD = "INEC vía Bloomberg Línea"

# (periodo, nivel, indicador, valor_inec, fuente)
OFICIAL = [
    *[(str(a), "Nacional", ind, v, ANUAL) for a, vals in {
        2021: (66.0, 32.5, 23.2, 5.2),
        2022: (65.9, 34.4, 22.2, 4.4),
        2023: (64.7, 36.3, 19.6, 3.8),
        2024: (64.3, 35.9, 21.0, 3.7),
        2025: (64.3, 37.1, 19.4, 3.6),
      }.items() for ind, v in zip(["tpg", "tasa_adecuado", "tasa_subempleo", "tasa_desempleo"], vals)],
    ("May 2025", "Nacional", "tasa_adecuado", 35.2, MENSUAL),
    ("May 2025", "Nacional", "tasa_desempleo", 4.1, MENSUAL),
    ("Dic 2025", "Nacional", "tasa_adecuado", 37.1, MENSUAL),
    ("Dic 2025", "Nacional", "tasa_desempleo", 2.6, MENSUAL),
    ("T1 2025", "Quito", "tasa_adecuado", 53.9, CIUDAD),
    ("T1 2025", "Quito", "tasa_subempleo", 14.7, CIUDAD),
    ("T1 2025", "Quito", "tasa_desempleo", 7.7, CIUDAD),
]
MESES = {"May 2025": 5, "Dic 2025": 12}


def buscar(periodo, nivel, ind, anual, mensual, trim):
    if periodo.isdigit():
        if anual is None:
            return None
        f = anual[(anual["dimension"] == "Nacional") & (anual["anio"] == int(periodo))]
    elif periodo in MESES:
        f = mensual[(mensual["dimension"] == "Nacional") & (mensual["mes"] == MESES[periodo])]
    else:
        f = trim[(trim["grupo"] == nivel) & (trim["trimestre"] == int(periodo[1]))]
    return None if f.empty else round(float(f[ind].iloc[0]), 1)


def main() -> None:
    ruta_anual = ORO / "indicadores_anuales.csv"
    anual = pd.read_csv(ruta_anual) if ruta_anual.exists() else None
    mensual = pd.read_csv(ORO / "indicadores_mensuales_2025.csv")
    trim = pd.read_csv(ORO / "ciudades_trimestral_2025.csv")

    filas = []
    for periodo, nivel, ind, oficial, fuente in OFICIAL:
        nuestro = buscar(periodo, nivel, ind, anual, mensual, trim)
        if nuestro is None:
            continue
        filas.append({"periodo": periodo, "nivel": nivel, "indicador": ind, "nuestro": nuestro,
                      "inec": oficial, "diferencia": round(nuestro - oficial, 1), "fuente": fuente})
    val = pd.DataFrame(filas)
    val.to_csv(ORO / "validacion_inec.csv", index=False, encoding="utf-8")
    print(val.drop(columns="fuente").to_string(index=False))
    print(f"\nDiferencia absoluta máxima: {val['diferencia'].abs().max()} puntos")


if __name__ == "__main__":
    main()
