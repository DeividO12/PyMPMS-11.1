# 03 · Referencia · correcciones a 60 °F (sistema °F / psig)

[⬅ Anterior: Guías](02_guias.md) · [Índice](README.md) · [Siguiente: Referencia · correcciones métricas ➡](04_ref_correcciones_metricas.md)

Funciones de `api_mpms` para condiciones base de **60 °F y 0 psig**. Unidades: densidad en kg/m³, temperatura en °F (ITS-90), presión en psig, α60 en °F⁻¹.

## 📑 Contenido

| Función | Norma | Uso |
|---|---|---|
| [`correct_observed_to_base`](#correct_observed_to_base) | 11.1.6.2 | Condiciones observadas → 60 °F |
| [`correct_base_to_alternate`](#correct_base_to_alternate) | 11.1.6.1 | 60 °F → otra temperatura y presión |
| [`correct_observed_to_alternate`](#correct_observed_to_alternate) | 11.1.6.3 | Condiciones observadas → otras condiciones |
| [`ctl_from_alpha`](#ctl_from_alpha) | 11.1.6.1 (tipo C, P = 0) | CTL a partir de α60, sin densidad |

Parámetros comunes: [`commodity_type` y `alpha_60`](#comunes).

---

<a id="comunes"></a>
## Parámetros comunes

| Parámetro | Tipo | Valores | Regla |
|---|---|---|---|
| `commodity_type` | `str` o [`CommodityType`](01_conceptos.md#tipos) | `"A"`, `"B"`, `"C"`, `"D"` | Obligatorio si no se da `alpha_60`. `"C"` exige `alpha_60`. |
| `alpha_60` | `float` | 230×10⁻⁶ a 930×10⁻⁶ °F⁻¹ | Solo para el tipo C. Junto con `"A"`, `"B"` o `"D"` → [`MPMSValidationError`](08_errores.md#validation). |

---

<a id="correct_observed_to_base"></a>
## `correct_observed_to_base`

Corrige densidad y volumen desde las condiciones **observadas** (temperatura y presión de la medición) a condiciones **base** (60 °F, 0 psig).

```text
correct_observed_to_base(*, rho_o, t_o, p_o, commodity_type=None, alpha_60=None) -> ObservedToBaseResult
```

### Parámetros

| Nombre | Tipo | Unidad | Obligatorio | Límites |
|---|---|---|:---:|---|
| `rho_o` | `float` | kg/m³ | ✅ | A: 470.5–1201.8 · B: 470.4–1209.5 · D: 714.3–1208.3 · C: > 0 |
| `t_o` | `float` | °F | ✅ | −58.0 a 302.0 |
| `p_o` | `float` | psig | ✅ | ≤ 1500 (negativa → 0) |
| `commodity_type` | `str` | — | ⚠️ | Ver [parámetros comunes](#comunes) |
| `alpha_60` | `float` | °F⁻¹ | ⚠️ | Ver [parámetros comunes](#comunes) |

`🔁` Si tiene °API o densidad relativa, convierta con [`api_to_rho`](06_ref_conversiones.md#api_to_rho) o [`gamma_t_to_rho`](06_ref_conversiones.md#gamma_t_to_rho). Si tiene °C, use las [funciones métricas](04_ref_correcciones_metricas.md) o [`celsius_to_fahrenheit`](06_ref_conversiones.md#celsius_to_fahrenheit).

### Retorna

[`ObservedToBaseResult`](07_ref_resultados.md#observedtobaseresult): `rho_60`, `ctl`, `fp`, `cpl`, `ctpl`, `ctpl_rounded`, `iterations`.

### Errores

| Excepción | Cuándo |
|---|---|
| [`MPMSRangeError`](08_errores.md#range) | `rho_o`, `t_o`, `p_o` o `alpha_60` fuera de límites; o la densidad a 60 °F resultante queda fuera de los límites del tipo |
| [`MPMSValidationError`](08_errores.md#validation) | Valor no numérico, `NaN`/infinito, tipo de producto desconocido, `"C"` sin `alpha_60`, `alpha_60` con A/B/D |
| [`MPMSConvergenceError`](08_errores.md#convergence) | El cálculo no converge (excepcional; ver [Errores](08_errores.md#convergence)) |

### Ejemplos

> `📘 Norma 11.1.6.2 · Ej. 6 · pág. PDF 66` `🔁 Conversión: densidad relativa → kg/m³`

Producto refinado (B) con densidad relativa 0.7322 a 139 °F y 100 psig:

```python
>>> from api_mpms import correct_observed_to_base
>>> from api_mpms.conversions import gamma_t_to_rho
>>> res = correct_observed_to_base(rho_o=gamma_t_to_rho(0.7322), t_o=139, p_o=100, commodity_type="B")
>>> round(res.rho_60, 6), res.ctpl_rounded, res.iterations
(770.349794, 0.94954, 3)

```

> `📘 Norma 11.1.6.2 · Ej. 9 · pág. PDF 69` `🔁 Conversión: °API → kg/m³`

Lubricante (D) de 62 °API observada a 302 °F y 1499.97 psig (cerca de los límites de temperatura y presión):

```python
>>> from api_mpms.conversions import api_to_rho
>>> res = correct_observed_to_base(rho_o=api_to_rho(62), t_o=302, p_o=1499.97, commodity_type="D")
>>> round(res.rho_60, 6), res.ctpl_rounded
(801.061125, 0.91197)

```

> `📘 Norma 11.1.6.2 · Ej. 16 · pág. PDF 71` `⚠️ Error`

```python
>>> correct_observed_to_base(rho_o=1208.314932900248, t_o=-57.97, p_o=240.7, commodity_type="D")
Traceback (most recent call last):
    ...
api_mpms.exceptions.validation.MPMSRangeError: rho_o 1208.314932900248 kg/m3 out of range for commodity type D (714.3 to 1208.3 kg/m3)

```

#### Todos los ejemplos de la norma para esta función

| Ej. | Pág. PDF | Tipo | Entrada | t (°F) | P (psig) | ρ60 esperado | CTPL redondeado |
|:---:|:---:|:---:|---|---:|---:|---:|---:|
| 1 | 61 | A | 823.7 kg/m³ | 80.3 | −5 | 832.048516184234 | 0.98997 |
| 2 | 62 | A | γ 0.72332 | −57.95 | 113.5 | 663.445062852402 | 1.08918 |
| 3 | 63 | B | γ 0.8665 | 68 | 11 | 868.722680008428 | 0.99646 |
| 4 | 64 | B | 41.4 °API | 72 | 375 | 820.670624131605 | 0.99624 |
| 5 | 65 | B | 803.141 kg/m³ | 25.3 | 267 | 787.507922593917 | 1.01985 |
| 6 | 66 | B | γ 0.7322 | 139 | 100 | 770.349794252060 | 0.94954 |
| 7 | 67 | C (α 0.00057634) | 853.7 kg/m³ | 84.5 | 573 | 863.403098613648 | 0.98876 |
| 8 | 68 | D | 23.6 °API | 78.7 | 128 | 917.442430351448 | 0.99343 |
| 9 | 69 | D | 62 °API | 302 | 1499.97 | 801.061124838869 | 0.91197 |
| 10–16 | 70–71 | A, B, D | Fuera de límites | — | — | `MPMSRangeError` | — |

Todos se verifican en [`tests/test_norm_examples.py`](../../tests/test_norm_examples.py).

---

<a id="correct_base_to_alternate"></a>
## `correct_base_to_alternate`

Corrige densidad y volumen desde condiciones **base** (60 °F, 0 psig) a una temperatura y presión **alternas** (por ejemplo, las de operación).

```text
correct_base_to_alternate(*, rho_60, t_f, p_psig, commodity_type=None, alpha_60=None) -> BaseToAlternateResult
```

### Parámetros

| Nombre | Tipo | Unidad | Obligatorio | Límites |
|---|---|---|:---:|---|
| `rho_60` | `float` | kg/m³ | ✅ | A, B: 610.6–1163.5 · D: 800.9–1163.5 · C: > 0 |
| `t_f` | `float` | °F | ✅ | −58.0 a 302.0 |
| `p_psig` | `float` | psig | ✅ | ≤ 1500 (negativa → 0) |
| `commodity_type` | `str` | — | ⚠️ | Ver [parámetros comunes](#comunes) |
| `alpha_60` | `float` | °F⁻¹ | ⚠️ | Ver [parámetros comunes](#comunes) |

### Retorna

[`BaseToAlternateResult`](07_ref_resultados.md#basetoalternateresult): `rho`, `ctl`, `fp`, `cpl`, `ctpl`, `ctpl_rounded`, `alpha_60`.

Volumen: `V_60 = V_alterno × ctpl_rounded` (ver [Conceptos › Volúmenes](01_conceptos.md#volumenes)).

### Errores

| Excepción | Cuándo |
|---|---|
| [`MPMSRangeError`](08_errores.md#range) | `rho_60`, `t_f`, `p_psig` o `alpha_60` fuera de límites |
| [`MPMSValidationError`](08_errores.md#validation) | Igual que en [`correct_observed_to_base`](#correct_observed_to_base) |

### Ejemplos

> `📘 Norma 11.1.6.1 · Ej. 4 · pág. PDF 47` `🔁 Conversión: densidad relativa → kg/m³`

Producto refinado (B, subgrupo jet) de densidad relativa 0.7943 a 60 °F, a 85 °F y 247.3 psig:

```python
>>> from api_mpms import correct_base_to_alternate
>>> from api_mpms.conversions import gamma_t_to_rho
>>> res = correct_base_to_alternate(rho_60=gamma_t_to_rho(0.7943), t_f=85, p_psig=247.3, commodity_type="B")
>>> round(res.rho, 6), round(res.cpl, 9), res.ctpl_rounded
(784.359025, 1.001646525, 0.98846)

```

> `📘 Norma 11.1.6.1 · Ej. 7 · pág. PDF 50`

Aplicación especial (C) con α60 = 0.000732185 °F⁻¹ y densidad 1052.6631592 kg/m³, a 97.7 °F y 287.4 psig:

```python
>>> res = correct_base_to_alternate(rho_60=1052.6631592, t_f=97.7, p_psig=287.4, alpha_60=0.000732185)
>>> round(res.ctl, 9), res.ctpl_rounded
(0.972173796, 0.97314)

```

> `📘 Norma 11.1.6.1 · Ej. 8 · pág. PDF 51` `🔁 Conversión: °API → kg/m³`

Lubricante (D) de 42.9 °API a 60 °F, a 129.3 °F y 138.8 psig:

```python
>>> from api_mpms.conversions import api_to_rho
>>> res = correct_base_to_alternate(rho_60=api_to_rho(42.9), t_f=129.3, p_psig=138.8, commodity_type="D")
>>> round(res.alpha_60, 12), res.ctpl_rounded
(0.000430296571, 0.97091)

```

> `📘 Norma 11.1.6.1 · Ej. 12 · pág. PDF 53` `⚠️ Error`

Crudo de 100.06 °API (densidad 610.4714 kg/m³ < 610.6):

```python
>>> correct_base_to_alternate(rho_60=610.471428571429, t_f=72, p_psig=0, commodity_type="A")
Traceback (most recent call last):
    ...
api_mpms.exceptions.validation.MPMSRangeError: rho_60 610.471428571429 kg/m3 out of range for commodity type A (610.6 to 1163.5 kg/m3)

```

#### Todos los ejemplos de la norma para esta función

| Ej. | Pág. PDF | Tipo | ρ60 de entrada | t (°F) | P (psig) | ρ esperada | CTPL redondeado |
|:---:|:---:|:---:|---|---:|---:|---:|---:|
| 1 | 44 | A | 17.785 °API | −27.7 | 0 | 978.178034364 | 1.03301 |
| 2 | 45 | A | −10 °API | 301.93 | 1500 | 1098.4391355882 | 0.94411 |
| 3 | 46 | B | 19.4 °API | 48.04 | −7.3 | 941.3353501926 | 1.00486 |
| 4 | 47 | B | γ 0.7943 | 85 | 247.3 | 784.3590249208 | 0.98846 |
| 5 | 48 | B | 48.0015 °API | 55.9 | 350 | 790.9208921357 | 1.00432 |
| 6 | 49 | B | 657.3 kg/m³ | 27.3 | 1234.5 | 683.0806148596 | 1.03922 |
| 7 | 50 | C (α 0.000732185) | γ 1.0537 | 97.7 | 287.4 | 1024.3915370787 | 0.97314 |
| 8 | 51 | D | 42.9 °API | 129.3 | 138.8 | 786.9754991473 | 0.97091 |
| 9–14 | 52–53 | A, B, D | Fuera de límites | — | — | `MPMSRangeError` | — |
| 15 | 54 | A | 100 °API | 200 | 0 | 530.202578933 | 0.86829 |

---

<a id="correct_observed_to_alternate"></a>
## `correct_observed_to_alternate`

Corrige desde condiciones **observadas** a condiciones **alternas** pasando por la base (60 °F). Devuelve ambos juegos de factores.

```text
correct_observed_to_alternate(*, rho_o, t_o, p_o, t_f, p_psig, commodity_type=None, alpha_60=None) -> ObservedToAlternateResult
```

### Parámetros

| Nombre | Tipo | Unidad | Obligatorio | Límites |
|---|---|---|:---:|---|
| `rho_o`, `t_o`, `p_o` | `float` | kg/m³, °F, psig | ✅ | Como en [`correct_observed_to_base`](#correct_observed_to_base) |
| `t_f`, `p_psig` | `float` | °F, psig | ✅ | Como en [`correct_base_to_alternate`](#correct_base_to_alternate) |
| `commodity_type`, `alpha_60` | | | ⚠️ | Ver [parámetros comunes](#comunes) |

### Retorna

[`ObservedToAlternateResult`](07_ref_resultados.md#observedtoalternateresult) con dos campos:

- `observed` — [`ObservedToBaseResult`](07_ref_resultados.md#observedtobaseresult) (observado → 60 °F)
- `alternate` — [`BaseToAlternateResult`](07_ref_resultados.md#basetoalternateresult) (60 °F → alterno)

Volúmenes: `V_60 = V_o × observed.ctpl_rounded` y `V_alterno = V_60 / alternate.ctpl_rounded`.

### Errores

Los de [`correct_observed_to_base`](#correct_observed_to_base) y [`correct_base_to_alternate`](#correct_base_to_alternate).

### Ejemplo

> `📘 Norma 11.1.6.3 · Ej. 1 · pág. PDF 74`

Crudo (A) de 823.7 kg/m³ observada a 80.25 °F y −5 psig (1000 bbl), llevado a −57.9 °F y 0 psig:

```python
>>> from api_mpms import correct_observed_to_alternate
>>> res = correct_observed_to_alternate(rho_o=823.7, t_o=80.25, p_o=-5, t_f=-57.9, p_psig=0, commodity_type="A")
>>> res.observed.ctpl_rounded, res.alternate.ctpl_rounded
(0.98999, 1.05697)
>>> v60 = 1000 * res.observed.ctpl_rounded
>>> round(v60, 2), round(v60 / res.alternate.ctpl_rounded, 6)
(989.99, 936.630179)

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρ60 (kg/m³) | 832.028100 | 832.028099977475 |
| Volumen a 60 °F | 989.99 | 989.99 |
| Volumen a −57.9 °F | 936.630179 | 936.630178718 |
| ρ a −57.9 °F (kg/m³) | 879.425609 | 879.425608949795 |

---

<a id="ctl_from_alpha"></a>
## `ctl_from_alpha`

CTL de un producto de **aplicación especial** (tipo C) a partir de α60, **sin densidad**. Válido solo para presión 0 (CPL = 1), que es como se construyen las tablas 6C, 24C, 54C y 60C.

```text
ctl_from_alpha(*, alpha_60, t_f) -> float
```

| Nombre | Tipo | Unidad | Obligatorio | Límites |
|---|---|---|:---:|---|
| `alpha_60` | `float` | °F⁻¹ | ✅ | 230×10⁻⁶ a 930×10⁻⁶ |
| `t_f` | `float` | °F | ✅ | −58.0 a 302.0 |

**Retorna:** `float` — CTL **sin redondear**. Para el valor de tabla, redondee con [`api_round`](06_ref_conversiones.md#api_round) (δ = 0.00001) o use [`table_6c_24c`](05_ref_tablas.md#table_6c_24c).

**Errores:** [`MPMSRangeError`](08_errores.md#range) si `alpha_60` o `t_f` están fuera de límites; [`MPMSValidationError`](08_errores.md#validation) si no son numéricos.

> `📗 Tabla 6C · pág. PDF 188` `📐 Redondeo`

```python
>>> from api_mpms import ctl_from_alpha
>>> from api_mpms.conversions import api_round
>>> [api_round(ctl_from_alpha(alpha_60=a, t_f=t), 0.00001)
...  for a, t in [(0.00047, 90.0), (0.0004703, 92.5), (0.0004706, 95.0)]]
[0.98584, 0.98464, 0.98345]

```

| α60 (°F⁻¹) | t (°F) | CTL (tabla 6C) |
|---|---:|---:|
| 0.0004700 | 90.0 | 0.98584 |
| 0.0004703 | 92.5 | 0.98464 |
| 0.0004706 | 95.0 | 0.98345 |

---

[⬅ Anterior: Guías](02_guias.md) · [Índice](README.md) · [Siguiente: Referencia · correcciones métricas ➡](04_ref_correcciones_metricas.md)
