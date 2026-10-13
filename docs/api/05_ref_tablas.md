# 05 · Referencia · tablas (`api_mpms.tables`)

[⬅ Anterior: Referencia · correcciones métricas](04_ref_correcciones_metricas.md) · [Índice](README.md) · [Siguiente: Referencia · conversiones ➡](06_ref_conversiones.md)

Funciones que devuelven **el mismo valor que la tabla impresa** de API MPMS 11.1 (sección 11.1.8). A diferencia de las [funciones de corrección](03_ref_correcciones_60f.md):

- **Redondean las entradas** al incremento de la tabla (por ejemplo, °API a 0.1 y °F a 0.1).
- **Redondean la salida** (CTL a 0.00001; °API a 0.1; densidad relativa a 0.0001; kg/m³ a 0.1).
- Trabajan siempre a **presión 0**.
- Reciben la unidad de la tabla (°API, densidad relativa o kg/m³) sin conversión previa.

```python
>>> from api_mpms import tables

```

## 📑 Contenido

| Tablas | Función | Entrada → salida | Unidades |
|---|---|---|---|
| 5A, 5B, 5D | [`table_5x`](#table_5x) | °API observada → °API a 60 °F | °API, °F |
| 6A, 6B, 6D | [`table_6x`](#table_6x) | °API a 60 °F → CTL | °API, °F |
| 23A, 23B, 23D | [`table_23x`](#table_23x) | Densidad relativa observada → densidad relativa 60/60 °F | adimensional, °F |
| 24A, 24B, 24D | [`table_24x`](#table_24x) | Densidad relativa 60/60 °F → CTL | adimensional, °F |
| 53A, 53B, 53D | [`table_53x`](#table_53x) | Densidad observada → densidad a 15 °C | kg/m³, °C |
| 54A, 54B, 54D | [`table_54x`](#table_54x) | Densidad a 15 °C → CTL | kg/m³, °C |
| 59A, 59B, 59D | [`table_59x`](#table_59x) | Densidad observada → densidad a 20 °C | kg/m³, °C |
| 60A, 60B, 60D | [`table_60x`](#table_60x) | Densidad a 20 °C → CTL | kg/m³, °C |
| 6C, 24C, 54C, 60C | [Tablas C](#tablas-c) | α → CTL | °F⁻¹ / °C⁻¹, °F / °C |
| — | [`ctl_from_observed_*`](#ctl_observed) | Densidad observada → CTL directo | según función |

La letra de la tabla se indica con `commodity_type`: **A** crudos, **B** productos refinados, **D** lubricantes. Errores: [`MPMSRangeError`](08_errores.md#range) fuera del rango de la tabla y [`MPMSValidationError`](08_errores.md#validation) con datos inválidos. Rangos de cada tabla: [09 · Límites](09_limites.md#tablas).

---

<a id="table_5x"></a>
## `table_5x` — Tablas 5A / 5B / 5D

```text
table_5x(*, api_obs, t_f_obs, commodity_type) -> float     # °API a 60 °F, redondeada a 0.1
```

| Parámetro | Unidad | Redondeo de entrada |
|---|---|---|
| `api_obs` | °API observada | 0.1 |
| `t_f_obs` | °F | 0.1 |
| `commodity_type` | `"A"`, `"B"` o `"D"` | — |

> `📗 Tabla 5A · pág. PDF 142` `📗 Tabla 5B · pág. PDF 144` `📗 Tabla 5D · pág. PDF 146`

```python
>>> tables.table_5x(api_obs=65.0, t_f_obs=135.0, commodity_type="A")
56.0
>>> tables.table_5x(api_obs=65.0, t_f_obs=135.0, commodity_type="B")
55.2
>>> tables.table_5x(api_obs=0.0, t_f_obs=135.0, commodity_type="D")
-3.1

```

---

<a id="table_6x"></a>
## `table_6x` — Tablas 6A / 6B / 6D

```text
table_6x(*, api_base, t_f_obs, commodity_type) -> float    # CTL, redondeado a 0.00001
```

| Parámetro | Unidad | Redondeo de entrada |
|---|---|---|
| `api_base` | °API a 60 °F | 0.1 |
| `t_f_obs` | °F | 0.1 |
| `commodity_type` | `"A"`, `"B"` o `"D"` | — |

> `📗 Tabla 6A · pág. PDF 148` `📗 Tabla 6B · pág. PDF 149` `📗 Tabla 6D · pág. PDF 151`

```python
>>> tables.table_6x(api_base=95.0, t_f_obs=120.0, commodity_type="A")
0.94671
>>> tables.table_6x(api_base=95.0, t_f_obs=120.0, commodity_type="B")
0.94615
>>> tables.table_6x(api_base=35.0, t_f_obs=120.0, commodity_type="D")
0.97517

```

> `⚠️ Error` Fuera del rango de la tabla (6A: −10 a 100 °API):

```python
>>> tables.table_6x(api_base=100.5, t_f_obs=100, commodity_type="A")
Traceback (most recent call last):
    ...
api_mpms.exceptions.validation.MPMSRangeError: rho_60 609.31... kg/m3 out of range for commodity type A (610.6 to 1163.5 kg/m3)

```

---

<a id="table_23x"></a>
## `table_23x` — Tablas 23A / 23B / 23D

```text
table_23x(*, rel_obs, t_f_obs, commodity_type) -> float    # densidad relativa 60/60 °F, redondeada a 0.0001
```

| Parámetro | Unidad | Redondeo de entrada |
|---|---|---|
| `rel_obs` | densidad relativa observada | 0.0001 |
| `t_f_obs` | °F | 0.1 |

> `📗 Tabla 23A · pág. PDF 153` `📗 Tabla 23B · pág. PDF 155` `📗 Tabla 23D · pág. PDF 157`

```python
>>> [tables.table_23x(rel_obs=0.8270, t_f_obs=90.0, commodity_type=ct) for ct in "ABD"]
[0.8393, 0.8389, 0.8375]

```

---

<a id="table_24x"></a>
## `table_24x` — Tablas 24A / 24B / 24D

```text
table_24x(*, rel_base, t_f_obs, commodity_type) -> float   # CTL, redondeado a 0.00001
```

| Parámetro | Unidad | Redondeo de entrada |
|---|---|---|
| `rel_base` | densidad relativa 60/60 °F | 0.0001 |
| `t_f_obs` | °F | 0.1 |

> `📗 Tabla 24A · pág. PDF 159` `📗 Tabla 24B · pág. PDF 160` `📗 Tabla 24D · pág. PDF 162`

```python
>>> [tables.table_24x(rel_base=0.9250, t_f_obs=105.0, commodity_type=ct) for ct in "ABD"]
[0.98193, 0.98127, 0.98293]

```

---

<a id="table_53x"></a>
## `table_53x` — Tablas 53A / 53B / 53D

```text
table_53x(*, den_obs, t_c_obs, commodity_type) -> float    # kg/m³ a 15 °C, redondeada a 0.1
```

| Parámetro | Unidad | Redondeo de entrada |
|---|---|---|
| `den_obs` | kg/m³ observada | 0.1 |
| `t_c_obs` | °C | 0.05 |

> `📗 Tabla 53A · pág. PDF 164` `📗 Tabla 53B · pág. PDF 166` `📗 Tabla 53D · pág. PDF 168`

```python
>>> [tables.table_53x(den_obs=827.0, t_c_obs=35.0, commodity_type=ct) for ct in "ABD"]
[841.7, 841.2, 839.6]

```

---

<a id="table_54x"></a>
## `table_54x` — Tablas 54A / 54B / 54D

```text
table_54x(*, den_base, t_c_obs, commodity_type) -> float   # CTL (base 15 °C), redondeado a 0.00001
```

| Parámetro | Unidad | Redondeo de entrada |
|---|---|---|
| `den_base` | kg/m³ a 15 °C | 0.1 |
| `t_c_obs` | °C | 0.05 |

> `📗 Tabla 54A · pág. PDF 170` `📗 Tabla 54B · pág. PDF 172` `📗 Tabla 54D · pág. PDF 174`

```python
>>> [tables.table_54x(den_base=925.0, t_c_obs=40.0, commodity_type=ct) for ct in "ABD"]
[0.98196, 0.98129, 0.98295]

```

---

<a id="table_59x"></a>
## `table_59x` — Tablas 59A / 59B / 59D

```text
table_59x(*, den_obs, t_c_obs, commodity_type) -> float    # kg/m³ a 20 °C, redondeada a 0.1
```

Parámetros y redondeos iguales a [`table_53x`](#table_53x).

> `📗 Tabla 59A · pág. PDF 176` `📗 Tabla 59B · pág. PDF 178` `📗 Tabla 59D · pág. PDF 180`

```python
>>> [tables.table_59x(den_obs=827.0, t_c_obs=35.0, commodity_type=ct) for ct in "ABD"]
[838.0, 837.7, 836.5]

```

---

<a id="table_60x"></a>
## `table_60x` — Tablas 60A / 60B / 60D

```text
table_60x(*, den_base, t_c_obs, commodity_type) -> float   # CTL (base 20 °C), redondeado a 0.00001
```

Parámetros y redondeos iguales a [`table_54x`](#table_54x), con `den_base` en kg/m³ a 20 °C.

> `📗 Tabla 60A · pág. PDF 182` `📗 Tabla 60B · pág. PDF 184` `📗 Tabla 60D · pág. PDF 186`

```python
>>> [tables.table_60x(den_base=925.0, t_c_obs=40.0, commodity_type=ct) for ct in "ABD"]
[0.98561, 0.98504, 0.98635]

```

---

<a id="tablas-c"></a>
## Tablas C — aplicaciones especiales (sin densidad)

<a id="table_6c_24c"></a>
### `table_6c_24c` — Tablas 6C y 24C

```text
table_6c_24c(*, alpha_obs, t_f_obs) -> float               # CTL, redondeado a 0.00001
```

| Parámetro | Unidad | Redondeo de entrada | Rango |
|---|---|---|---|
| `alpha_obs` | °F⁻¹ | 0.0000001 | 230×10⁻⁶ a 930×10⁻⁶ |
| `t_f_obs` | °F | 0.1 | −58.0 a 302.0 |

Las tablas 6C y 24C contienen los mismos valores.

> `📗 Tabla 6C · pág. PDF 188` `📗 Tabla 24C · pág. PDF 189`

```python
>>> tables.table_6c_24c(alpha_obs=0.000470, t_f_obs=90.0)
0.98584

```

<a id="table_54c"></a>
### `table_54c` — Tabla 54C (base 15 °C)

<a id="table_60c"></a>
### `table_60c` — Tabla 60C (base 20 °C)

```text
table_54c(*, alpha_obs, t_c_obs) -> float                  # CTL, redondeado a 0.00001
table_60c(*, alpha_obs, t_c_obs) -> float
```

| Parámetro | Unidad | Redondeo de entrada | Rango |
|---|---|---|---|
| `alpha_obs` | **°C⁻¹** | 0.0000002 | 414×10⁻⁶ a 1674×10⁻⁶ |
| `t_c_obs` | °C | 0.05 | −50.00 a 150.00 |

> `📗 Tabla 54C · pág. PDF 191` `📗 Tabla 60C · pág. PDF 192`

```python
>>> tables.table_54c(alpha_obs=0.000900, t_c_obs=35.0)
0.98192
>>> tables.table_60c(alpha_obs=0.000900, t_c_obs=35.0)
0.98636

```

> `🔁 Conversión: α °F⁻¹ → °C⁻¹` Si su α está en °F⁻¹, convierta con [`alpha_f_to_alpha_c`](06_ref_conversiones.md#alpha_f_to_alpha_c) antes de llamar a `table_54c` o `table_60c`.

---

<a id="ctl_observed"></a>
## CTL directo desde la densidad observada

Cuando se tiene la densidad **observada** y se quiere el CTL, la norma lo obtiene directamente del procedimiento de corrección; **no** encadena dos tablas redondeando la densidad base intermedia. Estas funciones hacen exactamente eso, con entradas y salida redondeadas como las tablas:

| Función | Entradas | Base | Equivale a |
|---|---|---|---|
| `ctl_from_observed_api(*, api_obs, t_f_obs, commodity_type)` | °API, °F | 60 °F | [`correct_observed_to_base`](03_ref_correcciones_60f.md#correct_observed_to_base) con P = 0 |
| `ctl_from_observed_relative_density(*, rel_obs, t_f_obs, commodity_type)` | densidad relativa, °F | 60 °F | ídem |
| `ctl_from_observed_density_15c(*, den_obs, t_c_obs, commodity_type)` | kg/m³, °C | 15 °C | [`correct_metric_observed_to_base`](04_ref_correcciones_metricas.md#correct_metric_observed_to_base) con P = 0 |
| `ctl_from_observed_density_20c(*, den_obs, t_c_obs, commodity_type)` | kg/m³, °C | 20 °C | ídem |

> `📘 Norma 11.1.6.2 · Ej. 4 · pág. PDF 64` (mismos datos de entrada, a presión 0)

```python
>>> tables.ctl_from_observed_api(api_obs=41.4, t_f_obs=72.0, commodity_type="B")
0.99413

```

> [!WARNING]
> Buscar primero la densidad a 60 °F en la tabla 5 y luego el CTL en la tabla 6 (consulta manual en dos pasos) puede diferir hasta en el quinto decimal, porque la densidad base intermedia se redondea. Use estas funciones cuando necesite el valor normativo.

---

[⬅ Anterior: Referencia · correcciones métricas](04_ref_correcciones_metricas.md) · [Índice](README.md) · [Siguiente: Referencia · conversiones ➡](06_ref_conversiones.md)
