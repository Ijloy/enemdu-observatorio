"""
Paso 5: prepara los CSV para Tableau Public (nombres claros, fecha, etiquetas).
Salida: data/tableau/

Uso:
    python src/05_exportar_tableau.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PROC = RAIZ / "data" / "processed"
OUT = RAIZ / "data" / "tableau"

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
NOMBRES = {
    "dimension": "Dimensión", "grupo": "Grupo",
    "pet": "PET (15+ años)", "pea": "PEA",
    "tpg": "Tasa de participación global",
    "tasa_adecuado": "Empleo adecuado", "tasa_subempleo": "Subempleo",
    "tasa_otro_no_pleno": "Otro empleo no pleno",
    "tasa_no_remunerado": "Empleo no remunerado", "tasa_desempleo": "Desempleo",
}


TASAS = ["Tasa de participación global", "Empleo adecuado", "Subempleo",
         "Otro empleo no pleno", "Empleo no remunerado", "Desempleo"]


def redondear(df: pd.DataFrame) -> pd.DataFrame:
    """Tasas a 1 decimal (como publica el INEC) y poblaciones sin decimales."""
    cols = [c for c in TASAS if c in df.columns]
    df[cols] = df[cols].round(1)
    for c in ["PET (15+ años)", "PEA"]:
        if c in df.columns:
            df[c] = df[c].round(0).astype("int64")
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    m = pd.read_csv(PROC / "indicadores_2025.csv")
    m.insert(0, "Fecha", pd.to_datetime(dict(year=2025, month=m["mes"], day=1)).dt.date)
    m.insert(1, "Mes", m["mes"].map(lambda x: MESES[x - 1]))
    m = redondear(m.drop(columns="mes").rename(columns=NOMBRES))
    m.to_csv(OUT / "indicadores_mensuales.csv", index=False, encoding="utf-8")

    t = pd.read_csv(PROC / "ciudades_trimestral_2025.csv")
    t.insert(0, "Trimestre", "T" + t["trimestre"].astype(str) + " 2025")
    t = t.drop(columns=["trimestre", "dimension"]).rename(columns=NOMBRES)
    t = redondear(t.rename(columns={"Grupo": "Ciudad"}))
    t.to_csv(OUT / "ciudades_trimestral.csv", index=False, encoding="utf-8")

    v = pd.read_csv(PROC / "validacion_inec.csv")
    v["indicador"] = v["indicador"].map(NOMBRES)
    v = v.rename(columns={"periodo": "Periodo", "nivel": "Nivel", "indicador": "Indicador",
                          "nuestro": "Cálculo propio (%)", "inec": "Cifra INEC (%)",
                          "diferencia": "Diferencia (pts)", "fuente": "Fuente"})
    v.to_csv(OUT / "validacion_inec.csv", index=False, encoding="utf-8")

    for f in sorted(OUT.glob("*.csv")):
        print(f"{f.name}: {len(pd.read_csv(f))} filas")


if __name__ == "__main__":
    main()
