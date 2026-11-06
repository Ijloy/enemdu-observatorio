"""
CAPA PLATA – Limpieza y estandarización.
Toma la copia en bronce y deja una tabla limpia a nivel de persona:
  - solo las variables necesarias, con nombres claros
  - tipos correctos (enteros, decimales)
  - etiquetas legibles (sexo, área, condición de actividad, ciudad...)
  - controles de calidad (fexp positivo, códigos válidos)

Salida:  data/plata/personas_mensual.parquet  (bases mensuales)
         data/plata/personas_anual.parquet    (bases anuales del INEC)
Se guardan separadas porque cada base tiene su propio factor de expansión.

Uso:  python src/02_plata.py
"""
import pandas as pd

from config import (AREA, BRONCE_PARQUET, CATEGORIA_PEA, CIUDADES, CONDACT,
                    EDUCACION, PLATA, SEXO, VARIABLES)


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    faltan = [v for v in VARIABLES if v not in df.columns]
    if faltan:
        raise ValueError(f"Faltan variables en {df['archivo_origen'].iloc[0]}: {faltan}")

    p = df[["periodicidad", "anio", "mes", "archivo_origen"] + VARIABLES].copy()
    p = p.rename(columns={"condact": "condicion_actividad", "fexp": "factor_expansion",
                          "p02": "sexo_cod", "p03": "edad", "nnivins": "nivel_instruccion_cod",
                          "ciudad": "ciudad_cod", "area": "area_cod"})

    # Tipos
    for c in ["condicion_actividad", "sexo_cod", "edad", "nivel_instruccion_cod", "area_cod"]:
        p[c] = pd.to_numeric(p[c], errors="coerce").astype("Int64")
    p["ciudad_cod"] = pd.to_numeric(p["ciudad_cod"], errors="coerce").astype("Int64")
    p["factor_expansion"] = pd.to_numeric(p["factor_expansion"], errors="coerce").astype(float)
    p["anio"] = p["anio"].astype("Int64")
    p["mes"] = pd.to_numeric(p["mes"], errors="coerce").astype("Int64")

    # Etiquetas legibles
    p["condicion_actividad_txt"] = p["condicion_actividad"].map(CONDACT)
    p["categoria_pea"] = p["condicion_actividad"].map(CATEGORIA_PEA)  # vacío si no es PEA
    p["sexo"] = p["sexo_cod"].map(SEXO)
    p["area"] = p["area_cod"].map(AREA)
    p["nivel_instruccion"] = p["nivel_instruccion_cod"].map(EDUCACION)
    p["ciudad"] = p["ciudad_cod"].map(CIUDADES)
    p["grupo_edad"] = pd.cut(p["edad"].astype(float), bins=[14, 24, 34, 44, 64, 120],
                             labels=["15-24", "25-34", "35-44", "45-64", "65+"]).astype("string")
    p["trimestre"] = ((p["mes"] - 1) // 3 + 1).astype("Int64")

    # Banderas de población
    p["es_pet"] = p["condicion_actividad"].between(1, 9)
    p["es_pea"] = p["condicion_actividad"].between(1, 8)
    return p


def controles(p: pd.DataFrame, nombre: str) -> None:
    errores = []
    if p["factor_expansion"].isna().any() or (p["factor_expansion"] <= 0).any():
        errores.append("factor de expansión vacío o no positivo")
    if not p["condicion_actividad"].dropna().between(0, 9).all():
        errores.append("códigos de condact fuera de 0-9")
    if p["condicion_actividad"].isna().any():
        errores.append(f"{p['condicion_actividad'].isna().sum()} personas sin condact")
    estado = "OK" if not errores else "REVISAR: " + "; ".join(errores)
    print(f"  Control de calidad {nombre}: {estado}")


def construir(periodicidad: str) -> None:
    archivos = sorted(BRONCE_PARQUET.glob(f"{periodicidad}_*.parquet"))
    if not archivos:
        print(f"(sin bases {periodicidad}es en bronce, se omite)")
        return
    plata = pd.concat([limpiar(pd.read_parquet(a)) for a in archivos], ignore_index=True)
    controles(plata, periodicidad)
    salida = PLATA / f"personas_{periodicidad}.parquet"
    plata.to_parquet(salida, index=False)
    pob = plata.groupby("anio" if periodicidad == "anual" else ["anio", "mes"])["factor_expansion"].sum() / 1e6
    print(f"  {salida.name}: {len(plata):,} personas, {plata.shape[1]} columnas")
    print("  Población representada (millones):")
    print("  " + pob.round(2).to_string().replace("\n", "\n  "))


def main() -> None:
    PLATA.mkdir(parents=True, exist_ok=True)
    print("Mensual:")
    construir("mensual")
    print("\nAnual:")
    construir("anual")


if __name__ == "__main__":
    main()
