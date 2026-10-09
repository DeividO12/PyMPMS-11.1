# 04 · Referencia · correcciones métricas (base 15 °C o 20 °C)

[⬅ Anterior: Referencia · correcciones a 60 °F](03_ref_correcciones_60f.md) · [Índice](README.md) · [Siguiente: Referencia · tablas ➡](05_ref_tablas.md)

Funciones de `api_mpms` para temperaturas base métricas. Unidades: densidad en kg/m³, temperatura en °C (ITS-90), presión en **kPa o bar** (manométrica), α60 en **°C⁻¹**.

## 📑 Contenido

| Función | Norma | Uso |
|---|---|---|
| [`correct_metric_observed_to_base`](#correct_metric_observed_to_base) | 11.1.7.2 | Condiciones observadas → 15 °C o 20 °C |
| [`correct_metric_base_to_alternate`](#correct_metric_base_to_alternate) | 11.1.7.1 | 15 °C o 20 °C → otra temperatura y presión |
| [Parámetros comunes](#comunes) | | `t_base_c`, `pressure_unit`, `commodity_type`, `alpha_60_c` |

---

<a id="comunes"></a>
## Parámetros comunes

| Parámetro | Tipo | Valores | Regla |
|---|---|---|---|
| `t_base_c` | `float` | `15` o `20` | Obligatorio. Cualquier otro valor → [`MPMSValidationError`](08_errores.md#validation). |
| `pressure_unit` | `str` | `"kPa"` o `"bar"` | Obligatorio, sin valor por defecto (no distingue mayúsculas). Fija también la unidad de `fp` en el resultado. |
| `commodity_type` | `str` o [`CommodityType`](01_conceptos.md#tipos) | `"A"`, `"B"`, `"C"`, `"D"` | Obligatorio si no se da `alpha_60_c`. |
| `alpha_60_c` | `float` | 414×10⁻⁶ a 1674×10⁻⁶ **°C⁻¹** | Solo tipo C. Si su dato está en °F⁻¹, convierta con [`alpha_f_to_alpha_c`](06_ref_conversiones.md#alpha_f_to_alpha_c) `🔁`. |

**Presión:** negativa → 0. Máximo 10 342.1 kPa / 103.421 bar (1500 psig). Ver [Conceptos › Presión](01_conceptos.md#presion).

---

<a id="correct_metric_observed_to_base"></a>
## `correct_metric_observed_to_base`

Corrige densidad y volumen desde las condiciones **observadas** a la temperatura **base métrica** (15 °C o 20 °C, presión 0).

```text
correct_metric_observed_to_base(*, rho_o, t_o_c, p_o, pressure_unit, t_base_c,
                                commodity_type=None, alpha_60_c=None) -> MetricObservedToBaseResult
```

### Parámetros

| Nombre | Tipo | Unidad | Obligatorio | Límites |
|---|---|---|:---:|---|
| `rho_o` | `float` | kg/m³ | ✅ | A: 470.5–1201.8 · B: 470.4–1209.5 · D: 714.3–1208.3 · C: > 0 |
| `t_o_c` | `float` | °C | ✅ | −50.00 a 150.00 |
| `p_o` | `float` | kPa o bar | ✅ | Ver [parámetros comunes](#comunes) |
| `pressure_unit` | `str` | — | ✅ | `"kPa"` o `"bar"` |
| `t_base_c` | `float` | °C | ✅ | 15 o 20 |
| `commodity_type` / `alpha_60_c` | | | ⚠️ | Ver [parámetros comunes](#comunes) |

### Retorna

[`MetricObservedToBaseResult`](07_ref_resultados.md#metricobservedtobaseresult): `rho_base`, `rho_60`, `ctl`, `fp` (kPa⁻¹ o bar⁻¹), `cpl`, `ctpl`, `ctpl_rounded`.

Volumen: `V_base = V_observado × ctpl_rounded`.

### Errores

| Excepción | Cuándo |
|---|---|
| [`MPMSRangeError`](08_errores.md#range) | `rho_o`, `t_o_c`, `p_o` o `alpha_60_c` fuera de límites, o densidad base resultante fuera de límites. El mensaje empieza por `API MPMS 11.1.7.2 (…)` con los datos en las unidades de entrada. |
| [`MPMSValidationError`](08_errores.md#validation) | `t_base_c` distinto de 15/20, `pressure_unit` desconocida, datos no numéricos, tipo de producto inválido |
| [`MPMSConvergenceError`](08_errores.md#convergence) | El cálculo no converge (excepcional) |

### Ejemplos

> `📘 Norma 11.1.7.2 · Ej. 2 · pág. PDF 105`

Crudo (A) de 823.7 kg/m³ a 26.8 °C y −5 kPa (presión negativa → 0), base 15 °C, 1000 m³:

```python
>>> from api_mpms import correct_metric_observed_to_base
>>> res = correct_metric_observed_to_base(
...     rho_o=823.7, t_o_c=26.8, p_o=-5, pressure_unit="kPa", t_base_c=15, commodity_type="A",
... )
>>> round(res.rho_base, 6), res.cpl, res.ctpl_rounded
(832.434018, 1.0, 0.98951)
>>> round(1000 * res.ctpl_rounded, 2)
989.51

```

> `📘 Norma 11.1.7.2 · Ej. 4 · pág. PDF 107`

Producto refinado (B) de 865.6 kg/m³ a 20 °C y 11.25 bar, base 15 °C:

```python
>>> res = correct_metric_observed_to_base(
...     rho_o=865.6, t_o_c=20, p_o=11.25, pressure_unit="bar", t_base_c=15, commodity_type="B",
... )
>>> round(res.fp, 9), res.ctpl_rounded              # fp en bar⁻¹
(7.045834505, 0.99675)

```

> `📘 Norma 11.1.7.2 · Ej. 17 · pág. PDF 116` `⚠️ Error`

Lubricante (D) de 723.45 kg/m³ a 0.42 °C: la densidad observada está dentro de límites, pero su densidad base quedaría por debajo de 800.9 kg/m³. La norma informa “densidad fuera de los límites del procedimiento”:

```python
>>> correct_metric_observed_to_base(
...     rho_o=723.45, t_o_c=0.42, p_o=0, pressure_unit="kPa", t_base_c=15, commodity_type="D",
... )
Traceback (most recent call last):
    ...
api_mpms.exceptions.validation.MPMSRangeError: API MPMS 11.1.7.2 (rho_o=723.45 kg/m3, t_o_c=0.42 degC, p_o=0 kPa, base 15 degC): rho_60 out of the limits of the procedure for commodity type D (800.9 to 1163.5 kg/m3): ...

```

#### Todos los ejemplos de la norma para esta función

| Ej. | Pág. PDF | Tipo | ρo (kg/m³) | t (°C) | P | ρ15 esperada | CTPL redondeado |
|:---:|:---:|:---:|---:|---:|---|---:|---:|
| 1 | 104 | B | 721.1 | 82.35 | 10005 kPa | 770.842780077632 | 0.93547 |
| 2 | 105 | A | 823.7 | 26.8 | −5 kPa | 832.434018321149 | 0.98951 |
| 3 | 106 | A | 722.6 | −50 | 115 kPa | 664.383677067826 | 1.08762 |
| 4 | 107 | B | 865.6 | 20 | 11.25 bar | 868.425929024799 | 0.99675 |
| 5 | 108 | B | 817.59 | 22.25 | 2587.3 kPa | 821.09497766568 | 0.99573 |
| 6 | 109 | B | 798.9 | 1.85 | 1835 kPa | 787.803957930685 | 1.01408 |
| 7 | 110 | B | 779.6 | 5.47 | 1710 kPa | 769.965411139556 | 1.01251 |
| 8 | 111 | C (α 0.0005763 °F⁻¹) | 853.7 | 29.18 | 395 kPa | 866.235845849433 | 0.98553 |
| 9 | 112 | D | 1204.6 | −49.97 | 31.1 bar | 1163.078239292499 | 1.0357 |
| 10 | 113 | D | 734.3 | 150 | 100 kPa | 820.979105094945 | 0.89442 |
| 11–17 | 114–116 | A, B, D | Fuera de límites | — | — | `MPMSRangeError` | — |

---

<a id="correct_metric_base_to_alternate"></a>
## `correct_metric_base_to_alternate`

Corrige densidad y volumen desde la temperatura **base métrica** (15 °C o 20 °C, presión 0) a una temperatura y presión **alternas**.

```text
correct_metric_base_to_alternate(*, rho_base, t_base_c, t_c, p, pressure_unit,
                                 commodity_type=None, alpha_60_c=None) -> MetricBaseToAlternateResult
```

### Parámetros

| Nombre | Tipo | Unidad | Obligatorio | Límites |
|---|---|---|:---:|---|
| `rho_base` | `float` | kg/m³ a `t_base_c` | ✅ | Su densidad equivalente a 60 °F debe estar en los límites del tipo (A, B: 610.6–1163.5; D: 800.9–1163.5) |
| `t_base_c` | `float` | °C | ✅ | 15 o 20 |
| `t_c` | `float` | °C | ✅ | −50.00 a 150.00 |
| `p` | `float` | kPa o bar | ✅ | Ver [parámetros comunes](#comunes) |
| `pressure_unit` | `str` | — | ✅ | `"kPa"` o `"bar"` |
| `commodity_type` / `alpha_60_c` | | | ⚠️ | Ver [parámetros comunes](#comunes) |

### Retorna

[`MetricBaseToAlternateResult`](07_ref_resultados.md#metricbasetoalternateresult): `rho`, `rho_60`, `ctl`, `fp` (kPa⁻¹ o bar⁻¹), `cpl`, `ctpl`, `ctpl_rounded`.

Volumen: `V_base = V_alterno × ctpl_rounded`.

> [!NOTE]
> `rho` se calcula con el CTPL sin redondear (fórmula del paso 5 de 11.1.7.1). Los ejemplos impresos de la norma muestran ρbase × CTPL redondeado; ver la [guía G9](02_guias.md#g9).

### Errores

| Excepción | Cuándo |
|---|---|
| [`MPMSRangeError`](08_errores.md#range) | `t_c`, `p` o `alpha_60_c` fuera de límites, o `rho_base` equivalente a una densidad a 60 °F fuera de límites. El mensaje empieza por `API MPMS 11.1.7.1 (…)`. |
| [`MPMSValidationError`](08_errores.md#validation) | Igual que en [`correct_metric_observed_to_base`](#correct_metric_observed_to_base) |

### Ejemplos

> `📘 Norma 11.1.7.1 · Ej. 3 · pág. PDF 94`

Producto refinado (B) de 865.6 kg/m³ a 15 °C, a 87.32 °C y 75 kPa:

```python
>>> from api_mpms import correct_metric_base_to_alternate
>>> res = correct_metric_base_to_alternate(
...     rho_base=865.6, t_base_c=15, t_c=87.32, p=75, pressure_unit="kPa", commodity_type="B",
... )
>>> round(res.rho_60, 6), round(res.fp, 9), res.ctpl_rounded       # fp en kPa⁻¹
(865.209799, 0.105233071, 0.94049)
>>> round(48.75 * res.ctpl_rounded, 7)                               # 48.75 m³ a 87.32 °C → m³ a 15 °C
45.8488875

```

> `📘 Norma 11.1.7.1 · Ej. 7 · pág. PDF 98` `🔁 Conversión: α °F⁻¹ → °C⁻¹`

Aplicación especial (C) con α60 = 0.000446759 °F⁻¹, 641.8 kg/m³ a 15 °C, a 89.9 °C y 45.35 bar:

```python
>>> from api_mpms.conversions import alpha_f_to_alpha_c
>>> res = correct_metric_base_to_alternate(
...     rho_base=641.8, t_base_c=15, t_c=89.9, p=45.35, pressure_unit="bar",
...     alpha_60_c=alpha_f_to_alpha_c(0.000446759),
... )
>>> round(res.fp, 8), res.ctpl_rounded             # fp en bar⁻¹
(41.70265108, 0.95694)

```

> `📘 Norma 11.1.7.1 · Ej. 9 · pág. PDF 99` `⚠️ Error`

Temperatura alterna de 150.025 °C (> 150 °C):

```python
>>> correct_metric_base_to_alternate(
...     rho_base=1163.55, t_base_c=20, t_c=150.025, p=10343, pressure_unit="kPa", commodity_type="B",
... )
Traceback (most recent call last):
    ...
api_mpms.exceptions.validation.MPMSRangeError: Temperature 150.025 degC out of range (-50 to 150 degC)

```

#### Todos los ejemplos de la norma para esta función

| Ej. | Pág. PDF | Tipo | ρbase (kg/m³) | Base | t (°C) | P | CTPL redondeado |
|:---:|:---:|:---:|---:|:---:|---:|---|---:|
| 1 | 92 | A | 772.3 | 15 °C | −32.8 | 24.6 bar | 1.05015 |
| 2 | 93 | A | 772.3 | 20 °C | −32.8 | 24.65 bar | 1.05504 |
| 3 | 94 | B | 865.6 | 15 °C | 87.32 | 75 kPa | 0.94049 |
| 4 | 95 | B | 793.5 | 15 °C | 27.37 | 17.05 bar | 0.98988 |
| 5 | 96 | B | 772.3 | 20 °C | −36 | 8.6 bar | 1.06073 |
| 6 | 97 | B | 657.3 | 15 °C | 27.35 | 1235 kPa | 0.98412 |
| 7 | 98 | C (α 0.000446759 °F⁻¹) | 641.8 | 15 °C | 89.9 | 45.35 bar | 0.95694 |
| 8–11 | 99–100 | A, B, D | Fuera de límites | — | — | — | `MPMSRangeError` |

---

[⬅ Anterior: Referencia · correcciones a 60 °F](03_ref_correcciones_60f.md) · [Índice](README.md) · [Siguiente: Referencia · tablas ➡](05_ref_tablas.md)
