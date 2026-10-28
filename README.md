# Observatorio del Mercado Laboral – Ecuador 2025

Análisis del mercado laboral ecuatoriano con los **microdatos de la ENEMDU 2025** (INEC):
procesamiento y ponderación en **Python**, validación contra cifras oficiales y
visualización en **Tableau Public**.

👉 **Dashboard interactivo:** [Mercado laboral en Ecuador 2025: el caso de Quito](https://public.tableau.com/views/MercadolaboralEcuador2025elcasodeQuito/ObservatorioLaboral)

## Pregunta

¿Cómo evolucionó el empleo en Ecuador durante 2025 y cómo se compara Quito con las
otras ciudades principales?

## Hallazgos

- A nivel nacional, el **empleo adecuado** subió de 34,0 % (enero) a 37,1 % (diciembre),
  y el **desempleo** cerró el año en 2,6 %.
- **Quito tuvo el desempleo más alto de las 5 ciudades principales** en los cuatro
  trimestres de 2025 (entre 6,7 % y 7,8 %).
- Aun así, **más de la mitad de su PEA tiene empleo adecuado** (54 %–57 %), solo por
  detrás de Cuenca. En Quito cuesta más conseguir trabajo, pero el que se consigue
  suele ser de mejor calidad.

## Datos

- **Fuente:** Encuesta Nacional de Empleo, Desempleo y Subempleo (ENEMDU), INEC –
  bases mensuales de personas, enero a diciembre 2025 (334.786 registros).
- Descarga: [ecuadorencifras.gob.ec](https://www.ecuadorencifras.gob.ec/estadisticas-laborales-enemdu/)
- Los microdatos (`.sav`) no se incluyen en el repositorio por su tamaño; se guardan en
  `data/raw/` con el nombre `2025_MM.sav`.

## Método

Todos los indicadores se ponderan con el factor de expansión `fexp` y se construyen a
partir de la variable `condact` (condición de actividad), siguiendo la definición del INEC:

| Indicador | Definición |
|---|---|
| PET | Población de 15 años y más (`condact` 1–9) |
| PEA | Población con empleo o desempleo (`condact` 1–8) |
| Tasa de participación global | PEA / PET |
| Empleo adecuado | `condact` = 1, sobre la PEA |
| Subempleo | `condact` 2–3, sobre la PEA |
| Desempleo | `condact` 7–8, sobre la PEA |

Las cifras por ciudad se calculan **por trimestre** (juntando 3 bases mensuales), igual
que las publica el INEC, porque la muestra mensual por ciudad es pequeña.

## Validación contra el INEC

| Nivel | Comparación | Diferencia máxima |
|---|---|---|
| Nacional (mayo y diciembre 2025) | 7 indicadores | **0,0 puntos** |
| Quito (T1 2025) | 3 indicadores | 0,5 puntos |

La pequeña diferencia en Quito se debe a que el INEC usa su base trimestral, con su
propio factor de expansión, mientras que aquí se juntan las tres bases mensuales.
El detalle está en `data/processed/validacion_inec.csv`.

## Estructura

```
├── src/
│   ├── 01_cargar_datos.py        # lee los 12 .sav y los une en un Parquet
│   ├── 02_explorar_variables.py  # revisa etiquetas y códigos de las variables
│   ├── 03_indicadores.py         # calcula indicadores mensuales y trimestrales
│   ├── 04_validacion.py          # compara contra cifras oficiales del INEC
│   └── 05_exportar_tableau.py    # prepara los CSV para Tableau
├── data/
│   ├── raw/                      # microdatos INEC (no incluidos)
│   ├── processed/                # indicadores calculados
│   └── tableau/                  # CSV listos para el dashboard
└── requirements.txt
```

## Cómo reproducirlo

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

python src/01_cargar_datos.py
python src/03_indicadores.py
python src/04_validacion.py
python src/05_exportar_tableau.py
```

## Autor

**Dereck Proaño** – Estudiante de Ingeniería de Software, Universidad de las Américas (Quito)
GitHub: [@Ijloy](https://github.com/Ijloy)
