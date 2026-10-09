# 04 · Estructura del paquete y empaquetado

[⬅ Anterior: Precisión numérica](03_precision_numerica.md) · [Índice](README.md) · [Siguiente: Pruebas ➡](05_pruebas.md)

## 📑 Contenido

| ID | Severidad | Título | Cierre |
|---|---|---|:---:|
| [E-01](#e-01) | 🟠 Alto | Dos implementaciones divergentes de las funciones de tabla | ✅ 100 % |
| [E-02](#e-02) | 🟠 Alto | `Tables` vs `tables`: mayúsculas distintas en git y en disco | ✅ 100 % |
| [E-03](#e-03) | 🟠 Alto | Dependencias no declaradas | ✅ 100 % |
| [E-04](#e-04) | 🟡 Medio | README desactualizado e inconsistente | ✅ 100 % |
| [E-05](#e-05) | 🔵 Bajo | Tests empaquetados dentro de la librería | ✅ 100 % |
| [E-06](#e-06) | 🔵 Bajo | Sin API pública definida | ✅ 100 % |
| [Estructura propuesta](#estructura-propuesta) | — | Árbol de directorios sugerido |

---

<a id="e-01"></a>
## E-01 · Dos implementaciones divergentes de las funciones de tabla — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟠 Alto | [`mpms_11_1/tables.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/tables.py) y [`Tables/table_*.py`](https://github.com/DeividO12/PyMPMS-11.1/tree/4f1216d/src/api_mpms/Tables/) | ✅ |

### Descripción

Los commits `97d38dd` (*“Unificar el manejo de las tablas en un solo script”*) y `f97be20` (*“Reintroducir funciones de tabla”*) dejaron **ambas** versiones en el repositorio. Tienen los mismos nombres de función pero distinto comportamiento:

| Aspecto | `mpms_11_1/tables.py` | `Tables/table_*.py` |
|---|---|---|
| Redondea las entradas (commit `8014542`) | ✅ | ❌ |
| Funciones | 11 | 11 (una por archivo) |
| Importable | ✅ | ✅ (salvo el generador, ver [F-03](01_errores_funcionales.md#f-03)) |

### Evidencia

| Llamada | `mpms_11_1.tables` | `tables.table_*` |
|---|:---:|:---:|
| `table_6x(api_base=30.04, t_f_obs=80.04, commodity_type='A')` | **0.99107** | **0.99105** |
| `table_6x(api_base=35.06, t_f_obs=150.06, commodity_type='B')` | **0.95783** | **0.95787** |
| `table_53x_54x(den_obs=850.06, t_c_obs=40.03, commodity_type='A')` | **0.97945** | **0.97947** |

### Impacto

Dependiendo de qué módulo importe el usuario, obtiene **CTL distintos** para la misma entrada. Cualquier corrección futura deberá aplicarse dos veces.

### Recomendación

Conservar una sola implementación (la de `mpms_11_1/tables.py`, que incluye el redondeo de entradas) y, si se quiere mantener la ruta `api_mpms.tables.table_6x`, convertir esos archivos en reexportaciones:

```python
# api_mpms/tables/__init__.py
from api_mpms.mpms_11_1.tables import (
    table_6x, table_5x_6x, table_6c_24c, table_24x, table_23x_24x,
    table_54x, table_54c, table_53x_54x, table_60x, table_60c, table_59x_60x,
)
```


<!-- res:E-01 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `26df9a8`, `5b0e53a` | 253 valores de tablas de muestra de la norma (`test_tables_norm.py`). |

Se eliminó `src/api_mpms/Tables/`; `mpms_11_1/tables.py` es la única implementación.

---

<a id="e-02"></a>
## E-02 · `Tables` vs `tables`: mayúsculas distintas en git y en disco — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟠 Alto | `src/api_mpms/Tables/` | ✅ |

### Descripción

| Fuente | Nombre del directorio |
|---|---|
| Índice de git (`git ls-files`) | `src/api_mpms/Tables/` |
| Disco local (Windows) | `src/api_mpms/tables/` |
| `core.ignorecase` | `true` |

En Windows funciona porque el sistema de archivos no distingue mayúsculas. En **Linux** (servidores, contenedores Docker, CI de GitHub) un clon crea `Tables/`, y cualquier `import api_mpms.tables` fallará con `ModuleNotFoundError`.

Además, PEP 8 recomienda nombres de paquete en minúsculas.

### Recomendación

Renombrar en git en dos pasos (necesario con `ignorecase=true`):

```bash
git mv src/api_mpms/Tables src/api_mpms/tables_tmp
git mv src/api_mpms/tables_tmp src/api_mpms/tables
```


<!-- res:E-02 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `26df9a8` | `git ls-files` no contiene rutas con mayúsculas distintas. |

El directorio `Tables`/`tables` ya no existe. La CI corre en Linux para detectar este tipo de problema.

---

<a id="e-03"></a>
## E-03 · Dependencias no declaradas — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟠 Alto | [`pyproject.toml`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/pyproject.toml) | ✅ |

### Descripción

- `generator_tables.py` requiere `numpy` y `pandas`, que **no** están en `[project.dependencies]`. En el entorno de verificación `numpy` no estaba instalado.
- `pytest` (necesario según el README) no figura como dependencia de desarrollo ni estaba instalado.
- La versión `0.1.0` está duplicada en `pyproject.toml` y en [`__init__.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/__init__.py).

### Recomendación

```toml
[project]
dependencies = []
dynamic = ["version"]

[project.optional-dependencies]
tables = ["numpy>=1.24", "pandas>=2.0"]
dev = ["pytest>=8", "pytest-cov", "mypy", "ruff"]

[tool.setuptools.dynamic]
version = { attr = "api_mpms.__version__" }
```


<!-- res:E-03 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `6b68257`, `7809937` | `pip install -e ".[dev,tables]"` en un `.venv` limpio. |

Extras `[tables]` (numpy, pandas) y `[dev]` (pytest, pytest-cov, ruff, mypy); versión dinámica desde `api_mpms.__version__` (0.2.0).

---

<a id="e-04"></a>
## E-04 · README desactualizado e inconsistente — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`README.md`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/README.md) | ✅ |

| Línea | Problema |
|---|---|
| [75](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/README.md?plain=1#L75) | `from mpms_11_1.section_6_2 import …` → la ruta real es `api_mpms.mpms_11_1.section_6_2`. El ejemplo **no funciona**. |
| [33-54](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/README.md?plain=1#L33-L54) | La estructura omite `section_5_1`, `5_4`, `7_1`, `7_2`, `tables.py` y `Tables/`; muestra `tests/test_6_1/` como carpetas. |
| [9-13](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/README.md?plain=1#L9-L13) | El alcance solo lista 5.3, 6.1 y 6.2. |
| [62-63](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/README.md?plain=1#L62-L63) | `pip install pympms-11-1`: el paquete no está publicado; el nombre de distribución (`pympms-11-1`) difiere del de import (`api_mpms`) sin aclararlo. |
| [95](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/README.md?plain=1#L95) | “Each test validates numerical convergence and tolerance” → falso, ver [T-01](05_pruebas.md#t-01). |
| [119](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/README.md?plain=1#L119) | “License to be defined” → el archivo `LICENSE` ya define una licencia propietaria. |


<!-- res:E-04 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `fa840c5` | Los ejemplos del README son casos de la suite (6.2-ej1, 7.2-ej1). |

README reescrito: import real, alcance, unidades, límites, excepciones, política de redondeo, tablas, generador y licencia propietaria. Se añadió `CHANGELOG.md` con la tabla de cambios incompatibles.

---

<a id="e-05"></a>
## E-05 · Tests empaquetados dentro de la librería — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔵 Bajo | [`src/api_mpms/tests/`](https://github.com/DeividO12/PyMPMS-11.1/tree/4f1216d/src/api_mpms/tests/) | — |

`packages.find` incluye `api_mpms.tests` en el *wheel*. Como esos módulos ejecutan `print(...)` a nivel de módulo, cualquier herramienta que importe todos los submódulos (documentación automática, descubrimiento de plugins) ejecutará los cálculos e imprimirá en consola.

**Recomendación:** mover a `tests/` en la raíz del repositorio.


<!-- res:E-05 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `6b68257` | `src/api_mpms` ya no contiene `tests`. |

Pruebas movidas a `tests/` en la raíz; ya no se empaquetan.

---

<a id="e-06"></a>
## E-06 · Sin API pública definida — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔵 Bajo | [`__init__.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/__init__.py) y subpaquetes | — |

- Todos los `__init__.py` están vacíos (salvo `__version__`); el usuario debe conocer la ruta interna de cada función.
- No existe `__all__`, por lo que no está claro qué es API pública y qué es detalle de implementación (`_MAX_ITER`, `DELTA_60`, etc.).
- No hay `py.typed`, así que los *type checkers* ignoran las anotaciones al instalar el paquete.

**Recomendación:**

```python
# api_mpms/__init__.py
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.exceptions.validation import MPMSValidationError
from api_mpms.exceptions.convergence import MPMSConvergenceError

__all__ = [...]
__version__ = "0.1.0"
```

Y añadir un archivo vacío `src/api_mpms/py.typed`.


<!-- res:E-06 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `26df9a8`, `5b0e53a` | `import api_mpms; api_mpms.correct_observed_to_base(...)`. |

`api_mpms/__init__.py` exporta la API pública con `__all__`; se añadió `py.typed` al *package data*.

---

<a id="estructura-propuesta"></a>
## Estructura propuesta

```text
api_mpms/
├── pyproject.toml
├── README.md
├── docs/
├── scripts/
│   └── generate_tables.py        # antes Tables/generator_tables.py
├── src/api_mpms/
│   ├── __init__.py                # API pública + __all__
│   ├── py.typed
│   ├── constants/
│   │   ├── commodity_groups.py    # incluye Da y límites
│   │   └── physical.py            # 999.016, 60 °F, rangos
│   ├── exceptions/
│   ├── validators/
│   ├── mpms_11_1/
│   │   ├── section_5_1.py … section_7_2.py
│   │   └── tables.py              # única implementación
│   └── tables/__init__.py         # reexportaciones (opcional)
└── tests/
    ├── test_section_5_3.py
    ├── test_section_5_4.py
    ├── test_section_6_1.py
    ├── test_section_6_2.py
    └── test_tables.py
```

---

[⬅ Anterior: Precisión numérica](03_precision_numerica.md) · [Índice](README.md) · [Siguiente: Pruebas ➡](05_pruebas.md)
