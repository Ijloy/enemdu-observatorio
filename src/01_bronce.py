"""
CAPA BRONCE – Ingesta.
Lee cada .sav del INEC tal como viene y guarda una copia fiel en Parquet.
No se limpia ni se elimina nada: solo se agregan columnas de trazabilidad
(origen, periodicidad, año y mes).

Entrada:  data/bronce/mensual/AAAA_MM.sav  y  data/bronce/anual/AAAA.sav
Salida:   data/bronce/parquet/mensual_AAAA_MM.parquet / anual_AAAA.parquet

Uso:  python src/01_bronce.py
"""
import pandas as pd
import pyreadstat

from config import BRONCE_ANUAL, BRONCE_MENSUAL, BRONCE_PARQUET


def ingerir(ruta, periodicidad: str, anio: int, mes) -> int:
    nombre = f"{periodicidad}_{ruta.stem}.parquet"
    destino = BRONCE_PARQUET / nombre
    # Ingesta incremental: si el Parquet ya existe y es más nuevo que el .sav, no se repite
    if destino.exists() and destino.stat().st_mtime >= ruta.stat().st_mtime:
        print(f"  {ruta.name:<14} -> {nombre:<28} (ya ingerido, se omite)")
        return 0
    df, _ = pyreadstat.read_sav(ruta, apply_value_formats=False)
    df.columns = [c.lower() for c in df.columns]
    df["periodicidad"] = periodicidad
    df["anio"] = anio
    df["mes"] = mes
    df["archivo_origen"] = ruta.name
    # Columnas de texto mixto como texto, para que Parquet no falle
    for col in df.columns[df.dtypes == "object"]:
        df[col] = df[col].astype("string")
    df.to_parquet(destino, index=False)
    print(f"  {ruta.name:<14} -> {nombre:<28} {len(df):>8,} filas  {df.shape[1]:>4} cols")
    return len(df)


def main() -> None:
    BRONCE_PARQUET.mkdir(parents=True, exist_ok=True)
    mensuales = sorted(BRONCE_MENSUAL.glob("????_??.sav"))
    anuales = sorted(BRONCE_ANUAL.glob("????.sav"))
    if not mensuales and not anuales:
        raise SystemExit("No hay archivos .sav en data/bronce/mensual ni data/bronce/anual")

    total = 0
    print("Bases mensuales:")
    for r in mensuales:
        anio, mes = r.stem.split("_")
        total += ingerir(r, "mensual", int(anio), int(mes))
    print("Bases anuales:")
    for r in anuales:
        total += ingerir(r, "anual", int(r.stem), pd.NA)
    print(f"\nBronce listo: {len(mensuales) + len(anuales)} archivos, {total:,} filas en total")


if __name__ == "__main__":
    main()
