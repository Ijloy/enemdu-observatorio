"""
Paso 3a: revisa en el diccionario interno del .sav (metadatos) qué significan
las variables clave y sus códigos, antes de calcular indicadores.

Uso:
    python src/02_explorar_variables.py
"""
from pathlib import Path

import pandas as pd
import pyreadstat

RAIZ = Path(__file__).resolve().parent.parent
SAV = RAIZ / "data" / "raw" / "2025_12.sav"
PARQUET = RAIZ / "data" / "processed" / "enemdu_personas_2025.parquet"

# Variables que esperamos usar (nombres homologados del INEC)
CLAVE = ["condact", "empleo", "desempleo", "pea", "ciudad", "area", "dominio",
         "prov", "p02", "p03", "nnivins", "fexp"]
# Palabras para buscar otras variables útiles por su etiqueta
BUSCAR = ["condición de actividad", "condicion de actividad", "ciudad", "sexo",
          "edad", "nivel de instrucción", "nivel de instruccion", "área", "area"]

_, meta = pyreadstat.read_sav(SAV, metadataonly=True)
etiquetas = {k.lower(): v for k, v in meta.column_names_to_labels.items()}
valores = {k.lower(): v for k, v in meta.variable_to_label.items()}
codigos = {k: v for k, v in meta.value_labels.items()}


def mostrar(var: str) -> None:
    print(f"\n=== {var}: {etiquetas.get(var)}")
    nombre_set = valores.get(var)
    if nombre_set:
        for cod, txt in list(codigos[nombre_set].items())[:30]:
            print(f"   {cod:>6} = {txt}")


print("VARIABLES CLAVE")
for v in CLAVE:
    if v in etiquetas:
        mostrar(v)
    else:
        print(f"\n=== {v}: NO EXISTE en la base")

print("\n\nOTRAS VARIABLES CANDIDATAS (por etiqueta)")
for var, lab in etiquetas.items():
    if lab and any(b in lab.lower() for b in BUSCAR) and var not in CLAVE:
        print(f"   {var:<12} {lab}")

# Distribución ponderada de condact en diciembre, para una primera mirada
df = pd.read_parquet(PARQUET, columns=["mes", "condact", "fexp"])
dic = df[df["mes"] == 12]
dist = dic.groupby("condact")["fexp"].sum() / 1e6
print("\n\nDiciembre 2025, personas por condact (millones, ponderado):")
print(dist.round(3).to_string())
