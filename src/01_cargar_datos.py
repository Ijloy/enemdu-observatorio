"""
Paso 2: lee las 12 bases mensuales de personas de la ENEMDU 2025 (.sav),
les agrega la columna `mes` y las une en un solo archivo Parquet.

Uso (desde la carpeta del proyecto):
    python src/01_cargar_datos.py
"""
from pathlib import Path

import pandas as pd
import pyreadstat

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw"
SALIDA = RAIZ / "data" / "processed" / "enemdu_personas_2025.parquet"


def leer_mes(ruta: Path) -> pd.DataFrame:
    df, meta = pyreadstat.read_sav(ruta, apply_value_formats=False)
    df.columns = [c.lower() for c in df.columns]
    df["mes"] = int(ruta.stem.split("_")[1])  # 2025_07 -> 7
    return df


def main() -> None:
    archivos = sorted(RAW.glob("2025_*.sav"))
    if not archivos:
        raise SystemExit(f"No encontré archivos 2025_*.sav en {RAW}")

    partes = []
    for ruta in archivos:
        df = leer_mes(ruta)
        print(f"{ruta.name}: {len(df):>7,} personas, {df.shape[1]} columnas")
        partes.append(df)

    # Algunas columnas pueden no estar en todos los meses: avisamos
    comunes = set.intersection(*(set(p.columns) for p in partes))
    todas = set.union(*(set(p.columns) for p in partes))
    if todas - comunes:
        print(f"\nOjo: {len(todas - comunes)} columnas no aparecen en todos los meses:")
        print(sorted(todas - comunes))

    base = pd.concat(partes, ignore_index=True)
    # Las columnas de texto mixto se guardan como texto para que Parquet no falle
    for col in base.columns[base.dtypes == "object"]:
        base[col] = base[col].astype("string")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    base.to_parquet(SALIDA, index=False)

    print(f"\nTotal: {len(base):,} filas y {base.shape[1]} columnas")
    print(f"Guardado en: {SALIDA}")
    print(f"Población representada por mes (suma de fexp, en millones):")
    print((base.groupby("mes")["fexp"].sum() / 1e6).round(2).to_string())


if __name__ == "__main__":
    main()
