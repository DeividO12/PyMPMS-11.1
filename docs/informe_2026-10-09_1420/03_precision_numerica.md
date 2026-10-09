# 03 · Precisión numérica y redondeo

[⬅ Anterior: Validación](02_validacion_y_errores.md) · [Índice](README.md) · [Siguiente: Estructura y empaquetado ➡](04_estructura_empaquetado.md)

## 📑 Contenido

| ID | Severidad | Título | Cierre |
|---|---|---|:---:|
| [N-01](#n-01) | 🔴 Crítico | `api_round` no detecta empates en valores grandes | ✅ 100 % |
| [N-02](#n-02) | 🟠 Alto | La “limpieza de precisión” de `api_round` corrompe deltas no decimales | ✅ 100 % |
| [N-03](#n-03) | 🟡 Medio | Rangos con `np.arange` de paso flotante | ✅ 100 % |
| [N-04](#n-04) | 🟡 Medio | Constantes y límites duplicados en varios archivos | ✅ 100 % |
| [Propuesta](#propuesta-de-reimplementación-de-api_round) | — | Reimplementación verificada de `api_round` |

---

<a id="n-01"></a>
## N-01 · `api_round` no detecta empates en valores grandes — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔴 Crítico | [`section_5_4.py:44-64`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_5_4.py#L44-L64) | ✅ |

### Descripción

La detección del caso “exactamente 0.5” usa una tolerancia **relativa a 0.5**:

```python
y = abs(x) / delta
decimal_part = y - math.floor(y)
if not math.isclose(decimal_part, 0.5, rel_tol=1e-12):   # tolerancia absoluta efectiva = 5e-13
    i = math.floor(y + 0.5)
```

El error de representación de `y` crece con su magnitud (≈ 1 ulp de `y`). Para `x = 611.15`, `delta = 0.1`: `y = 6111.4999999999…` con un error ~ 1e-12, **mayor** que la tolerancia de 5e-13. El empate no se detecta y se aplica `floor(y + 0.5)`, que redondea hacia el lado equivocado.

Cuando `y` es pequeño (p. ej. `0.15 / 0.1`) el error cae dentro de la tolerancia y funciona, por eso los ejemplos simples parecen correctos.

### Evidencia

Comparación contra `decimal.Decimal(...).quantize(..., ROUND_HALF_EVEN)` sobre valores que son empates exactos en decimal:

| Conjunto de prueba | Empates evaluados | Mal redondeados | Ejemplos |
|---|:---:|:---:|---|
| Densidad kg/m³, δ = 0.1, rango 610.6–1163.5 | 5 529 | **901** | `611.15 → 611.1` (esperado `611.2`), `612.15 → 612.1` |
| CTL, δ = 0.00001, rango 0.8–1.1 | 30 000 | **7 874** (26 %) | `0.800055 → 0.80005` (esperado `0.80006`) |
| Temperatura °C, δ = 0.05, rango −60…305 | 7 300 | **298** | `205.075 → 205.05` (esperado `205.1`) |
| Valores 0–2000, δ = 0.1 | 20 000 | **2 512** | `410.15 → 410.1` |

### Impacto

- Las funciones de tabla redondean **todas** sus entradas con `api_round` ([`tables.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/tables.py)): una densidad de entrada como `850.05` o `1000.05` puede redondearse en sentido contrario, cambiando el CTL resultante.
- El CTL final de **todas** las tablas pasa por `api_round(CTL, 0.00001)`.
- El error es **silencioso** y **dependiente de la magnitud**, por lo que es difícil de detectar con ejemplos manuales.

### Recomendación

Implementar el redondeo con aritmética decimal exacta. Ver la [propuesta verificada](#propuesta-de-reimplementación-de-api_round).


<!-- res:N-01 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `968c0fe`, `869cc63` | `test_rounding.py`: todos los empates de densidad 610–1163 y de CTL 0.8–1.1, más 720 000 casos aleatorios sin diferencias frente a `Decimal`. |

`api_round` resuelve los empates en aritmética decimal (`ROUND_HALF_EVEN`), la interpretación de la norma (10.05/0.1 = 100.5 exacto, pág. 38). Tiene un camino rápido en coma flotante, idéntico en resultado, cuando no hay empate posible.

---

<a id="n-02"></a>
## N-02 · La “limpieza de precisión” de `api_round` corrompe deltas no decimales — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟠 Alto | [`section_5_4.py:71-78`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_5_4.py#L71-L78) | ✅ |

### Descripción

Tras el redondeo, el resultado pasa por un segundo `round()` cuyo número de decimales se deduce con `int(math.log10(delta))`:

```python
if delta < 1:
    precision = abs(int(math.log10(delta)))
    return round(x_round, precision + 1)
return round(x_round, 0)
```

La heurística supone que `delta` es de la forma `k·10⁻ⁿ` con un solo dígito significativo. Con otros valores falla:

| Llamada | Resultado | Esperado | Causa |
|---|---|---|---|
| `api_round(0.75, 0.25)` | `0.8` | `0.75` | `log10(0.25) = -0.6 → int = 0 → round(…, 1)` |
| `api_round(12.5, 2.5)` | `12.0` | `12.5` | `delta >= 1 → round(…, 0)` (y además *banker's rounding* de Python) |

Otros problemas del mismo bloque:

| Caso | Resultado |
|---|---|
| `delta = 0` | `ZeroDivisionError` |
| `delta < 0` | `ValueError: math domain error` en `log10` |
| `x = nan` | `ValueError: cannot convert float NaN to integer` |
| `x = inf` | `OverflowError` |
| `x = -0.01, delta = 0.1` | `-0.0` (cero con signo) |

> [!NOTE]
> Con los deltas que la librería usa hoy (0.1, 0.05, 0.0001, 0.00001, 1, 5…) el bloque no produce errores visibles; el riesgo aparece al reutilizar la función con otros incrementos (p. ej. 0.25 o 2.5), cosa que su firma genérica invita a hacer.

### Recomendación

Eliminar la heurística: con aritmética decimal el resultado ya es exacto ([propuesta](#propuesta-de-reimplementación-de-api_round)).


<!-- res:N-02 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `968c0fe` | `api_round(0.75, 0.25) == 0.75`, `api_round(12.5, 2.5) == 12.5` y `test_no_negative_zero`. |

Se eliminó la «limpieza de precisión» con `log10`: el resultado sale exacto de la aritmética decimal. δ ≤ 0, NaN e inf lanzan `MPMSValidationError`, y ya no se devuelve −0.0.

---

<a id="n-03"></a>
## N-03 · Rangos con `np.arange` de paso flotante — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`generator_tables.py:19-20`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L19-L20) y equivalentes en cada función | — |

### Descripción

```python
api_range  = np.arange(-13.4, 169, 0.1)
temp_range = np.arange(-58.0, 302.1, 0.1)
rel_range  = np.arange(0.4710, 1.199, 0.0001)
```

La documentación de NumPy advierte que con pasos no enteros el número de elementos y la inclusión del extremo final **no están garantizados** por el error de redondeo acumulado. El código lo compensa parcialmente con `api_round`, pero:

- El extremo superior puede aparecer o no (p. ej. `302.1` redondeado podría generarse y fallar la validación).
- Dos valores consecutivos podrían colapsar en el mismo valor tras el redondeo → **columnas duplicadas** en el `dict` (la segunda sobrescribe la primera sin aviso).
- Las claves de columna `f"T_{t_obs}"` dependen de la representación del float.

### Recomendación

Iterar sobre enteros y escalar:

```python
temps = [i / 10 for i in range(-580, 3021)]          # -58.0 … 302.0, exactos tras repr
# o bien
temps = np.round(np.linspace(-58.0, 302.0, 3601), 1)
```


<!-- res:N-03 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `968c0fe` | `test_generator.py::test_grids`: número de filas y columnas, extremos y ausencia de duplicados en 6 tablas. |

`Grid` genera los rangos con índices enteros (`start + k·step`, redondeado), sin `np.arange`.

---

<a id="n-04"></a>
## N-04 · Constantes y límites duplicados en varios archivos — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | Varios | — |

### Descripción

Los mismos números aparecen copiados a mano en distintos módulos, sin una fuente única:

| Valor | Aparece en |
|---|---|
| Límites de grupo `610.6`, `770.3520`, `787.5195`, `838.3127`, `1163.5`, `800.9` | [`commodity_groups.py:18-25`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/constants/commodity_groups.py#L18-L25), [`iteration_coefficients.py:26-33`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/constants/iteration_coefficients.py#L26-L33), [`section_6_2.py:47-52`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L47-L52) |
| Densidad del agua `999.016` | 4 veces en [`section_5_1.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_5_1.py) |
| Temperatura base `60.0` | [`section_6_2.py:83`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L83) (y `T_BASE_IPTS68` en 6.1) |
| Rango de temperatura `-58 … 302` y presión `0 … 1500` | [`inputs.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/validators/inputs.py) (literal en el mensaje y en la condición) |
| Límites tipo C `(-10000000, 1000000)` | [`section_6_2.py:51`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L51) — valores arbitrarios, no simétricos |

### Impacto

Una corrección en un sitio y no en los demás genera inconsistencias difíciles de rastrear (p. ej. el `Da` elegido por `da_coefficient` dejaría de corresponder con el grupo resuelto por `resolve_commodity_group`).

### Recomendación

- Derivar `da_coefficient` y `bounds_60` de `COMMODITY_GROUPS` (añadir un campo `Da` al `dataclass`).
- Crear `constants/physical.py` con `WATER_DENSITY_60F = 999.016`, `T_BASE_F = 60.0`, `T_MIN_F`, `T_MAX_F`, `P_MAX_PSIG`.
- Para el tipo C usar `(-math.inf, math.inf)` o, mejor, no aplicar límites.


<!-- res:N-04 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `62fc683`, `5b0e53a` | Revisión de código y pruebas de límites. |

`constants/physical.py` (agua, 60 °F, límites de t, P y α, kPa/bar por psi, bases 15/20 °C). `CommodityGroup.Da`, `COMMODITY_TYPE_BOUNDS` derivados de los grupos y `OBSERVED_DENSITY_BOUNDS`. Se eliminó `iteration_coefficients.py`.

---

<a id="propuesta-de-reimplementación-de-api_round"></a>
## Propuesta de reimplementación de `api_round`

Implementación con `decimal`, verificada contra todos los casos que fallaban en N-01 y N-02:

```python
from decimal import Decimal, ROUND_HALF_EVEN
import math

from api_mpms.exceptions.validation import MPMSValidationError


def api_round(x: float, delta: float) -> float:
    """Redondea x al múltiplo de delta más cercano (empates al par)."""
    if not math.isfinite(x):
        raise MPMSValidationError(f"No se puede redondear {x!r}")
    d = Decimal(str(delta))
    if not d.is_finite() or d <= 0:
        raise MPMSValidationError(f"Incremento de redondeo inválido: {delta!r}")
    q = (Decimal(repr(float(x))) / d).to_integral_value(rounding=ROUND_HALF_EVEN)
    return float(q * d) + 0.0   # + 0.0 normaliza -0.0
```

| Entrada | Actual | Propuesta | Esperado |
|---|---|---|---|
| `(611.15, 0.1)` | 611.1 | **611.2** | 611.2 |
| `(205.075, 0.05)` | 205.05 | **205.1** | 205.1 |
| `(0.800055, 0.00001)` | 0.80005 | **0.80006** | 0.80006 |
| `(0.75, 0.25)` | 0.8 | **0.75** | 0.75 |
| `(12.5, 2.5)` | 12.0 | **12.5** | 12.5 |
| `(0.25, 0.1)` | 0.2 | 0.2 | 0.2 |
| `(-27.75, 0.05)` | -27.75 | -27.75 | -27.75 |

> [!NOTE]
> `Decimal(repr(x))` interpreta el float por su representación decimal más corta (lo que el usuario “escribió”). Así, `611.15` se trata como el empate decimal que es, en vez del binario `611.149999…`.
>
> **Coste:** ≈ 3.9 µs por llamada frente a ≈ 1.4 µs de la versión actual. Es irrelevante en cálculos individuales; para la generación masiva de tablas ver [P-03](06_rendimiento.md#p-03).

---

[⬅ Anterior: Validación](02_validacion_y_errores.md) · [Índice](README.md) · [Siguiente: Estructura y empaquetado ➡](04_estructura_empaquetado.md)
