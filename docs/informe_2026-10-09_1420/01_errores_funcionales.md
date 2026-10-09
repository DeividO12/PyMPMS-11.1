# 01 · Errores funcionales

[⬅ Volver al índice](README.md) · [Siguiente: Validación y manejo de errores ➡](02_validacion_y_errores.md)

Errores que hacen que el código devuelva resultados incorrectos o lance excepciones no controladas.

## 📑 Contenido

| ID | Severidad | Título | Cierre |
|---|---|---|:---:|
| [F-01](#f-01) | 🔴 Crítico | Tabla 23A convierte la temperatura en vez de la densidad relativa | ✅ 100 % |
| [F-02](#f-02) | 🟠 Alto | Guardia `rho_60 <= 0` inalcanzable → `ZeroDivisionError` | ✅ 100 % |
| [F-03](#f-03) | 🟠 Alto | `generator_tables.py` no se puede importar | ✅ 100 % |
| [F-04](#f-04) | 🟡 Medio | Anotaciones de retorno no coinciden con lo devuelto | ✅ 100 % |
| [F-05](#f-05) | 🟡 Medio | `alpha_60_c = 0.0` se trata como “no proporcionado” | ✅ 100 % |
| [F-06](#f-06) | 🟡 Medio | `commodity_type=None` por defecto produce `AttributeError` | ✅ 100 % |
| [F-07](#f-07) | 🟡 Medio | `its90_to_ipts68` ignora en silencio una de las dos temperaturas | ✅ 100 % |
| [F-08](#f-08) | 🟡 Medio | Presión ignorada silenciosamente cuando `rho_60 <= 0` | ✅ 100 % |
| [F-09](#f-09) | 🔵 Bajo | Valores calculados y no usados en la sección 7.1 | ✅ 100 % |
| [F-10](#f-10) | 🔵 Bajo | El grupo de producto puede cambiar entre iteraciones | ✅ 100 % |

---

<a id="f-01"></a>
## F-01 · Tabla 23A convierte la temperatura en vez de la densidad relativa — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔴 Crítico | [`Tables/generator_tables.py:317`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L317) | ✅ (lectura) |

### Descripción

Dentro del doble bucle de `generar_tabla_23a`, la densidad observada se calcula a partir de la **temperatura sin redondear** en lugar de la densidad relativa:

```python
for rel_obs_raw in rel_range:
    rel_obs = api_round(rel_obs_raw, 0.0001)
    ...
    for t_obs_raw in temp_range:
        t_obs = api_round(t_obs_raw, 0.1)
        rho_o = gamma_t_to_rho(t_obs_raw)   # ❌ debería ser rel_obs
```

### Impacto

- Cada celda de la tabla usa `ρ = T × 999.016` (p. ej. `T = 60 °F → ρ = 59 941 kg/m³`), totalmente fuera de rango.
- El resultado es una tabla compuesta por valores sin sentido o por `'-'`, porque el `except:` desnudo ([V-02](02_validacion_y_errores.md#v-02)) **oculta** el error en lugar de exponerlo.
- La fila no depende de `rel_obs`: todas las filas son idénticas.

### Recomendación

```python
rho_o = gamma_t_to_rho(rel_obs)
```

Además, mover el cálculo **fuera** del bucle interno (es invariante respecto a la temperatura, ver [P-03](06_rendimiento.md#p-03)) y sustituir el `except:` por una excepción concreta.


<!-- res:F-01 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `26df9a8`, `968c0fe` | `tests/test_generator.py::test_generate_table_23a_sample`: 0.8270 a 90 °F → **0.8393**, el valor impreso en la norma (pág. 153). Rango 0.4710–1.1989 sin la fila extra 1.1990 (NORM-T08). |

`gamma_t_to_rho(rel_obs)` en lugar de la temperatura. El generador se reescribió como una sola función parametrizada (`scripts/generate_tables.py`) que llama a `tables.table_23x`.

---

<a id="f-02"></a>
## F-02 · Guardia `rho_60 <= 0` inalcanzable → `ZeroDivisionError` — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟠 Alto | [`mpms_11_1/section_6_1.py:64-83`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py#L64-L83) | ✅ |

### Descripción

El commit `76a2f16` (*“Handle zero or negative density”*) añadió una rama para `rho_60 <= 0`, pero está ubicada **después** de las operaciones que dividen por `rho_60`:

```python
A = (DELTA_60 / 2.0) * ((K0 / rho_60**2) + (K1 / rho_60) + K2)   # línea 64 → divide por rho_60
B = (2.0 * K0 + K1 * rho_60) / (K0 + (K1 + K2 * rho_60) * rho_60) # línea 65 → divide por 0 si rho_60 = 0
...
if rho_60 <= 0:          # línea 81 → nunca se alcanza con rho_60 = 0 en la rama sin alpha
    fp = 0.0
    CPL = 1.0
```

### Evidencia

| Llamada | Resultado |
|---|---|
| `correct_base_to_alternate(0, 60, 0, commodity_group='A')` | `ZeroDivisionError: float division by zero` |
| `correct_base_to_alternate(-800, 60, 0, commodity_group='A')` | Devuelve `rho = -800.0`, `CTL ≈ 1.0` (sin error) |

### Impacto

- La guardia solo es útil para la rama con `alpha_60` (tipo C) y da una falsa sensación de protección.
- Una densidad negativa se procesa y devuelve resultados absurdos sin aviso.

### Recomendación

Validar la densidad **al inicio** de la función y distinguir explícitamente el caso “tipo C sin densidad”:

```python
if alpha_60 is None:
    if rho_60 is None or not math.isfinite(rho_60) or rho_60 <= 0:
        raise MPMSValidationError(f"rho_60 debe ser > 0 (recibido {rho_60})")
```

Ver también [V-01](02_validacion_y_errores.md#v-01) y [F-08](#f-08).


<!-- res:F-02 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `5b0e53a` | `test_validation.py::test_base_to_alternate_rejects_invalid_density` (0, −800, NaN, ±inf, None, '850') y `test_base_density_out_of_range_is_not_extrapolated`. |

La densidad se valida **al inicio** (`validate_density`, > 0 y finita) y después contra los límites del tipo (`resolve_commodity_group` lanza `MPMSRangeError`). Se eliminó la rama `rho_60 <= 0`.

---

<a id="f-03"></a>
## F-03 · `generator_tables.py` no se puede importar — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟠 Alto | [`Tables/generator_tables.py:1-9`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L1-L9) | ✅ |

### Descripción

El módulo usa imports **no relativos al paquete**, distintos al resto de la librería:

```python
from exceptions.convergence import MPMSConvergenceError   # ❌
from mpms_11_1.section_5_1 import ...                     # ❌
```

y depende de `numpy` y `pandas`, que no están declarados (ver [E-03](04_estructura_empaquetado.md#e-03)).

### Evidencia

| Forma de importar | Resultado |
|---|---|
| `import api_mpms.tables.generator_tables` (con `src` en `sys.path`) | `ModuleNotFoundError: No module named 'exceptions'` |
| `import tables.generator_tables` (con `src/api_mpms` en `sys.path`) | `ModuleNotFoundError: No module named 'api_mpms'` (cadena desde `section_6_1`) |
| Entorno sin `numpy` | `ModuleNotFoundError: No module named 'numpy'` |

> [!WARNING]
> No existe ninguna forma de ejecutar este módulo con la estructura actual del paquete; solo funcionaría con una manipulación manual de `sys.path` que incluya **ambas** rutas.

### Recomendación

```python
from api_mpms.exceptions.convergence import MPMSConvergenceError
from api_mpms.mpms_11_1.section_5_1 import API_to_rho, rho_to_API, gamma_t_to_rho, rho_to_gamma_t
...
```

Y declarar `numpy`/`pandas` como dependencia opcional (`[project.optional-dependencies] tables = [...]`). Considerar mover el generador fuera del paquete (p. ej. `scripts/`), ya que es una herramienta y no parte de la API.


<!-- res:F-03 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `26df9a8`, `6b68257` | `tests/test_generator.py` importa y ejecuta el script; la tabla 5D completa (805 × 3 601) se generó en 30 s con 16 procesos. |

Movido a `scripts/generate_tables.py` con imports absolutos `api_mpms.*`; `numpy`/`pandas` declarados en el extra `[tables]`.

---

<a id="f-04"></a>
## F-04 · Anotaciones de retorno no coinciden con lo devuelto — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | Varios (ver tabla) | ✅ |

### Descripción

| Función | Anotación | Devuelve realmente |
|---|---|---|
| [`correct_base_to_alternate`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py#L30) | `Tuple[float × 5]` | **6** valores (`rho, CTL, fp, CPL, CTPL, alpha_60`) |
| [`correct_observed_to_base_C`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_2.py#L16) | `Tuple[float × 5]` | **6** valores |
| Todas las funciones `table_*` ([`tables.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/tables.py), [`Tables/`](https://github.com/DeividO12/PyMPMS-11.1/tree/4f1216d/src/api_mpms/Tables/)) | `Tuple[float × 5]` | **un `float`** (CTL) |

### Impacto

- Herramientas como `mypy`/Pylance reportarán errores falsos o, peor, no detectarán desempaquetados incorrectos.
- El historial (`d54fa2d`) muestra que el número de valores de retorno ya cambió una vez; con tuplas posicionales cualquier llamador desactualizado falla con `ValueError: too many values to unpack` (o, si coincide el número, **toma el valor equivocado sin error**).

### Recomendación

Corregir las anotaciones y migrar a un `NamedTuple` (ver [C-02](07_calidad_mantenibilidad.md#c-02)):

```python
def table_6x(...) -> float: ...
```


<!-- res:F-04 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `5b0e53a` | `mypy src` sin errores; la CI ejecuta mypy. |

Resultados `NamedTuple` (`BaseToAlternateResult`, `ObservedToBaseResult`, `Metric*Result`, `ObservedToAlternateResult`) y funciones de tabla anotadas `-> float`.

---

<a id="f-05"></a>
## F-05 · `alpha_60_c = 0.0` se trata como “no proporcionado” — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`section_7_1.py:26`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_1.py#L26), [`section_7_2.py:26`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_2.py#L26) | ✅ |

### Descripción

```python
alpha_60_f = alphac_to_alphaf(alpha_60_c) if alpha_60_c else None
```

`0.0` es *falsy*, por lo que un coeficiente explícito de 0 se descarta y el flujo cae en la resolución por grupo de producto.

### Evidencia

`correct_observed_to_alternate_C(rho_t=0, t_a_c=30, p_a=0, commodity_type='C', alpha_60_c=0.0)` → `MPMSValidationError: commodity_group must be A, B, or D`.

### Recomendación

```python
alpha_60_f = alphac_to_alphaf(alpha_60_c) if alpha_60_c is not None else None
```

(Si `alpha = 0` no es físicamente válido, rechazarlo con un mensaje explícito en lugar de producir un error engañoso — ver [V-04](02_validacion_y_errores.md#v-04).)


<!-- res:F-05 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `5b0e53a` | `test_validation.py::test_invalid_alpha` (0.0, negativo, NaN, inf). |

`alpha_60_c is not None`. Según la norma, α = 0 queda fuera de 230–930×10⁻⁶ °F⁻¹, así que ahora es un `MPMSRangeError` explícito y no un «no proporcionado».

---

<a id="f-06"></a>
## F-06 · `commodity_type=None` por defecto produce `AttributeError` — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`section_7_1.py:14`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_1.py#L14), [`section_7_2.py:14`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_2.py#L14), [`section_6_2.py:39`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L39), [`commodity_groups.py:41`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/constants/commodity_groups.py#L41) | ✅ |

### Descripción

`commodity_type: str = None` se pasa directamente a `correct_observed_to_base`, que ejecuta `commodity_type.lower()` sin comprobar el tipo.

### Evidencia

| Llamada | Resultado |
|---|---|
| `correct_observed_to_alternate_C(rho_t=850, t_a_c=30, p_a=0)` | `AttributeError: 'NoneType' object has no attribute 'lower'` |
| `correct_base_to_alternate(800, 60, 0, commodity_group=1)` | `AttributeError: 'int' object has no attribute 'lower'` |

### Recomendación

- Hacer el parámetro obligatorio o tiparlo como `Optional[str]` y validarlo.
- Centralizar la normalización en un validador que lance `MPMSValidationError` (ver [V-06](02_validacion_y_errores.md#v-06)).


<!-- res:F-06 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8` | `test_validation.py::test_invalid_commodity_type`. |

Validador único `validate_commodity_type` con `Enum CommodityType`: `None`, números o textos desconocidos lanzan `MPMSValidationError`.

---

<a id="f-07"></a>
## F-07 · `its90_to_ipts68` ignora en silencio una de las dos temperaturas — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`section_5_3.py:19-70`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_5_3.py#L19-L70) | ✅ |

### Descripción

1. Si se pasan **ambos** `t_f_90` y `t_c_90`, se usa `t_c_90` y se descarta `t_f_90` sin aviso.
   - `its90_to_ipts68(t_f_90=212, t_c_90=0)` → `32.0` (resultado de 0 °C, no de 212 °F).
2. `out_fahrenheit: Optional[bool] = True`: pasar `None` devuelve **Celsius** (se evalúa como falso).
   - `its90_to_ipts68(t_f_90=212, out_fahrenheit=None)` → `100.0256…` (°C).

### Recomendación

```python
if (t_f_90 is None) == (t_c_90 is None):
    raise MPMSValidationError("Proporcione exactamente uno de t_f_90 o t_c_90")
...
out_fahrenheit: bool = True
```


<!-- res:F-07 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `5b0e53a` | `test_its90_requires_exactly_one_temperature`, `test_its90_celsius_input_returns_celsius` y 19 valores t* de la norma (≤ 1e-14). |

Se exige exactamente una temperatura y se devuelve en la misma unidad de entrada, como indica 11.1.5.3 (NORM-03). Se eliminó `out_fahrenheit`.

---

<a id="f-08"></a>
## F-08 · Presión ignorada silenciosamente cuando `rho_60 <= 0` — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`section_6_1.py:81-83`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py#L81-L83) | ✅ |

### Descripción

Con `alpha_60` y `rho_60 = 0` (uso de las tablas 6C/24C/54C/60C), el código fija `Fp = 0` y `CPL = 1` **independientemente de la presión**.

### Evidencia

`correct_base_to_alternate(0, 100, 1000, alpha_60=0.0005)` → `CPL = 1.0` con 1000 psig.
`correct_observed_to_base(rho_o=0, t_o=100, p_o=500, commodity_type='c', alpha_60=0.0005)` → `CPL = 1.0`.

### Impacto

Las funciones públicas aceptan una presión distinta de 0 que no tiene efecto, sin advertirlo. Correcto para las tablas (p = 0), pero peligroso para cualquier otro llamador.

### Recomendación

Si `rho_60 <= 0` y `p_psig > 0`, lanzar `MPMSValidationError("Se requiere densidad para calcular CPL")`, o exponer una función específica `ctl_from_alpha(...)` que no reciba presión.


<!-- res:F-08 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `5b0e53a` | `test_type_c_with_density_and_pressure` y `test_ctl_from_alpha_matches_full_procedure`. |

La presión nunca se ignora: 6.1/6.2 exigen ρ > 0 y calculan Fp/CPL. Las tablas C (sin densidad, P = 0) usan `ctl_from_alpha`, validado contra 1 428 valores impresos (NORM-T07, NORM-26).

---

<a id="f-09"></a>
## F-09 · Valores calculados y no usados en la sección 7.1 — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔵 Bajo | [`section_7_1.py:29-36`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_7_1.py#L29-L36) | — |

### Descripción

`correct_observed_to_alternate_C` calcula `rho` (densidad a condiciones alternas) y `alpha_60_a`, pero los descarta y devuelve `rho_60`. Su contraparte `correct_observed_to_base_C` sí devuelve `rho` y por eso tiene **6** valores frente a los **5** de la 7.1. Dos funciones hermanas con contratos distintos dificultan su uso.

### Recomendación

Definir explícitamente qué densidad devuelve cada función y unificar la forma del resultado (ver [C-02](07_calidad_mantenibilidad.md#c-02)).


<!-- res:F-09 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `5b0e53a` | Ejemplos 7.1-1 a 7.1-7 de la norma. |

`correct_metric_base_to_alternate` (11.1.7.1) devuelve la densidad a condiciones alternas `rho` (Paso 5) y `rho_60`; 7.1 y 7.2 tienen resultados con nombre equivalentes.

---

<a id="f-10"></a>
## F-10 · El grupo de producto puede cambiar entre iteraciones — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔵 Bajo | [`section_6_1.py:57`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py#L57), [`section_6_2.py:59-98`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L59-L98) | ✅ (barrido) |

### Descripción

Para tipo B, `resolve_commodity_group` se evalúa en cada iteración con el `rho_60` actual. Si la iteración cruza un límite de grupo (p. ej. 770.352 o 787.5195 kg/m³), los coeficientes K cambian de forma discontinua, lo que en teoría puede provocar oscilación.

### Evidencia

Un barrido denso de la zona 740–840 kg/m³ × −58…302 °F (14 800 casos) **no produjo ningún fallo de convergencia**. El riesgo es bajo, pero no existe una prueba que lo proteja.

### Recomendación

Añadir pruebas de regresión con densidades en los límites exactos de cada grupo (y ±1e-6).


<!-- res:F-10 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `5b0e53a` | Ejemplos 6.2-5, 6.2-6, 7.2-1, 7.2-6 y 7.2-7, con el mismo número de iteraciones que la norma. |

**La norma exige este comportamiento** (pág. 55: «sub-group switching is automatically performed»). Se conserva y se protege con pruebas. Además, el extremo 1163.5 kg/m³ de fuel oil ahora es inclusivo y su Da es 1.3 (NORM-11).

---

[⬅ Volver al índice](README.md) · [Siguiente: Validación y manejo de errores ➡](02_validacion_y_errores.md)
