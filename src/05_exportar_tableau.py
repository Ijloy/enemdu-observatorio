"""
Exporta la capa oro a CSV con nombres claros para Tableau (data/tableau/).

Uso:  python src/05_exportar_tableau.py
"""
import pandas as pd

from config import ORO, TABLEAU

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
NOMBRES = {
    "anio": "Año", "dimension": "Dimensión", "grupo": "Grupo",
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


def guardar(df: pd.DataFrame, nombre: str) -> None:
    df.to_csv(TABLEAU / nombre, index=False, encoding="utf-8")
    print(f"  {nombre}: {len(df)} filas")


def main() -> None:
    TABLEAU.mkdir(parents=True, exist_ok=True)

    if (ORO / "indicadores_anuales.csv").exists():
        a = pd.read_csv(ORO / "indicadores_anuales.csv")
        guardar(redondear(a.rename(columns=NOMBRES)), "indicadores_anuales.csv")

        c = pd.read_csv(ORO / "composicion_pea_anual.csv")
        c = c.rename(columns={"anio": "Año", "categoria_pea": "Categoría",
                              "personas": "Personas", "porcentaje": "Porcentaje de la PEA"})
        c["Personas"] = c["Personas"].round(0).astype("int64")
        c["Porcentaje de la PEA"] = c["Porcentaje de la PEA"].round(1)
        guardar(c, "composicion_pea.csv")

    m = pd.read_csv(ORO / "indicadores_mensuales_2025.csv")
    m.insert(0, "Fecha", pd.to_datetime(dict(year=2025, month=m["mes"], day=1)).dt.date)
    m.insert(1, "Mes", m["mes"].map(lambda x: MESES[x - 1]))
    guardar(redondear(m.drop(columns="mes").rename(columns=NOMBRES)), "indicadores_mensuales.csv")

    t = pd.read_csv(ORO / "ciudades_trimestral_2025.csv")
    t.insert(0, "Trimestre", "T" + t["trimestre"].astype(str) + " 2025")
    t = t.drop(columns=["trimestre", "dimension"]).rename(columns=NOMBRES).rename(columns={"Grupo": "Ciudad"})
    guardar(redondear(t), "ciudades_trimestral.csv")

    v = pd.read_csv(ORO / "validacion_inec.csv")
    v["indicador"] = v["indicador"].map(NOMBRES)
    v = v.rename(columns={"periodo": "Periodo", "nivel": "Nivel", "indicador": "Indicador",
                          "nuestro": "Cálculo propio (%)", "inec": "Cifra INEC (%)",
                          "diferencia": "Diferencia (pts)", "fuente": "Fuente"})
    guardar(v, "validacion_inec.csv")


if __name__ == "__main__":
    main()
