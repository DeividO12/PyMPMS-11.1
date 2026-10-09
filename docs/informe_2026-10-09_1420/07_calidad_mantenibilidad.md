# 07 · Calidad de código y mantenibilidad

[⬅ Anterior: Rendimiento](06_rendimiento.md) · [Índice](README.md) · [Siguiente: Anexo de evidencias ➡](08_anexo_evidencias.md)

## 📑 Contenido

| ID | Severidad | Título | Cierre |
|---|---|---|:---:|
| [C-01](#c-01) | 🔵 Bajo | Variables e imports sin uso | ✅ 100 % |
| [C-02](#c-02) | 🔵 Bajo | Retornos como tuplas posicionales | ✅ 100 % |
| [C-03](#c-03) | 🔵 Bajo | Nombres inconsistentes y errores tipográficos | 🟡 80 % |
| [C-04](#c-04) | 🔵 Bajo | Docstrings y cabeceras incorrectas | ✅ 100 % |
| [C-05](#c-05) | — | Uso de `print` en lugar de `logging` | ✅ 100 % |
| [C-06](#c-06) | — | Rutas de salida fijas | ✅ 100 % |
| [Herramientas](#herramientas-recomendadas) | — | Linters y *type checkers* sugeridos |

---

<a id="c-01"></a>
## C-01 · Variables e imports sin uso — ✅ 100 %

| Archivo | Línea | Elemento |
|---|---|---|
| [`section_6_2.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L34) | 34 | `section_6_2 = False` (nunca se usa) |
| [`section_6_2.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L59) | 59 | Variable de bucle `m` sin uso (usar `_`) |
| [`section_6_1.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py#L7) | 7 | `COMMODITY_GROUPS` importado y no usado |
| [`section_7_1.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_1.py#L29) | 29 | `rho`, `alpha_60_a` calculados y descartados |
| [`section_7_2.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_2.py#L28-L29) | 28-29 | `CTPL_o`, `fp_60`, `CPL_60`, `CTPL_60`, `alpha_60` sin uso |
| [`tables.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/tables.py#L2) | 2 | Imports usados solo en parte de las funciones (correcto, pero conviene revisarlo tras la unificación de [E-01](04_estructura_empaquetado.md#e-01)) |
| [`generator_tables.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L7-L10) | 7, 10 | `math`, `Optional`, `Tuple` sin uso |
| [`section_5_4.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_5_4.py#L1-L3) | 1-3 | `import math` antes del docstring del módulo → el texto deja de ser el `__doc__` del módulo |


<!-- res:C-01 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `5b0e53a` | `ruff check src tests scripts`. |

Se eliminaron las variables e imports sin uso; `ruff` (reglas F, E, W, B) pasa sin errores.

---

<a id="c-02"></a>
## C-02 · Retornos como tuplas posicionales — ✅ 100 %

Las funciones principales devuelven tuplas de 5 o 6 `float` sin nombre. El orden varía entre funciones:

| Función | Orden devuelto |
|---|---|
| `correct_base_to_alternate` | `rho, CTL, Fp, CPL, CTPL, alpha_60` |
| `correct_observed_to_base` | `rho_60, CTL, Fp, CPL, CTPL` |
| `correct_observed_to_alternate_C` | `rho_60, CTL, Fp_psi, CPL, CTPL` |
| `correct_observed_to_base_C` | `rho, rho_60, CTL, Fp_psi, CPL, CTPL` |

En `correct_observed_to_base_C` la **segunda** posición es `rho_60`, mientras que en las demás es `CTL`. Un desempaquetado copiado de otra función asigna valores equivocados sin error.

**Recomendación:**

```python
from typing import NamedTuple

class CorrectionResult(NamedTuple):
    rho: float
    ctl: float
    fp: float
    cpl: float
    ctpl: float
    alpha_60: float | None = None
```

`NamedTuple` sigue siendo desempaquetable (compatibilidad hacia atrás) pero permite `res.ctl`.


<!-- res:C-02 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `5b0e53a` | `test_results_are_named`. |

Todos los procedimientos devuelven `NamedTuple` con nombres en minúscula (`rho`, `ctl`, `fp`, `cpl`, `ctpl`, `ctpl_rounded`…).

---

<a id="c-03"></a>
## C-03 · Nombres inconsistentes y errores tipográficos — 🟡 80 %

| Problema | Ejemplos |
|---|---|
| Parámetro con error tipográfico | `alpa_obs` en [`table_54c`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/tables.py#L148) y [`table_60c`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/tables.py#L213) (vs. `alpha_obs` en `table_6c_24c`) |
| Mismo concepto, distinto nombre | `commodity_group` (6.1) / `commodity_type` (6.2, 7.x) |
| Mismo concepto, distinto nombre | `rho_60`, `rho_o`, `rho_t`, `den_base`, `den_obs`, `api_base`, `rel_base` |
| Temperatura base tipada como `int` | `t_b: Optional[int] = 20` en 7.1/7.2 (acepta `float` y no admite `None`) |
| Variables locales en mayúsculas | `CTL`, `CPL`, `CTPL`, `A`, `B`, `K0`… (PEP 8 reserva mayúsculas para constantes) |
| Mayúsculas en nombre de función | `rho_to_API`, `API_to_rho`, `correct_observed_to_base_C` |
| Mezcla de idiomas | Comentarios y docstrings en español e inglés en el mismo módulo |
| Unidad de presión ambigua | Las funciones `_C` reciben temperatura en °C, pero `p_a`/`p_o` siguen en **psig**; nada en la firma lo indica |


<!-- res:C-03 -->
### 🟡 Resolución — 80 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **80 %** | `b21e5d8`, `5b0e53a` | Revisión de código. |

Hecho: `alpa_obs` → `alpha_obs`; un solo `commodity_type`; `t_base_c` validado (15/20); funciones en minúscula (`api_to_rho`, `celsius_to_fahrenheit`…); unidad de presión explícita en 7.x. **Se conserva a propósito**: la notación de la norma en los cálculos (`A`, `B`, `K0`, `E_m`, `DT_m`, `DP_m`) para poder cotejar con las ecuaciones. **Pendiente**: mensajes de error en inglés y docstrings en español (no se unificó el idioma en esta fase).

---

<a id="c-04"></a>
## C-04 · Docstrings y cabeceras incorrectas — ✅ 100 %

| Archivo | Problema |
|---|---|
| [`section_7_2.py:1`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_2.py#L1) | La cabecera dice `# api_mpms/mpms_11_1/section_7_1.py` |
| [`section_7_1.py:18`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_1.py#L18), [`section_7_2.py:18`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_2.py#L18) | Docstring “API MPMS 11.1.6.2” en módulos de la sección 7 |
| [`tables.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/tables.py) (11 funciones) | Todas dicen “API MPMS 11.1.6.2”, sin indicar qué tabla, unidades ni tipo admitido |
| [`section_6_1.py:36-37`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py#L36-L37) | El docstring lista 6 valores pero la anotación dice 5 ([F-04](01_errores_funcionales.md#f-04)) |
| [`section_5_1.py:10`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_5_1.py#L10) | Errata “AF'I” por “API” |
| [`generator_tables.py:180-181`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L180-L181) | Comentario “Usar tu función: correct_observed_to_base” sobre una llamada a `correct_base_to_alternate` |
| [`test_6_1.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/tests/test_6_1.py) | Errata “grabity” |
| General | Ninguna función documenta las excepciones que puede lanzar ni las unidades de cada parámetro |


<!-- res:C-04 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `5b0e53a` | Revisión de código. |

Cabeceras corregidas; cada función cita su sección (11.1.6.1, 11.1.7.2, 11.1.8.x…) y documenta unidades, límites y excepciones.

---

<a id="c-05"></a>
## C-05 · Uso de `print` en lugar de `logging` — ✅ 100 %

`generator_tables.py` usa `print(e)` y `print("Tabla … generada …")`. En una librería esto contamina la salida estándar del programa anfitrión. Usar `logger = logging.getLogger(__name__)`.


<!-- res:C-05 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `968c0fe` | — |

El generador usa `logging`.

---

<a id="c-06"></a>
## C-06 · Rutas de salida fijas — ✅ 100 %

El generador escribe `Tabla_5A.csv`, etc., en el **directorio de trabajo actual**, sobrescribiendo sin aviso cualquier archivo con el mismo nombre. Recibir un parámetro `out_dir: Path` y usar `pathlib`.


<!-- res:C-06 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `968c0fe` | — |

`--out-dir` configurable con `pathlib`.

---

<a id="herramientas-recomendadas"></a>
## Herramientas recomendadas

| Herramienta | Detectaría | Configuración mínima |
|---|---|---|
| `ruff` | C-01, `except:` desnudo (V-02), imports no absolutos (F-03), nombres (C-03) | `ruff check src --select E,F,W,B,N,E722` |
| `mypy` | F-04, F-06 (`str = None`), C-02 | `mypy src --strict` |
| `pytest` + `pytest-cov` | T-01, T-02 | ver [05_pruebas.md](05_pruebas.md) |
| `pre-commit` | Ejecutar todo lo anterior antes de cada commit | `.pre-commit-config.yaml` |

---

[⬅ Anterior: Rendimiento](06_rendimiento.md) · [Índice](README.md) · [Siguiente: Anexo de evidencias ➡](08_anexo_evidencias.md)
