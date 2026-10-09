# 07 · Referencia · resultados

[⬅ Anterior: Referencia · conversiones](06_ref_conversiones.md) · [Índice](README.md) · [Siguiente: Errores ➡](08_errores.md)

Las funciones de corrección devuelven `NamedTuple` inmutables, importables desde `api_mpms`. Se leen por atributo (`res.ctl`), por posición (`res[1]`), se desempaquetan o se convierten a `dict` con `res._asdict()`.

## 📑 Contenido

| Tipo | Devuelto por |
|---|---|
| [`ObservedToBaseResult`](#observedtobaseresult) | [`correct_observed_to_base`](03_ref_correcciones_60f.md#correct_observed_to_base) |
| [`BaseToAlternateResult`](#basetoalternateresult) | [`correct_base_to_alternate`](03_ref_correcciones_60f.md#correct_base_to_alternate) |
| [`ObservedToAlternateResult`](#observedtoalternateresult) | [`correct_observed_to_alternate`](03_ref_correcciones_60f.md#correct_observed_to_alternate) |
| [`MetricObservedToBaseResult`](#metricobservedtobaseresult) | [`correct_metric_observed_to_base`](04_ref_correcciones_metricas.md#correct_metric_observed_to_base) |
| [`MetricBaseToAlternateResult`](#metricbasetoalternateresult) | [`correct_metric_base_to_alternate`](04_ref_correcciones_metricas.md#correct_metric_base_to_alternate) |
| [Serialización](#serializacion) | Cómo guardar o enviar un resultado |

Glosario de factores:

| Campo | Nombre en la norma | Significado |
|---|---|---|
| `ctl` | CTL | Corrección por temperatura del líquido |
| `cpl` | CPL | Corrección por presión del líquido (1.0 a presión 0) |
| `ctpl` | CTPL | CTL × CPL, sin redondear |
| `ctpl_rounded` | CTPL redondeado | **Factor de corrección de volumen (VCF)** a 5 decimales — el que se usa para el volumen |
| `fp` | Fp | Factor de compresibilidad escalado |

---

<a id="observedtobaseresult"></a>
## `ObservedToBaseResult`

| Posición | Campo | Tipo | Unidad | Descripción |
|:---:|---|---|---|---|
| 0 | `rho_60` | `float` | kg/m³ | Densidad a 60 °F y 0 psig |
| 1 | `ctl` | `float` | — | CTL de las condiciones observadas a 60 °F |
| 2 | `fp` | `float` | psi⁻¹ | Fp a las condiciones observadas |
| 3 | `cpl` | `float` | — | CPL a la presión observada |
| 4 | `ctpl` | `float` | — | CTL × CPL |
| 5 | `ctpl_rounded` | `float` | — | CTPL redondeado a 0.00001 |
| 6 | `iterations` | `int` | — | Iteración en la que convergió el cálculo (informativo) |

> `📘 Norma 11.1.6.2 · Ej. 5 · pág. PDF 65`

```python
>>> from api_mpms import correct_observed_to_base
>>> res = correct_observed_to_base(rho_o=803.141, t_o=25.3, p_o=267, commodity_type="B")
>>> rho_60, ctl, fp, cpl, ctpl, ctpl_rounded, iterations = res
>>> round(rho_60, 6), ctpl_rounded, iterations
(787.507923, 1.01985, 3)

```

---

<a id="basetoalternateresult"></a>
## `BaseToAlternateResult`

| Posición | Campo | Tipo | Unidad | Descripción |
|:---:|---|---|---|---|
| 0 | `rho` | `float` | kg/m³ | Densidad a las condiciones alternas |
| 1 | `ctl` | `float` | — | CTL de las condiciones alternas a 60 °F |
| 2 | `fp` | `float` | psi⁻¹ | Fp a las condiciones alternas |
| 3 | `cpl` | `float` | — | CPL a la presión alterna |
| 4 | `ctpl` | `float` | — | CTL × CPL |
| 5 | `ctpl_rounded` | `float` | — | CTPL redondeado a 0.00001 |
| 6 | `alpha_60` | `float` | °F⁻¹ | Coeficiente de expansión térmica a 60 °F (calculado para A/B/D o el informado para C) |

> `📘 Norma 11.1.6.1 · Ej. 2 · pág. PDF 45` `🔁 Conversión: °API → kg/m³`

```python
>>> from api_mpms import correct_base_to_alternate
>>> from api_mpms.conversions import api_to_rho
>>> res = correct_base_to_alternate(rho_60=api_to_rho(-10), t_f=301.93, p_psig=1500, commodity_type="A")
>>> round(res.rho, 6), round(res.alpha_60, 12), res.ctpl_rounded
(1098.439136, 0.000251982006, 0.94411)

```

---

<a id="observedtoalternateresult"></a>
## `ObservedToAlternateResult`

| Posición | Campo | Tipo | Descripción |
|:---:|---|---|---|
| 0 | `observed` | [`ObservedToBaseResult`](#observedtobaseresult) | Corrección de las condiciones observadas a 60 °F |
| 1 | `alternate` | [`BaseToAlternateResult`](#basetoalternateresult) | Corrección de 60 °F a las condiciones alternas |

> `📘 Norma 11.1.6.3 · Ej. 7 · pág. PDF 80`

```python
>>> from api_mpms import correct_observed_to_alternate
>>> res = correct_observed_to_alternate(rho_o=853.7, t_o=84.5, p_o=157, t_f=97.4, p_psig=0, alpha_60=0.00057634)
>>> round(res.observed.rho_60, 6), res.observed.ctpl_rounded, res.alternate.ctpl_rounded
(865.279061, 0.98662, 0.97831)

```

---

<a id="metricobservedtobaseresult"></a>
## `MetricObservedToBaseResult`

| Posición | Campo | Tipo | Unidad | Descripción |
|:---:|---|---|---|---|
| 0 | `rho_base` | `float` | kg/m³ | Densidad a la temperatura base (15 °C o 20 °C) |
| 1 | `rho_60` | `float` | kg/m³ | Densidad a 60 °F (informativa) |
| 2 | `ctl` | `float` | — | CTL de las condiciones observadas a la base métrica |
| 3 | `fp` | `float` | kPa⁻¹ o bar⁻¹ | Fp en la unidad de `pressure_unit` |
| 4 | `cpl` | `float` | — | CPL a la presión observada |
| 5 | `ctpl` | `float` | — | CTL × CPL |
| 6 | `ctpl_rounded` | `float` | — | CTPL redondeado a 0.00001 |

> `📘 Norma 11.1.7.2 · Ej. 3 · pág. PDF 106`

```python
>>> from api_mpms import correct_metric_observed_to_base
>>> res = correct_metric_observed_to_base(
...     rho_o=722.6, t_o_c=-50, p_o=115, pressure_unit="kPa", t_base_c=15, commodity_type="A",
... )
>>> round(res.rho_base, 6), round(res.fp, 9), res.ctpl_rounded
(664.383677, 0.087329935, 1.08762)

```

---

<a id="metricbasetoalternateresult"></a>
## `MetricBaseToAlternateResult`

| Posición | Campo | Tipo | Unidad | Descripción |
|:---:|---|---|---|---|
| 0 | `rho` | `float` | kg/m³ | Densidad a las condiciones alternas |
| 1 | `rho_60` | `float` | kg/m³ | Densidad a 60 °F (informativa) |
| 2 | `ctl` | `float` | — | CTL de las condiciones alternas a la base métrica |
| 3 | `fp` | `float` | kPa⁻¹ o bar⁻¹ | Fp en la unidad de `pressure_unit` |
| 4 | `cpl` | `float` | — | CPL a la presión alterna |
| 5 | `ctpl` | `float` | — | CTL × CPL |
| 6 | `ctpl_rounded` | `float` | — | CTPL redondeado a 0.00001 |

> `📘 Norma 11.1.7.1 · Ej. 6 · pág. PDF 97`

```python
>>> from api_mpms import correct_metric_base_to_alternate
>>> res = correct_metric_base_to_alternate(
...     rho_base=657.3, t_base_c=15, t_c=27.35, p=1235, pressure_unit="kPa", commodity_type="B",
... )
>>> round(res.rho_60, 6), round(res.fp, 9), res.ctpl_rounded
(656.763157, 0.194781276, 0.98412)

```

---

<a id="serializacion"></a>
## Serialización

`_asdict()` devuelve un `dict` con nombres de campo estables, listo para JSON o para una fila de base de datos. Los tipos son `float` e `int` nativos:

```python
>>> import json
>>> res = correct_observed_to_base(rho_o=823.7, t_o=80.3, p_o=-5, commodity_type="A")
>>> data = res._asdict()
>>> list(data)
['rho_60', 'ctl', 'fp', 'cpl', 'ctpl', 'ctpl_rounded', 'iterations']
>>> json.loads(json.dumps(data))["ctpl_rounded"]
0.98997

```

> [!IMPORTANT]
> El orden y los nombres de los campos forman parte de la API pública. Si su sistema desempaqueta por posición, fíjese en la columna **Posición** de cada tabla.

---

[⬅ Anterior: Referencia · conversiones](06_ref_conversiones.md) · [Índice](README.md) · [Siguiente: Errores ➡](08_errores.md)
