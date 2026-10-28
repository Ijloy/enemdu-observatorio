"""
Paso 4: compara nuestras cifras con las cifras oficiales publicadas por el INEC.
Genera data/processed/validacion_inec.csv (se mostrará en la app).

Uso:
    python src/04_validacion.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"

# Cifras oficiales (INEC). Fuente en cada fila.
OFICIAL = [
    # periodo, nivel, indicador, valor_inec, fuente
    ("May 2025", "Nacional", "tpg", 65.4, "INEC, tabla resumen ENEMDU mensual"),
    ("May 2025", "Nacional", "tasa_adecuado", 35.2, "INEC, tabla resumen ENEMDU mensual"),
    ("May 2025", "Nacional", "tasa_subempleo", 20.9, "INEC, tabla resumen ENEMDU mensual"),
    ("May 2025", "Nacional", "tasa_desempleo", 4.1, "INEC, tabla resumen ENEMDU mensual"),
    ("Dic 2025", "Nacional", "tasa_adecuado", 37.1, "INEC, boletín ENEMDU dic-2025"),
    ("Dic 2025", "Nacional", "tasa_subempleo", 17.4, "INEC, boletín ENEMDU dic-2025"),
    ("Dic 2025", "Nacional", "tasa_desempleo", 2.6, "INEC, boletín ENEMDU dic-2025"),
    ("T1 2025", "Quito", "tasa_adecuado", 53.9, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Quito", "tasa_subempleo", 14.7, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Quito", "tasa_desempleo", 7.7, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Guayaquil", "tasa_adecuado", 48.3, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Guayaquil", "tasa_subempleo", 21.0, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Guayaquil", "tasa_desempleo", 3.6, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Cuenca", "tasa_adecuado", 59.3, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Cuenca", "tasa_subempleo", 10.6, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Cuenca", "tasa_desempleo", 5.2, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Machala", "tasa_adecuado", 45.0, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Machala", "tasa_subempleo", 20.4, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Machala", "tasa_desempleo", 5.8, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Ambato", "tasa_adecuado", 44.0, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Ambato", "tasa_subempleo", 19.9, "INEC vía Bloomberg Línea"),
    ("T1 2025", "Ambato", "tasa_desempleo", 4.0, "INEC vía Bloomberg Línea"),
]
MESES = {"May 2025": 5, "Dic 2025": 12}


def main() -> None:
    mensual = pd.read_csv(PROC / "indicadores_2025.csv")
    trim = pd.read_csv(PROC / "ciudades_trimestral_2025.csv")

    filas = []
    for periodo, nivel, ind, oficial, fuente in OFICIAL:
        if nivel == "Nacional":
            fila = mensual[(mensual["dimension"] == "Nacional") & (mensual["mes"] == MESES[periodo])]
        else:
            fila = trim[(trim["grupo"] == nivel) & (trim["trimestre"] == int(periodo[1]))]
        nuestro = round(float(fila[ind].iloc[0]), 1)
        filas.append({"periodo": periodo, "nivel": nivel, "indicador": ind,
                      "nuestro": nuestro, "inec": oficial,
                      "diferencia": round(nuestro - oficial, 1), "fuente": fuente})

    val = pd.DataFrame(filas)
    val.to_csv(PROC / "validacion_inec.csv", index=False, encoding="utf-8")
    print(val.drop(columns="fuente").to_string(index=False))
    print(f"\nDiferencia absoluta máxima: {val['diferencia'].abs().max()} puntos")


if __name__ == "__main__":
    main()
