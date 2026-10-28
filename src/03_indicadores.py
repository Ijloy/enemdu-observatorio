"""
Paso 3b: calcula los indicadores del mercado laboral, ponderados con fexp,
para cada mes de 2025 y por grupos (nacional, área, sexo, edad, educación, ciudad).

Definiciones (INEC, según condact):
  PET  = 15 años y más                      -> condact 1..9
  PEA  = con empleo + con desempleo          -> condact 1..8
  Empleo adecuado                            -> condact 1
  Subempleo (tiempo + ingresos)              -> condact 2, 3
  Otro empleo no pleno                       -> condact 4
  Empleo no remunerado                       -> condact 5
  Desempleo (abierto + oculto)               -> condact 7, 8
Las tasas de empleo/subempleo/desempleo se calculan sobre la PEA;
la tasa de participación global (TPG) es PEA / PET.

Uso:
    python src/03_indicadores.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PARQUET = RAIZ / "data" / "processed" / "enemdu_personas_2025.parquet"
SALIDA = RAIZ / "data" / "processed" / "indicadores_2025.csv"
SALIDA_TRIM = RAIZ / "data" / "processed" / "ciudades_trimestral_2025.csv"

# Códigos INEC de las 5 ciudades autorrepresentadas
CIUDADES = {170150: "Quito", 90150: "Guayaquil", 10150: "Cuenca",
            70150: "Machala", 180150: "Ambato"}
SEXO = {1: "Hombre", 2: "Mujer"}
AREA = {1: "Urbana", 2: "Rural"}
EDUCACION = {1: "Ninguno", 2: "Centro de alfabetización", 3: "Educación básica",
             4: "Bachillerato", 5: "Superior"}


def preparar() -> pd.DataFrame:
    cols = ["mes", "condact", "fexp", "area", "p02", "p03", "nnivins", "ciudad"]
    df = pd.read_parquet(PARQUET, columns=cols)
    df = df[df["condact"].between(1, 9)].copy()  # solo PET (15+)

    c = df["condact"]
    w = df["fexp"]
    df["w_pet"] = w
    df["w_pea"] = np.where(c.between(1, 8), w, 0)
    df["w_adecuado"] = np.where(c == 1, w, 0)
    df["w_subempleo"] = np.where(c.isin([2, 3]), w, 0)
    df["w_otro_no_pleno"] = np.where(c == 4, w, 0)
    df["w_no_remunerado"] = np.where(c == 5, w, 0)
    df["w_desempleo"] = np.where(c.isin([7, 8]), w, 0)

    df["trimestre"] = (df["mes"] - 1) // 3 + 1
    df["nacional"] = "Nacional"
    df["area_txt"] = df["area"].map(AREA)
    df["sexo_txt"] = df["p02"].map(SEXO)
    df["edad_txt"] = pd.cut(df["p03"], bins=[14, 24, 34, 44, 64, 120],
                            labels=["15-24", "25-34", "35-44", "45-64", "65+"])
    df["educacion_txt"] = df["nnivins"].map(EDUCACION)
    df["ciudad_txt"] = pd.to_numeric(df["ciudad"], errors="coerce").map(CIUDADES)
    return df


def tasas(df: pd.DataFrame, columna: str, dimension: str, periodo: str = "mes") -> pd.DataFrame:
    w = [c for c in df.columns if c.startswith("w_")]
    g = (df.dropna(subset=[columna])
           .groupby([periodo, columna], observed=True)[w].sum()
           .reset_index()
           .rename(columns={columna: "grupo"}))
    out = pd.DataFrame({
        periodo: g[periodo],
        "dimension": dimension,
        "grupo": g["grupo"].astype(str),
        "pet": g["w_pet"].round(0),
        "pea": g["w_pea"].round(0),
        "tpg": 100 * g["w_pea"] / g["w_pet"],
    })
    for k in ["adecuado", "subempleo", "otro_no_pleno", "no_remunerado", "desempleo"]:
        out[f"tasa_{k}"] = 100 * g[f"w_{k}"] / g["w_pea"]
    return out


def main() -> None:
    df = preparar()
    partes = [
        tasas(df, "nacional", "Nacional"),
        tasas(df, "area_txt", "Área"),
        tasas(df, "sexo_txt", "Sexo"),
        tasas(df, "edad_txt", "Edad"),
        tasas(df, "educacion_txt", "Educación"),
        tasas(df, "ciudad_txt", "Ciudad"),
    ]
    res = pd.concat(partes, ignore_index=True)
    tasa_cols = [c for c in res.columns if c == "tpg" or c.startswith("tasa_")]
    res[tasa_cols] = res[tasa_cols].round(2)
    res.to_csv(SALIDA, index=False, encoding="utf-8")
    print(f"Guardado: {SALIDA} ({len(res)} filas)\n")

    cols = ["mes", "tpg", "tasa_adecuado", "tasa_subempleo", "tasa_desempleo"]
    print("NACIONAL por mes (%):")
    print(res[res["dimension"] == "Nacional"][cols].round(1).to_string(index=False))

    print("\nCIUDADES, diciembre (%):")
    cd = res[(res["dimension"] == "Ciudad") & (res["mes"] == 12)]
    print(cd[["grupo", "pea"] + cols[1:]].round(1).to_string(index=False))

    # Las cifras por ciudad del INEC son TRIMESTRALES (se juntan 3 meses de muestra)
    trim = tasas(df, "ciudad_txt", "Ciudad", periodo="trimestre")
    tc = [c for c in trim.columns if c == "tpg" or c.startswith("tasa_")]
    trim[tc] = trim[tc].round(2)
    trim[["pet", "pea"]] = (trim[["pet", "pea"]] / 3).round(0)  # promedio del trimestre
    trim.to_csv(SALIDA_TRIM, index=False, encoding="utf-8")
    print(f"\nGuardado: {SALIDA_TRIM}")
    print("\nCIUDADES por trimestre (%):")
    print(trim[["trimestre", "grupo", "tasa_adecuado", "tasa_subempleo", "tasa_desempleo"]]
          .round(1).to_string(index=False))


if __name__ == "__main__":
    main()
