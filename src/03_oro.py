"""
CAPA ORO – Tablas de negocio.
A partir de la capa plata calcula los indicadores laborales ponderados
(siempre con el factor de expansión) y deja tablas listas para el dashboard.

Definiciones INEC:
  PET = 15 años y más (condact 1-9)      PEA = con empleo o desempleo (condact 1-8)
  Tasas de empleo/subempleo/desempleo sobre la PEA; participación global = PEA / PET

Salidas en data/oro/:
  indicadores_anuales.csv        nacional, área y sexo por año (base anual INEC)
  composicion_pea_anual.csv      reparto de la PEA nacional por categoría (suma 100 %)
  indicadores_mensuales_2025.csv mensual 2025 por grupos
  ciudades_trimestral_2025.csv   5 ciudades por trimestre 2025

Uso:  python src/03_oro.py
"""
import numpy as np
import pandas as pd

from config import ORO, PLATA


def pesos(p: pd.DataFrame) -> pd.DataFrame:
    """Agrega columnas de peso: cada persona aporta su factor de expansión."""
    p = p[p["es_pet"]].copy()
    c, w = p["condicion_actividad"], p["factor_expansion"]
    p["w_pet"] = w
    p["w_pea"] = np.where(p["es_pea"], w, 0)
    p["w_adecuado"] = np.where(c == 1, w, 0)
    p["w_subempleo"] = np.where(c.isin([2, 3]), w, 0)
    p["w_otro_no_pleno"] = np.where(c == 4, w, 0)
    p["w_no_remunerado"] = np.where(c == 5, w, 0)
    p["w_desempleo"] = np.where(c.isin([7, 8]), w, 0)
    p["nacional"] = "Nacional"
    return p


def tasas(p: pd.DataFrame, periodo: list, columna: str, dimension: str, n_periodos: int = 1) -> pd.DataFrame:
    w = [c for c in p.columns if c.startswith("w_")]
    g = (p.dropna(subset=[columna]).groupby(periodo + [columna], observed=True)[w].sum()
           .reset_index().rename(columns={columna: "grupo"}))
    out = g[periodo].copy()
    out["dimension"] = dimension
    out["grupo"] = g["grupo"].astype(str)
    out["pet"] = (g["w_pet"] / n_periodos).round(0)
    out["pea"] = (g["w_pea"] / n_periodos).round(0)
    out["tpg"] = (100 * g["w_pea"] / g["w_pet"]).round(4)
    for k in ["adecuado", "subempleo", "otro_no_pleno", "no_remunerado", "desempleo"]:
        out[f"tasa_{k}"] = (100 * g[f"w_{k}"] / g["w_pea"]).round(4)
    return out


def oro_anual() -> None:
    ruta = PLATA / "personas_anual.parquet"
    if not ruta.exists():
        print("(sin capa plata anual: descarga las bases anuales del INEC)")
        return
    p = pesos(pd.read_parquet(ruta))

    ind = pd.concat([tasas(p, ["anio"], "nacional", "Nacional"),
                     tasas(p, ["anio"], "area", "Área"),
                     tasas(p, ["anio"], "sexo", "Sexo")], ignore_index=True)
    ind.to_csv(ORO / "indicadores_anuales.csv", index=False, encoding="utf-8")

    pea = p[p["es_pea"]]
    comp = pea.groupby(["anio", "categoria_pea"])["factor_expansion"].sum().reset_index(name="personas")
    comp["porcentaje"] = (100 * comp["personas"] / comp.groupby("anio")["personas"].transform("sum")).round(4)
    comp["personas"] = comp["personas"].round(0)
    comp.to_csv(ORO / "composicion_pea_anual.csv", index=False, encoding="utf-8")

    cols = ["anio", "tpg", "tasa_adecuado", "tasa_subempleo", "tasa_desempleo"]
    print("NACIONAL por año (%):")
    print(ind[ind["dimension"] == "Nacional"][cols].round(1).to_string(index=False))
    ultimo = comp["anio"].max()
    print(f"\nComposición de la PEA nacional {ultimo} (%):")
    print(comp[comp["anio"] == ultimo][["categoria_pea", "porcentaje"]].round(1).to_string(index=False))


def oro_mensual() -> None:
    ruta = PLATA / "personas_mensual.parquet"
    if not ruta.exists():
        print("(sin capa plata mensual)")
        return
    p = pesos(pd.read_parquet(ruta))
    p = p[p["anio"] == 2025]

    ind = pd.concat([tasas(p, ["mes"], c, d) for c, d in
                     [("nacional", "Nacional"), ("area", "Área"), ("sexo", "Sexo"),
                      ("grupo_edad", "Edad"), ("nivel_instruccion", "Educación"),
                      ("ciudad", "Ciudad")]], ignore_index=True)
    ind.to_csv(ORO / "indicadores_mensuales_2025.csv", index=False, encoding="utf-8")

    # Las cifras por ciudad del INEC son trimestrales: se juntan 3 meses de muestra
    trim = tasas(p, ["trimestre"], "ciudad", "Ciudad", n_periodos=3)
    trim.to_csv(ORO / "ciudades_trimestral_2025.csv", index=False, encoding="utf-8")

    print("\nCIUDADES por trimestre 2025 (%):")
    print(trim[["trimestre", "grupo", "tasa_adecuado", "tasa_desempleo"]].round(1).to_string(index=False))


def main() -> None:
    ORO.mkdir(parents=True, exist_ok=True)
    oro_anual()
    oro_mensual()
    print(f"\nCapa oro lista en {ORO}")


if __name__ == "__main__":
    main()
