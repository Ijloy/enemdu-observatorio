"""
Configuración compartida del proyecto: rutas de la arquitectura medallón y
códigos/etiquetas del INEC que usan todos los scripts.

Arquitectura medallón:
  BRONCE -> datos crudos tal como los entrega el INEC (+ copia en Parquet sin cambios)
  PLATA  -> datos limpios a nivel de persona: variables seleccionadas, tipos y etiquetas
  ORO    -> tablas agregadas listas para el negocio (indicadores, composición, validación)
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"

BRONCE = DATA / "bronce"
BRONCE_MENSUAL = BRONCE / "mensual"       # 2025_01.sav ... 2025_12.sav
BRONCE_ANUAL = BRONCE / "anual"           # 2021.sav ... 2025.sav (base anual del INEC)
BRONCE_PARQUET = BRONCE / "parquet"       # copia fiel en Parquet

PLATA = DATA / "plata"
ORO = DATA / "oro"
TABLEAU = DATA / "tableau"

# Variables que pasan de bronce a plata (nombres homologados del INEC)
VARIABLES = ["condact", "fexp", "area", "p02", "p03", "nnivins", "ciudad"]

# Condición de actividad (condact)
CONDACT = {
    0: "Menor de 15 años",
    1: "Empleo adecuado",
    2: "Subempleo por insuficiencia de tiempo",
    3: "Subempleo por insuficiencia de ingresos",
    4: "Otro empleo no pleno",
    5: "Empleo no remunerado",
    6: "Empleo no clasificado",
    7: "Desempleo abierto",
    8: "Desempleo oculto",
    9: "Población económicamente inactiva",
}
# Categorías agregadas que suman el 100 % de la PEA (para el gráfico de pastel)
CATEGORIA_PEA = {
    1: "Empleo adecuado",
    2: "Subempleo", 3: "Subempleo",
    4: "Otro empleo no pleno",
    5: "Empleo no remunerado",
    6: "Empleo no clasificado",
    7: "Desempleo", 8: "Desempleo",
}

SEXO = {1: "Hombre", 2: "Mujer"}
AREA = {1: "Urbana", 2: "Rural"}
EDUCACION = {1: "Ninguno", 2: "Centro de alfabetización", 3: "Educación básica",
             4: "Bachillerato", 5: "Superior"}
CIUDADES = {170150: "Quito", 90150: "Guayaquil", 10150: "Cuenca",
            70150: "Machala", 180150: "Ambato"}
