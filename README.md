# Observatorio del Mercado Laboral – Ecuador 2021–2025

Análisis del mercado laboral ecuatoriano con los **microdatos de la ENEMDU** (INEC):
pipeline en **Python** con **arquitectura medallón** (bronce → plata → oro),
validación contra cifras oficiales y visualización en **Tableau Public**.

👉 **Dashboard interactivo:** [Mercado laboral en Ecuador: el caso de Quito](https://public.tableau.com/views/MercadolaboralEcuador2025elcasodeQuito/ObservatorioLaboral)

## Preguntas

1. ¿Cómo evolucionó el empleo en Ecuador entre 2021 y 2025?
2. ¿Cómo se reparte la población económicamente activa (PEA) entre empleo adecuado,
   subempleo, otras formas de empleo y desempleo?
3. ¿Cómo se compara Quito con las otras ciudades principales?

## Hallazgos

- **Recuperación sostenida:** el **empleo adecuado** subió de 32,5 % (2021) a 37,1 % (2025)
  y el **desempleo** bajó de 5,2 % a 3,6 %.

  | Año | Participación | Empleo adecuado | Subempleo | Desempleo |
  |---|---|---|---|---|
  | 2021 | 66,0 % | 32,5 % | 23,2 % | 5,2 % |
  | 2022 | 65,9 % | 34,4 % | 22,2 % | 4,4 % |
  | 2023 | 64,7 % | 36,3 % | 19,6 % | 3,8 % |
  | 2024 | 64,3 % | 35,9 % | 21,0 % | 3,7 % |
  | 2025 | 64,3 % | 37,1 % | 19,4 % | 3,6 % |

- **Aun así, solo 37 de cada 100 personas de la PEA tienen empleo adecuado.** En 2025 la PEA se
  reparte en: empleo adecuado 37,1 %, otro empleo no pleno 30,8 %, subempleo 19,4 %,
  empleo no remunerado 8,8 %, desempleo 3,6 % y no clasificado 0,2 %.
- **Quito tuvo el desempleo más alto de las 5 ciudades principales** en los cuatro
  trimestres de 2025 (entre 6,7 % y 7,8 %), aunque más de la mitad de su PEA tiene
  empleo adecuado (54 %–57 %), solo por detrás de Cuenca.

## Datos

- **Fuente:** Encuesta Nacional de Empleo, Desempleo y Subempleo (ENEMDU), INEC.
  - **Bases anuales 2021–2025** (base de personas): para la comparación por año y la composición de la PEA.
  - **Bases mensuales enero–diciembre 2025:** para el detalle mensual y por ciudad.
- Descarga: [ENEMDU mensual](https://www.ecuadorencifras.gob.ec/estadisticas-laborales-enemdu/) ·
  [ENEMDU anual](https://www.ecuadorencifras.gob.ec/enemdu-anual/)
- Los microdatos (`.sav`, ~700 MB) no se incluyen en el repositorio; se colocan en
  `data/bronce/` como se indica abajo.

## Arquitectura medallón

La arquitectura medallón organiza los datos en tres capas, como las medallas: **bronce, plata
y oro**. Cada capa lee solo de la anterior y deja los datos más limpios y más cerca de la
pregunta que se quiere responder. La ventaja es que cada etapa tiene una sola responsabilidad:
si cambia una definición, se vuelve a correr desde esa capa sin descargar ni releer los
microdatos, y cualquier cifra del dashboard se puede rastrear hasta el archivo original del INEC.

```mermaid
flowchart LR
    A["Microdatos INEC<br/>.sav"] --> B["🥉 Bronce<br/>copia fiel en Parquet"]
    B --> C["🥈 Plata<br/>personas limpias"]
    C --> D["🥇 Oro<br/>indicadores agregados"]
    D --> E["CSV para Tableau"]
    E --> F["Dashboard"]
```

| Capa | Pregunta que responde | Granularidad | Volumen actual | ¿En el repo? |
|---|---|---|---|---|
| 🥉 **Bronce** | ¿Qué entregó exactamente el INEC? | La original de cada base | 17 bases, 2 076 026 filas | No |
| 🥈 **Plata** | ¿Quién es cada persona, con datos limpios? | Una fila por persona | 2 076 026 personas, 21 columnas | No |
| 🥇 **Oro** | ¿Cuáles son los indicadores? | Agregada por periodo y grupo | 5 tablas CSV | Sí |

### 🥉 Bronce: los datos tal como llegan

`src/01_bronce.py` lee cada `.sav` y guarda una copia en Parquet **sin limpiar ni eliminar nada**.
Solo agrega columnas de trazabilidad (`periodicidad`, `anio`, `mes`, `archivo_origen`).
La ingesta es incremental: omite los archivos cuyo Parquet ya está al día. Así, si una capa
posterior tiene un error, el dato original sigue intacto y no hace falta volver a leer los `.sav`.

### 🥈 Plata: los datos limpios y entendibles

`src/02_plata.py` conserva las variables necesarias y las deja listas para analizar:

- **Nombres claros:** `p02` pasa a `sexo_cod`, `p03` a `edad` y `fexp` a `factor_expansion`.
- **Tipos correctos:** enteros y decimales en lugar de valores mixtos.
- **Etiquetas legibles:** sexo, área, ciudad, nivel de instrucción, grupo de edad y categoría de la PEA.
- **Banderas de población:** `es_pet` y `es_pea`.
- **Controles de calidad:** informa si hay factores de expansión vacíos o no positivos y códigos
  `condact` faltantes o fuera de rango.

Las bases anuales y mensuales se guardan en archivos separados porque cada una tiene su propio
factor de expansión y mezclarlas duplicaría a la población.

### 🥇 Oro: las respuestas listas para usar

`src/03_oro.py` y `src/04_validacion.py` ponderan los datos de plata con el factor de expansión y
generan las tablas finales:

| Tabla en `data/oro/` | Contenido |
|---|---|
| `indicadores_anuales.csv` | Nacional, área y sexo por año, 2021–2025 |
| `composicion_pea_anual.csv` | Reparto de la PEA por categoría (suma 100 %) |
| `indicadores_mensuales_2025.csv` | Mensual 2025 por área, sexo, edad, educación y ciudad |
| `ciudades_trimestral_2025.csv` | Las 5 ciudades principales por trimestre |
| `validacion_inec.csv` | Cálculo propio frente a la cifra oficial del INEC |

Después, `src/05_exportar_tableau.py` copia estas tablas a `data/tableau/` con nombres claros y
redondeadas a 1 decimal. Las rutas y los códigos del INEC están centralizados en `src/config.py`.

### Ejemplo: el recorrido de un dato

Una persona con subempleo por insuficiencia de tiempo pasa por las capas así:

1. **Bronce:** aparece con el código original, `condact = 2`.
2. **Plata:** recibe la etiqueta `Subempleo por insuficiencia de tiempo`, la categoría `Subempleo`
   y la bandera `es_pea = True`.
3. **Oro:** su factor de expansión se suma a la tasa de subempleo de su año, que en 2025 fue de 19,4 %.

## Método

Todos los indicadores se ponderan con el factor de expansión (`fexp`) y se construyen a
partir de la condición de actividad (`condact`), según la definición del INEC:

| Indicador | Definición |
|---|---|
| PET | Población de 15 años y más (`condact` 1–9) |
| PEA | Población con empleo o desempleo (`condact` 1–8) |
| Tasa de participación global | PEA / PET |
| Empleo adecuado | `condact` = 1, sobre la PEA |
| Subempleo | `condact` 2–3, sobre la PEA |
| Desempleo | `condact` 7–8, sobre la PEA |

- La **serie anual** usa la base anual del INEC, que tiene un factor de expansión
  recalibrado para el año. Promediar los 12 meses daría cifras distintas a las oficiales
  (por ejemplo, 36,0 % de empleo adecuado en 2025 en lugar de 37,1 %).
- Las cifras **por ciudad** se calculan por trimestre, igual que las publica el INEC,
  porque la muestra mensual por ciudad es pequeña.
- Las tasas se guardan con 4 decimales en la capa oro y se redondean **una sola vez**
  al exportar, para evitar errores de doble redondeo.

## Validación contra el INEC

| Nivel | Comparación | Diferencia máxima |
|---|---|---|
| Nacional anual 2021–2025 | 20 indicadores | **0,0 puntos** |
| Nacional mensual (mayo y diciembre 2025) | 4 indicadores | **0,0 puntos** |
| Quito (T1 2025) | 3 indicadores | 0,5 puntos |

La diferencia en Quito se debe a que el INEC usa su base trimestral, con su propio factor
de expansión, mientras que aquí se juntan las tres bases mensuales.
El detalle está en `data/oro/validacion_inec.csv`.

## Estructura

```
├── src/
│   ├── config.py                 # rutas de las capas y códigos del INEC
│   ├── 01_bronce.py              # ingesta: .sav -> Parquet sin modificar
│   ├── 02_plata.py               # limpieza, tipos, etiquetas y controles de calidad
│   ├── 03_oro.py                 # indicadores y composición de la PEA
│   ├── 04_validacion.py          # comparación contra cifras oficiales del INEC
│   ├── 05_exportar_tableau.py    # CSV para Tableau
│   └── utils/explorar_variables.py
├── data/
│   ├── bronce/                   # microdatos INEC (no incluidos en el repo)
│   │   ├── anual/                #   2021.sav … 2025.sav
│   │   ├── mensual/              #   2025_01.sav … 2025_12.sav
│   │   └── parquet/              #   copia fiel generada por 01_bronce.py
│   ├── plata/                    # personas limpias en Parquet (no incluido)
│   ├── oro/                      # tablas de negocio (CSV)
│   └── tableau/                  # CSV que consume el dashboard
└── requirements.txt
```

## Cómo reproducirlo

1. Descarga las bases de personas del INEC y guárdalas en `data/bronce/anual/AAAA.sav`
   y `data/bronce/mensual/AAAA_MM.sav`.
2. Ejecuta el pipeline:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

python src/01_bronce.py
python src/02_plata.py
python src/03_oro.py
python src/04_validacion.py
python src/05_exportar_tableau.py
```

## Autor

**Dereck Proaño** – Estudiante de Ingeniería de Software, Universidad de las Américas (Quito)
GitHub: [@Ijloy](https://github.com/Ijloy)
