# 10 · Generador de tablas

[⬅ Anterior: Límites y unidades](09_limites.md) · [Índice](README.md)

`scripts/generate_tables.py` genera las 28 tablas de temperatura de API MPMS 11.1.8 como archivos CSV, con los rangos e incrementos de la norma. Úselo cuando necesite la tabla completa (para cargarla en otro sistema o publicarla). Para valores puntuales use [`api_mpms.tables`](05_ref_tablas.md).

## 📑 Contenido

1. [Requisitos](#requisitos)
2. [Uso](#uso)
3. [Tablas disponibles](#disponibles)
4. [Formato del CSV](#formato)
5. [Leer el CSV](#leer)
6. [Tiempos](#tiempos)

---

<a id="requisitos"></a>
## 1. Requisitos

```bash
pip install ".[tables]"      # numpy y pandas
```

Se ejecuta desde la raíz del repositorio; no forma parte del paquete instalado.

---

<a id="uso"></a>
## 2. Uso

```bash
python scripts/generate_tables.py --list                         # tablas disponibles y tamaño
python scripts/generate_tables.py 6A                             # una tabla, en ./tablas
python scripts/generate_tables.py 5A 6A 54B --out-dir salida     # varias, en otra carpeta
python scripts/generate_tables.py 60C --workers 4                # limitar procesos en paralelo
```

| Opción | Por defecto | Descripción |
|---|---|---|
| `tablas…` | — | Nombres de tabla (no distingue mayúsculas): `5A`, `6B`, `23D`, `54C`… |
| `--out-dir` | `tablas` | Carpeta de salida (se crea si no existe). Los archivos existentes se sobrescriben. |
| `--workers` | núcleos del equipo | Procesos en paralelo; `1` para ejecución secuencial. |
| `--list` | — | Muestra las tablas y su tamaño (columnas × temperaturas). |

---

<a id="disponibles"></a>
## 3. Tablas disponibles

| Tablas | Contenido de la celda | Función equivalente |
|---|---|---|
| 5A, 5B, 5D | °API a 60 °F | [`table_5x`](05_ref_tablas.md#table_5x) |
| 6A, 6B, 6D | CTL | [`table_6x`](05_ref_tablas.md#table_6x) |
| 23A, 23B, 23D | Densidad relativa 60/60 °F | [`table_23x`](05_ref_tablas.md#table_23x) |
| 24A, 24B, 24D | CTL | [`table_24x`](05_ref_tablas.md#table_24x) |
| 53A, 53B, 53D | Densidad a 15 °C (kg/m³) | [`table_53x`](05_ref_tablas.md#table_53x) |
| 54A, 54B, 54D | CTL | [`table_54x`](05_ref_tablas.md#table_54x) |
| 59A, 59B, 59D | Densidad a 20 °C (kg/m³) | [`table_59x`](05_ref_tablas.md#table_59x) |
| 60A, 60B, 60D | CTL | [`table_60x`](05_ref_tablas.md#table_60x) |
| 6C, 24C | CTL | [`table_6c_24c`](05_ref_tablas.md#table_6c_24c) |
| 54C, 60C | CTL | [`table_54c`](05_ref_tablas.md#table_54c), [`table_60c`](05_ref_tablas.md#table_60c) |

Rangos e incrementos: [09 · Límites › Rangos de las tablas](09_limites.md#tablas).

---

<a id="formato"></a>
## 4. Formato del CSV

Igual que las tablas impresas de la norma: **temperatura en filas** y densidad (o °API, densidad relativa, α) en columnas.

```text
# If hydrometer used to determine density, apply glass correction before entering table
t_f_obs,-14.1,-14.0,-13.9,…
-58.0,-10.0,-9.9,-9.8,…
-57.9,…
```

| Elemento | Detalle |
|---|---|
| Archivo | `Tabla_<nombre>.csv` (por ejemplo `Tabla_6A.csv`), UTF-8 |
| Primera línea | Solo en las tablas de densidad observada (5, 23, 53, 59): nota de la norma sobre la corrección del hidrómetro, precedida de `#` |
| Encabezado | Nombre de la columna índice (`t_f_obs` o `t_c_obs`) seguido de los valores de entrada de cada columna |
| Celdas | Valor redondeado según la tabla (CTL a 5 decimales, °API a 1, densidad relativa a 4, kg/m³ a 1) |
| Celda vacía | La combinación está fuera de los límites de la norma. **Nunca** se escribe 0. |

---

<a id="leer"></a>
## 5. Leer el CSV

```python
import pandas as pd

tabla = pd.read_csv("tablas/Tabla_6A.csv", comment="#", index_col=0)
ctl = tabla.loc[120.0, "95.0"]        # fila: temperatura; columna: °API a 60 °F (texto)
# ctl == 0.94671  (valor impreso en la norma, tabla 6A, pág. PDF 148)
```

> [!TIP]
> Use `comment="#"` para saltar la nota del hidrómetro. Las celdas vacías se leen como `NaN`.

---

<a id="tiempos"></a>
## 6. Tiempos

Cada tabla tiene entre 2 y 29 millones de celdas. Como referencia, la tabla 5D (805 × 3 601 celdas) tarda unos 30 s con 16 procesos. Las tablas más grandes (23, 53, 59) pueden tardar varios minutos.

---

[⬅ Anterior: Límites y unidades](09_limites.md) · [Índice](README.md)
