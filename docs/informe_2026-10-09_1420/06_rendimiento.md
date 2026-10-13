# 06 · Rendimiento y optimizaciones

[⬅ Anterior: Pruebas](05_pruebas.md) · [Índice](README.md) · [Siguiente: Calidad y mantenibilidad ➡](07_calidad_mantenibilidad.md)

## 📑 Contenido

| ID | Severidad | Título | Cierre |
|---|---|---|:---:|
| [Mediciones](#mediciones-de-referencia) | — | Tiempos base medidos |
| [P-01](#p-01) | 🟡 Medio | Trabajo invariante recalculado en cada iteración de 6.2 | ✅ 100 % |
| [P-02](#p-02) | 🔵 Bajo | `resolve_commodity_group` reconstruye listas en cada llamada | ✅ 100 % |
| [P-03](#p-03) | 🟡 Medio | Coste y memoria del generador de tablas | 🟡 70 % |
| [P-04](#p-04) | 🔵 Bajo | Código del generador duplicado 7 veces | ✅ 100 % |

> [!NOTE]
> El README declara *“Normative fidelity over optimization”*. Ninguna de las optimizaciones propuestas cambia la fórmula ni el orden de las operaciones de punto flotante del cálculo normativo; solo evitan repetir trabajo.

---

<a id="mediciones-de-referencia"></a>
## Mediciones de referencia

Python 3.12.10, Windows 11, una sola hebra, 20 000 repeticiones:

| Función | Tiempo medio por llamada |
|---|---:|
| `correct_base_to_alternate(850, 100, 0, 'a')` | ≈ 5.5 µs |
| `correct_observed_to_base(rho_o=850, t_o=100, p_o=0, 'a')` | ≈ 20.7 µs |
| `api_round` (actual) | ≈ 1.4 µs |
| `api_round` (propuesta con `Decimal`) | ≈ 3.9 µs |

Para cálculos individuales (un ticket de medición) los tiempos son despreciables. El impacto aparece en la **generación masiva de tablas**.

---

<a id="p-01"></a>
## P-01 · Trabajo invariante recalculado en cada iteración de 6.2 — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`section_6_2.py:59-98`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L59-L98) | ✅ |

### Descripción

Cada iteración llama a `correct_base_to_alternate`, que repite operaciones cuyo resultado **no cambia** entre iteraciones:

| Operación repetida | Depende de | ¿Cambia en el bucle? |
|---|---|:---:|
| `validate_temperature_f(t_o)` | `t_o` | ❌ |
| `validate_pressure_psig(p_o)` | `p_o` | ❌ |
| `its90_to_ipts68(t_f_90=t_o)` (polinomio de 8 términos) | `t_o` | ❌ |
| `resolve_commodity_group` (tipos A y D) | tipo | ❌ (solo B puede cambiar) |
| `da_coefficient(...)` (tipos A, D, C) | tipo | ❌ |
| `delta_t = t_o - 60.0`, `7.93920 + 0.02326 * t_o` | `t_o` | ❌ |

### Recomendación

Separar el núcleo de cálculo de la capa de validación:

```python
def _base_to_alternate_core(rho_60, t_ipts68, p_psig, alpha_60, group):
    """Sin validaciones ni conversiones; recibe t ya convertida a IPTS-68."""
    ...

def correct_base_to_alternate(rho_60, t_f, p_psig, *, alpha_60=None, commodity_group=None):
    validate_temperature_f(t_f)
    p_psig = validate_pressure_psig(p_psig)
    t68 = its90_to_ipts68(t_f_90=t_f)
    ...
    return _base_to_alternate_core(...)
```

`correct_observed_to_base` valida y convierte **una vez** y llama al núcleo en el bucle. Estimación: reducción del 30–50 % del tiempo por llamada de 6.2 (a confirmar con *benchmark* tras el cambio).


<!-- res:P-01 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `869cc63` | 6.2 tipo A: 15.5 → 13.6 µs; tipo B: 22.4 → 16.7 µs. 6.1: 4.4 → 6.0 µs, ahora con validación completa y CTPL redondeado. |

`_correct_core` sin validación: 6.2 valida, convierte la temperatura y precalcula `delta_t` y el factor de DP una sola vez.

---

<a id="p-02"></a>
## P-02 · `resolve_commodity_group` reconstruye listas en cada llamada — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔵 Bajo | [`commodity_groups.py:45-69`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/constants/commodity_groups.py#L45-L69) | — |

En cada llamada se construyen dos listas por comprensión, se define una función interna y se ordena por ancho de rango. Dado que los rangos de un mismo tipo **no se solapan**, el criterio “el más estrecho” (`min(..., key=ancho)`) nunca tiene más de un candidato.

```python
_GROUPS_BY_TYPE = {
    t: tuple(sorted((COMMODITY_GROUPS[i] for i in ids), key=lambda g: g.rho_min))
    for t, ids in COMMODITY_TYPE_GROUPS.items()
}

def resolve_commodity_group(rho, commodity_type):
    groups = _GROUPS_BY_TYPE[normalize(commodity_type)]
    for g in groups:
        if g.rho_min <= rho < g.rho_max:
            return g
    ...
```


<!-- res:P-02 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8` | Revisión de código. |

Grupos precalculados y ordenados por tipo (`COMMODITY_TYPE_GROUPS`); la búsqueda es lineal sin construir listas.

---

<a id="p-03"></a>
## P-03 · Coste y memoria del generador de tablas — 🟡 70 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`generator_tables.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py) | ✅ (estimación) |

### Dimensión del problema

| Tabla | Filas × Columnas | Celdas | Tiempo estimado solo en 6.2 |
|---|---|---:|---:|
| 5A | 1 824 × 3 601 | ≈ 6.6 M | ≈ 2.3 min |
| 5B | 1 832 × 3 601 | ≈ 6.6 M | ≈ 2.3 min |
| 23A | 7 280 × 3 601 | ≈ 26.2 M | ≈ 9 min |

A esto hay que sumar `api_round` (×2–3 por celda), la creación del `dict` por fila y las celdas que fallan, que consumen las **15 iteraciones completas** antes de lanzar la excepción ([V-05](02_validacion_y_errores.md#v-05)).

### Problemas concretos

| # | Problema | Línea de ejemplo |
|---|---|---|
| 1 | `API_to_rho(api_obs)` se calcula dentro del bucle de temperatura aunque solo depende de la fila | [L34](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L34) |
| 2 | `api_round(t_obs_raw, 0.1)` se recalcula para cada fila (3 601 × N filas) en vez de una sola vez | [L31](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L31) |
| 3 | Mezclar `float` y `'-'` en las celdas obliga a `pandas` a usar `dtype=object` (≈ 4–8× más memoria y operaciones lentas) | [L46](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L46) |
| 4 | El `DataFrame` completo se mantiene en memoria y se devuelve, además de escribirse a CSV | [L53-58](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L53-L58) |
| 5 | Ejecución en un único núcleo; las filas son independientes | — |

### Recomendaciones

1. Precalcular las listas de temperaturas redondeadas y las densidades de fila **fuera** de los bucles.
2. Usar `float('nan')` en lugar de `'-'`; exportar con `df.to_csv(..., na_rep='-')` si se necesita el guion.
3. Paralelizar por filas con `concurrent.futures.ProcessPoolExecutor` (escalado casi lineal con núcleos).
4. Escribir el CSV de forma incremental (`csv.writer`) si no se necesita el `DataFrame`.
5. A medio plazo, vectorizar con NumPy el núcleo de 6.1 (las operaciones son elementales: `exp`, potencias, divisiones) y aplicar la iteración de 6.2 sobre arreglos completos con máscara de convergencia.


<!-- res:P-03 -->
### 🟡 Resolución — 70 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **70 %** | `968c0fe` | Tabla 5D completa en 30 s con 16 procesos. |

Hecho: invariantes fuera del bucle (rangos precalculados), NaN en lugar de `'-'` (dtype numérico), ejecución en paralelo por columnas (`--workers`) y salida a `--out-dir`. **Pendiente**: escritura incremental del CSV (hoy se arma el `DataFrame` completo) y vectorización con NumPy del núcleo.

---

<a id="p-04"></a>
## P-04 · Código del generador duplicado 7 veces — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔵 Bajo | [`generator_tables.py:12-341`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L12-L341) | — |

Las siete funciones `generar_tabla_*` son copias con variaciones mínimas (rango, tipo, conversión, nombre de archivo). La duplicación ya causó divergencias: distinto manejo de excepciones ([V-02](02_validacion_y_errores.md#v-02)) y el bug de la tabla 23A ([F-01](01_errores_funcionales.md#f-01)), que no existe en las otras copias.

```python
@dataclass(frozen=True)
class TableSpec:
    name: str
    commodity: str
    row_values: Sequence[float]
    row_label: str
    compute: Callable[[float, float, str], float]   # (valor_fila, temperatura, tipo) -> celda

def generate_table(spec: TableSpec, temps: Sequence[float], out_dir: Path) -> Path:
    ...
```


<!-- res:P-04 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `968c0fe` | `python scripts/generate_tables.py --list`. |

`TableSpec` + `generate_table`: una sola función para las 28 tablas de 11.1.8.

---

[⬅ Anterior: Pruebas](05_pruebas.md) · [Índice](README.md) · [Siguiente: Calidad y mantenibilidad ➡](07_calidad_mantenibilidad.md)
