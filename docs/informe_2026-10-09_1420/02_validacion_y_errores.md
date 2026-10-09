# 02 · Validación de entradas y manejo de errores

[⬅ Anterior: Errores funcionales](01_errores_funcionales.md) · [Índice](README.md) · [Siguiente: Precisión numérica ➡](03_precision_numerica.md)

## 📑 Contenido

| ID | Severidad | Título | Cierre |
|---|---|---|:---:|
| [V-01](#v-01) | 🟠 Alto | No se valida la densidad en ningún punto | ✅ 100 % |
| [V-02](#v-02) | 🟠 Alto | `except:` desnudo oculta errores en el generador | ✅ 100 % |
| [V-03](#v-03) | 🟡 Medio | Presión `NaN` pasa la validación | ✅ 100 % |
| [V-04](#v-04) | 🟡 Medio | `alpha_60` no se valida | ✅ 100 % |
| [V-05](#v-05) | 🟡 Medio | Entradas fuera de rango se reportan como error de convergencia | ✅ 100 % |
| [V-06](#v-06) | 🟡 Medio | Validación del tipo de producto inconsistente | ✅ 100 % |
| [V-07](#v-07) | 🔵 Bajo | Conversiones de unidades sin protección | ✅ 100 % |
| [Resumen](#resumen-de-cobertura-de-validación) | — | Matriz de cobertura de validación |

---

<a id="v-01"></a>
## V-01 · No se valida la densidad en ningún punto — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟠 Alto | [`validators/inputs.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/validators/inputs.py), [`section_6_1.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py), [`section_6_2.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py) | ✅ |

### Descripción

El módulo `validators` solo valida temperatura y presión. La densidad, que es la entrada principal, no tiene validación: ni tipo, ni finitud, ni signo, ni rango.

Además, `resolve_commodity_group` tiene un *fallback* de “grupo más cercano” ([`commodity_groups.py:63-69`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/constants/commodity_groups.py#L63-L69)) que hace que **cualquier** densidad, por absurda que sea, produzca un resultado.

### Evidencia

| Llamada | Resultado |
|---|---|
| `correct_base_to_alternate(5000, 60, 0, commodity_group='A')` | Devuelve resultados (extrapolación silenciosa) |
| `correct_base_to_alternate(-800, 60, 0, commodity_group='A')` | `rho = -800.0` |
| `correct_base_to_alternate(float('nan'), 60, 0, commodity_group='A')` | Tupla de `nan` (sin error) |
| `correct_base_to_alternate(0, 60, 0, commodity_group='A')` | `ZeroDivisionError` |

### Recomendación

Añadir `validate_density_kgm3(rho, *, allow_zero=False)` en `validators/inputs.py` y llamarlo al inicio de 6.1 y 6.2. Decidir explícitamente si el *fallback* al grupo más cercano es deseado; si lo es, documentarlo y emitir un `warnings.warn(...)`.

```python
def validate_density_kgm3(rho: float) -> float:
    if not isinstance(rho, (int, float)) or isinstance(rho, bool):
        raise MPMSValidationError(f"Densidad inválida: {rho!r}")
    if not math.isfinite(rho) or rho <= 0:
        raise MPMSValidationError(f"Densidad debe ser finita y > 0 (recibido {rho})")
    return float(rho)
```


<!-- res:V-01 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `62fc683`, `5b0e53a` | Ejemplos de error 6.1-12/13/14, 6.2-10…16, 7.1-8…11 y 7.2-11…16 → `MPMSRangeError`. |

`validate_density` (tipo, finitud, > 0); límites inclusivos de ρ60 por tipo (11.1.6.1 Paso 1) y de ρo (11.1.6.2 Paso 1: A 470.5–1201.8, B 470.4–1209.5, D 714.3–1208.3). Se eliminó el *fallback* al grupo más cercano.

---

<a id="v-02"></a>
## V-02 · `except:` desnudo oculta errores en el generador — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟠 Alto | [`generator_tables.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py) — líneas [45](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L45), [93](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L93), [234](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L234), [280](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L280), [328](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py#L328) | ✅ |

### Descripción

Cinco de las siete funciones usan `except:` sin tipo. Esto captura **todo**, incluido `KeyboardInterrupt`, `SystemExit`, `NameError` o `TypeError` debidos a bugs. El manejo además es inconsistente entre funciones:

| Función | Captura |
|---|---|
| `generar_tabla_5a`, `5b`, `6b`, `6d`, `23a` | `except:` (todo) |
| `generar_tabla_5d` | solo `MPMSConvergenceError` |
| `generar_tabla_6a` | `Exception`, e imprime el mensaje |

### Impacto

- El bug [F-01](01_errores_funcionales.md#f-01) queda oculto: la tabla se genera “con éxito”.
- Un `Ctrl+C` durante una generación de varios minutos no detiene el proceso: se convierte en un `'-'` y el bucle sigue.

### Recomendación

```python
except (MPMSConvergenceError, MPMSValidationError):
    api_60 = None   # o float('nan'); ver P-03
```


<!-- res:V-02 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `26df9a8`, `968c0fe` | `test_generate_table_23a_sample` (celdas fuera de rango vacías). |

Solo se capturan `MPMSConvergenceError` y `MPMSValidationError`; las celdas no calculables quedan vacías (NaN), nunca 0 (NORM-T13).

---

<a id="v-03"></a>
## V-03 · Presión `NaN` pasa la validación — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`validators/inputs.py:13-20`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/validators/inputs.py#L13-L20) | ✅ |

### Descripción

Las comparaciones con `NaN` siempre son `False`, por lo que `P < 0` y `P > 1500` no se cumplen y la función **devuelve `nan`**. `validate_temperature_f` sí rechaza `NaN` (por usar `not (a <= t <= b)`), lo que muestra la inconsistencia.

Además:
- Un `None` produce `TypeError` en lugar de `MPMSValidationError`.
- Las presiones negativas se fuerzan a 0 sin ningún aviso (documentado en el README, pero no en el código ni mediante `warnings`).

### Evidencia

`validate_pressure_psig(float('nan'))` → `nan`.
`correct_observed_to_base(rho_o=800, t_o=60, p_o=float('nan'), commodity_type='a')` → `MPMSConvergenceError` (mensaje engañoso).

### Recomendación

```python
def validate_pressure_psig(p: float) -> float:
    if not math.isfinite(p):
        raise MPMSValidationError(f"Presión inválida: {p}")
    if p > 1500:
        raise MPMSValidationError(...)
    return max(p, 0.0)
```


<!-- res:V-03 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8` | `test_invalid_pressure` y `test_negative_pressure_is_zero`. |

`validate_pressure_psig` rechaza NaN/inf/None/no numéricos. P < 0 → 0 y P > 1500 → error, como en la norma (pág. 41).

---

<a id="v-04"></a>
## V-04 · `alpha_60` no se valida — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`section_6_1.py:47-49`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py#L47-L49), [`section_6_1.py:96-100`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py#L96-L100) | ✅ |

### Descripción

El coeficiente de expansión térmica suministrado por el usuario se usa sin ningún control.

### Evidencia

| Llamada | Resultado |
|---|---|
| `correct_base_to_alternate(800, 300, 0, alpha_60=1.0)` | `CTL = 0.0`, `rho = 0.0` (subdesbordamiento de `exp`, sin error) |
| `correct_base_to_alternate(800, 100, 0, alpha_60=-0.001)` | Resultado devuelto sin aviso |
| `correct_observed_to_base(rho_o=1e-3, t_o=100, p_o=500, commodity_type='c', alpha_60=0.0005)` | `OverflowError: math range error` (no controlado) |

### Recomendación

Validar que `alpha_60` sea finito y esté en un rango plausible (definido por el equipo) y capturar `OverflowError` alrededor de `math.exp` convirtiéndolo en `MPMSValidationError`.


<!-- res:V-04 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `62fc683` | `test_invalid_alpha`, `test_table_6c_alpha_out_of_range` y `test_metric_c_alpha_range_edges`. |

α60 limitado a 230.0–930.0×10⁻⁶ °F⁻¹, equivalente a 414–1674×10⁻⁶ °C⁻¹ (11.1.6.1 Paso 1). Con α > 0 el exponente de CTL está acotado y el `OverflowError` original venía de densidades absurdas, que ahora se rechazan.

---

<a id="v-05"></a>
## V-05 · Entradas fuera de rango se reportan como error de convergencia — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`section_6_2.py:55-102`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L55-L102) | ✅ |

### Descripción

Cuando la densidad base buscada cae fuera de `bounds_60`, la iteración queda “anclada” en el límite (`max(min(...))`) y agota las 15 iteraciones antes de lanzar `MPMSConvergenceError`. Lo mismo ocurre con `NaN` o densidades negativas.

### Evidencia

Barrido de ≈ 21 000 combinaciones por tipo (600–1180 kg/m³ × −58…302 °F):

| Tipo | Fallos | Densidades observadas con fallo |
|---|:---:|---|
| A | 1 916 | Extremos: desde 600 kg/m³ y desde 1 092.5 kg/m³ hacia arriba (con temperaturas extremas) |
| B | 2 108 | Extremos: desde 600 kg/m³ y desde 1 075 kg/m³ hacia arriba |
| D | 8 077 | Extremo inferior (límite de grupo 800.9 kg/m³) y desde 1 080 kg/m³ hacia arriba |

Los fallos se concentran en los extremos, donde el `rho_60` buscado cae fuera de los límites del tipo: son **errores de dominio** que se reportan como errores de convergencia.

### Impacto

- El llamador no puede distinguir “entrada fuera de rango” de “algoritmo inestable”.
- Se desperdician 15 iteraciones completas por cada caso inválido (relevante en la generación de tablas).
- El mensaje tiene `15` codificado a mano en vez de usar `_MAX_ITER`.

### Recomendación

1. Detectar si el valor queda fijado al límite en dos iteraciones consecutivas y lanzar `MPMSValidationError("rho_60 fuera de rango para el tipo X")`.
2. Usar `f"... within {_MAX_ITER} iterations"` e incluir `commodity_type` y `p_o` en el mensaje.


<!-- res:V-05 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `5b0e53a` | `test_base_density_outside_limits_is_range_error_not_convergence` y `test_non_convergence_keeps_last_result`. |

Nueva `MPMSRangeError` (subclase de `MPMSValidationError`) para el Paso 1 y para ρ60 anclado al límite (Paso 7). `MPMSConvergenceError` solo para la no convergencia real; conserva `last_result` (nota del Paso 6). El mensaje usa `_MAX_ITER`.

---

<a id="v-06"></a>
## V-06 · Validación del tipo de producto inconsistente — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | [`commodity_groups.py:41-43`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/constants/commodity_groups.py#L41-L43), [`section_6_1.py:52-55`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_1.py#L52-L55), [`section_6_2.py:39-41`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_6_2.py#L39-L41) | ✅ |

### Descripción

| Aspecto | 6.1 | 6.2 | `resolve_commodity_group` |
|---|---|---|---|
| Nombre del parámetro | `commodity_group` | `commodity_type` | `commodity_type` |
| Valores aceptados | A, B, D (+ C implícito con alpha) | a, b, c, d | a, b, d |
| Mensaje de error | “commodity_group (A, B, D) required…” | “commodity_type must be 'a', 'b', 'c', or 'd'” | “commodity_group must be A, B, or D” |

Consecuencia: `correct_observed_to_base(..., commodity_type='c')` **sin** `alpha_60` pasa la validación de 6.2 pero falla dentro de `resolve_commodity_group` con el mensaje *“commodity_group must be A, B, or D”*, que no menciona que falta `alpha_60`.

También: con `commodity_type='a'` **y** `alpha_60` dado, el alpha se usa y el tipo se ignora silenciosamente (solo afecta a los límites de iteración).

### Recomendación

Crear un `Enum` `CommodityType` y un único validador:

```python
class CommodityType(str, Enum):
    CRUDE = "a"; PRODUCTS = "b"; SPECIAL = "c"; LUBRICANTS = "d"

def validate_commodity(ct, alpha_60):
    ct = CommodityType(str(ct).lower())          # ValueError → MPMSValidationError
    if ct is CommodityType.SPECIAL and alpha_60 is None:
        raise MPMSValidationError("El tipo C requiere alpha_60")
    return ct
```


<!-- res:V-06 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8`, `5b0e53a` | `test_type_c_requires_alpha`, `test_alpha_and_commodity_abd_are_exclusive` y `test_commodity_type_normalization`. |

`CommodityType` + `validate_commodity_and_alpha`: un solo parámetro `commodity_type`; C exige α60 y α60 es excluyente con A/B/D (NORM-16, NORM-18).

---

<a id="v-07"></a>
## V-07 · Conversiones de unidades sin protección — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔵 Bajo | [`section_5_1.py:20-42`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/mpms_11_1/section_5_1.py#L20-L42) | ✅ |

### Descripción

| Función | Caso problemático |
|---|---|
| `rho_to_API(0)` | `ZeroDivisionError` |
| `API_to_rho(-131.5)` | `ZeroDivisionError` |
| `API_to_rho(-200)` | Densidad negativa sin error |

Ninguna función tiene anotación de retorno y `alphac_to_alphaf` no tiene anotación de parámetro.

### Recomendación

Validar dominio (`rho > 0`, `API > -131.5`) y añadir anotaciones `-> float`.


<!-- res:V-07 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `b21e5d8` | `test_unit_conversion_domain` y `test_pressure_and_fp_conversions`. |

Validación de dominio en `rho_to_api`, `api_to_rho`, `gamma_t_to_rho` y `rho_to_gamma_t`; anotaciones `-> float`. Se añadieron las conversiones de presión, Fp y α °F→°C de 11.1.5.1 (NORM-02).

---

<a id="resumen-de-cobertura-de-validación"></a>
## Resumen de cobertura de validación

| Entrada | Tipo | Finitud (`NaN`/`inf`) | Signo / cero | Rango | Excepción correcta |
|---|:---:|:---:|:---:|:---:|:---:|
| Temperatura °F | ❌ | ✅ | n/a | ✅ | ⚠️ (`None` → `TypeError`) |
| Temperatura °C (7.x) | ❌ | ✅ (tras convertir) | n/a | ✅ (tras convertir) | ⚠️ |
| Presión psig | ❌ | ❌ | ⚠️ (clamp silencioso) | ✅ | ⚠️ |
| Densidad | ❌ | ❌ | ❌ | ❌ | ❌ |
| `alpha_60` | ❌ | ❌ | ❌ | ❌ | ❌ |
| Tipo de producto | ❌ | n/a | n/a | ✅ | ⚠️ (`AttributeError`) |
| `delta` de `api_round` | ❌ | ❌ | ❌ | n/a | ❌ |

---

[⬅ Anterior: Errores funcionales](01_errores_funcionales.md) · [Índice](README.md) · [Siguiente: Precisión numérica ➡](03_precision_numerica.md)
