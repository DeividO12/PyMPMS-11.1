# 02 · Guías por caso de uso

[⬅ Anterior: Conceptos](01_conceptos.md) · [Índice](README.md) · [Siguiente: Referencia · correcciones a 60 °F ➡](03_ref_correcciones_60f.md)

Recetas para los casos habituales de medición. Todas usan un ejemplo resuelto de la norma, de modo que el resultado esperado es verificable.

## 📑 Contenido

**Sistema °F / psig (base 60 °F)**

| Guía | Producto | Dato de entrada | Etiquetas |
|---|---|---|---|
| [G1](#g1) | Crudo (A) | Densidad observada en kg/m³ | `📘` |
| [G2](#g2) | Crudo (A) | Densidad relativa observada | `📘` `🔁` `📐` |
| [G3](#g3) | Producto refinado (B) | °API observada | `📘` `🔁` `📐` |
| [G4](#g4) | Lubricante (D) | °API observada | `📘` `🔁` |
| [G5](#g5) | Aplicación especial (C) | Densidad observada + α60 | `📘` |
| [G6](#g6) | Crudo (A) | °API a 60 °F → condiciones de operación | `📘` `🔁` |
| [G7](#g7) | Producto refinado (B) | De unas condiciones de operación a otras | `📘` `🔁` |

**Sistema métrico (base 15 °C o 20 °C)**

| Guía | Producto | Dato de entrada | Etiquetas |
|---|---|---|---|
| [G8](#g8) | B y D | Densidad observada, presión en kPa o bar → 15 °C | `📘` |
| [G9](#g9) | Crudo (A) | Densidad a 15 °C o 20 °C → condiciones de línea | `📘` |
| [G10](#g10) | Aplicación especial (C) | α60 en °F⁻¹ con funciones métricas; CTL sin densidad | `📘` `🔁` |

**Otros**

| Guía | Tema |
|---|---|
| [G11](#g11) | Obtener el valor de una tabla impresa (6A, 54B, 60C…) |
| [G12](#g12) | Manejo de errores en la integración |

---

<a id="g1"></a>
## G1 · Crudo con densidad observada (kg/m³) → 60 °F

> `📘 Norma 11.1.6.2 · Ej. 1 · pág. PDF 61`

**Datos:** crudo (A), densidad observada 823.7 kg/m³, 80.3 °F, −5 psig, 1000 bbl observados.

```python
>>> from api_mpms import correct_observed_to_base
>>> res = correct_observed_to_base(rho_o=823.7, t_o=80.3, p_o=-5, commodity_type="A")
>>> res.ctpl_rounded
0.98997
>>> round(1000 * res.ctpl_rounded, 2)     # bbl a 60 °F
989.97
>>> round(res.rho_60, 6), round(res.ctl, 9), res.cpl
(832.048516, 0.989966311, 1.0)

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρ60 (kg/m³) | 832.048516… | 832.048516184234 |
| CTL | 0.989966311… | 0.989966310837 |
| CPL | 1.0 (−5 psig se toma como 0) | 1.000000000000 |
| CTPL redondeado | 0.98997 | 0.98997 |
| Volumen a 60 °F | 989.97 | 989.97 |

Referencia: [`correct_observed_to_base`](03_ref_correcciones_60f.md#correct_observed_to_base).

---

<a id="g2"></a>
## G2 · Crudo con densidad relativa observada → 60 °F

> `📘 Norma 11.1.6.2 · Ej. 2 · pág. PDF 62` `🔁 Conversión: densidad relativa → kg/m³` `📐 Redondeo`

**Datos:** crudo (A), densidad relativa observada 0.72332, −57.95 °F, 113.5 psig, 637 483 bbl.

1. Convertir la densidad relativa a kg/m³ con [`gamma_t_to_rho`](06_ref_conversiones.md#gamma_t_to_rho).
2. Corregir a 60 °F.
3. (Opcional) Reportar la densidad relativa a 60 °F con [`rho_to_gamma_t`](06_ref_conversiones.md#rho_to_gamma_t) y redondearla con [`api_round`](06_ref_conversiones.md#api_round) (δ = 0.0001).

```python
>>> from api_mpms import correct_observed_to_base
>>> from api_mpms.conversions import gamma_t_to_rho, rho_to_gamma_t, api_round
>>> rho_o = gamma_t_to_rho(0.72332)
>>> rho_o
722.60825312
>>> res = correct_observed_to_base(rho_o=rho_o, t_o=-57.95, p_o=113.5, commodity_type="A")
>>> res.ctpl_rounded
1.08918
>>> round(637483 * res.ctpl_rounded, 5)
694333.73394
>>> api_round(rho_to_gamma_t(res.rho_60), 0.0001)     # densidad relativa 60/60 °F
0.6641

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρo (kg/m³) | 722.60825312 | 722.608253120000 |
| ρ60 (kg/m³) | 663.445062852… | 663.445062852402 |
| CPL | 1.000685370 | 1.000685369884 |
| CTPL redondeado | 1.08918 | 1.08918 |
| Volumen a 60 °F | 694 333.73394 | 694 333.73394 |

---

<a id="g3"></a>
## G3 · Producto refinado con °API observada → 60 °F

> `📘 Norma 11.1.6.2 · Ej. 4 · pág. PDF 64` `🔁 Conversión: °API → kg/m³ → °API` `📐 Redondeo`

**Datos:** producto refinado (B), 41.4 °API observada, 72 °F, 375 psig, 200.5 bbl.

```python
>>> from api_mpms import correct_observed_to_base
>>> from api_mpms.conversions import api_to_rho, rho_to_api, api_round
>>> res = correct_observed_to_base(rho_o=api_to_rho(41.4), t_o=72, p_o=375, commodity_type="B")
>>> res.ctpl_rounded
0.99624
>>> round(200.5 * res.ctpl_rounded, 6)
199.74612
>>> round(res.rho_60, 6)
820.670624
>>> api_round(rho_to_api(res.rho_60), 0.1)              # °API a 60 °F para el reporte
40.8

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρo (kg/m³) | 817.586836… ([`api_to_rho`](06_ref_conversiones.md#api_to_rho)) | 817.586836321573 |
| ρ60 (kg/m³) | 820.670624… | 820.670624131605 |
| CPL | 1.002151908 | 1.002151908149 |
| CTPL redondeado | 0.99624 | 0.99624 |
| Volumen a 60 °F | 199.74612 | 199.74612 |

> [!TIP]
> Para productos B la librería elige el subgrupo (gasolinas, zona de transición, jet o fuel oils) según la densidad, y puede cambiarlo durante el cálculo. El integrador solo indica `"B"`.

---

<a id="g4"></a>
## G4 · Lubricante con °API observada → 60 °F

> `📘 Norma 11.1.6.2 · Ej. 8 · pág. PDF 68` `🔁 Conversión: °API → kg/m³`

**Datos:** aceite lubricante (D), 23.6 °API observada, 78.7 °F, 128 psig, 2500 bbl.

```python
>>> from api_mpms import correct_observed_to_base
>>> from api_mpms.conversions import api_to_rho
>>> res = correct_observed_to_base(rho_o=api_to_rho(23.6), t_o=78.7, p_o=128, commodity_type="D")
>>> res.ctpl_rounded
0.99343
>>> round(2500 * res.ctpl_rounded, 4)
2483.575
>>> round(res.rho_60, 6)
917.44243

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρ60 (kg/m³) | 917.442430… | 917.442430351448 |
| CTPL redondeado | 0.99343 | 0.99343 |
| Volumen a 60 °F | 2483.575 | 2483.575 |

> [!WARNING]
> Los lubricantes solo admiten densidades a 60 °F desde **800.9 kg/m³**, es decir, como máximo ≈ 45.0 °API. Ver [Límites](09_limites.md).

---

<a id="g5"></a>
## G5 · Aplicación especial (tipo C) con α60 → 60 °F

> `📘 Norma 11.1.6.2 · Ej. 7 · pág. PDF 67`

**Datos:** producto especial con α60 = 0.00057634 °F⁻¹, densidad observada 853.7 kg/m³, 84.5 °F, 573 psig, 5000 bbl.

Se informa `alpha_60` en lugar de `commodity_type` (o junto con `commodity_type="C"`):

```python
>>> res = correct_observed_to_base(rho_o=853.7, t_o=84.5, p_o=573, alpha_60=0.00057634)
>>> res.ctpl_rounded
0.98876
>>> round(5000 * res.ctpl_rounded, 4)
4943.8
>>> round(res.rho_60, 6)
863.403099

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρ60 (kg/m³) | 863.403099… | 863.403098613648 |
| CTL | 0.985817858 | 0.985817857839 |
| CPL | 1.002986292 | 1.002986291965 |
| CTPL redondeado | 0.98876 | 0.98876 |

> [!NOTE]
> Con presión distinta de 0 la densidad es obligatoria, porque se necesita para el factor de presión. Si solo necesita CTL a presión 0, use [`ctl_from_alpha`](03_ref_correcciones_60f.md#ctl_from_alpha) ([G10](#g10)).

---

<a id="g6"></a>
## G6 · Crudo: de 60 °F a condiciones de operación

> `📘 Norma 11.1.6.1 · Ej. 1 · pág. PDF 44` `🔁 Conversión: °API → kg/m³`

**Datos:** crudo (A) de 17.785 °API a 60 °F, en un tanque a −27.7 °F y 0 psig. Volumen medido a esas condiciones: 987.99 bbl.

```python
>>> from api_mpms import correct_base_to_alternate
>>> from api_mpms.conversions import api_to_rho
>>> alt = correct_base_to_alternate(rho_60=api_to_rho(17.785), t_f=-27.7, p_psig=0, commodity_type="A")
>>> alt.ctpl_rounded
1.03301
>>> round(alt.rho, 6)                                  # densidad a −27.7 °F, kg/m³
978.178034
>>> round(987.99 * alt.ctpl_rounded, 7)                # volumen a 60 °F
1020.6035499
>>> round(1020.6035499 / alt.ctpl_rounded, 4)          # y de vuelta: volumen a −27.7 °F
987.99

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρ60 (kg/m³) | 946.918739… ([`api_to_rho`](06_ref_conversiones.md#api_to_rho)) | 946.918739324112 |
| ρ a −27.7 °F (kg/m³) | 978.178034… | 978.178034364 |
| α60 (°F⁻¹) | 0.000380407 | 0.000380407044 |
| CTL | 1.033011592 | 1.033011591958 |
| CTPL redondeado | 1.03301 | 1.03301 |

---

<a id="g7"></a>
## G7 · Producto refinado: de unas condiciones de operación a otras

> `📘 Norma 11.1.6.3 · Ej. 3 · pág. PDF 76` `🔁 Conversión: densidad relativa → kg/m³`

**Datos:** producto refinado (B) con densidad relativa observada 0.8665 a 68.02 °F y 11 psig; 285.45 bbl. Se quiere el volumen a 150.3 °F y 534 psig.

```python
>>> from api_mpms import correct_observed_to_alternate
>>> from api_mpms.conversions import gamma_t_to_rho
>>> res = correct_observed_to_alternate(
...     rho_o=gamma_t_to_rho(0.8665), t_o=68.02, p_o=11,
...     t_f=150.3, p_psig=534, commodity_type="B",
... )
>>> res.observed.ctpl_rounded, res.alternate.ctpl_rounded
(0.99645, 0.96228)
>>> v60 = round(285.45 * res.observed.ctpl_rounded, 7)
>>> v60                                                # volumen a 60 °F
284.4366525
>>> round(v60 / res.alternate.ctpl_rounded, 6)         # volumen a 150.3 °F y 534 psig
295.586163
>>> round(res.alternate.rho, 6)                        # densidad a 150.3 °F y 534 psig
835.963129

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρ60 (kg/m³) | 868.730481… | 868.730481427765 |
| CTPL observado (redondeado) | 0.99645 | 0.99645 |
| CTPL alterno (redondeado) | 0.96228 | 0.96228 |
| Volumen a 60 °F | 284.4366525 | 284.4366525 |
| ρ alterna (kg/m³) | 835.963129… | 835.963128925946 |

---

<a id="g8"></a>
## G8 · Sistema métrico: densidad observada → 15 °C

### Presión en kPa · producto refinado (B)

> `📘 Norma 11.1.7.2 · Ej. 1 · pág. PDF 104`

**Datos:** 721.1 kg/m³ a 82.35 °C y 10 005 kPa; 10 000 m³ observados; base 15 °C.

```python
>>> from api_mpms import correct_metric_observed_to_base
>>> res = correct_metric_observed_to_base(
...     rho_o=721.1, t_o_c=82.35, p_o=10005, pressure_unit="kPa",
...     t_base_c=15, commodity_type="B",
... )
>>> res.ctpl_rounded
0.93547
>>> round(10000 * res.ctpl_rounded, 1)        # m³ a 15 °C
9354.7
>>> round(res.rho_base, 6)                    # densidad a 15 °C
770.84278
>>> round(res.fp, 9)                          # Fp en kPa⁻¹ (unidad de la presión de entrada)
0.156160024

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρ15 (kg/m³) | 770.842780… | 770.842780077632 |
| CTL | 0.920854016 | 0.920854015583 |
| Fp (kPa⁻¹) | 0.156160024 | 0.156160024039 |
| CTPL redondeado | 0.93547 | 0.93547 |
| Volumen a 15 °C | 9354.7 | 9354.7 |

### Presión en bar · lubricante (D)

> `📘 Norma 11.1.7.2 · Ej. 9 · pág. PDF 112`

```python
>>> from api_mpms import correct_metric_observed_to_base
>>> res = correct_metric_observed_to_base(
...     rho_o=1204.6, t_o_c=-49.97, p_o=31.1, pressure_unit="bar",
...     t_base_c=15, commodity_type="D",
... )
>>> res.ctpl_rounded, round(100 * res.ctpl_rounded, 2)
(1.0357, 103.57)
>>> round(res.fp, 9)                          # Fp en bar⁻¹
3.188159805

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρ15 (kg/m³) | 1163.078239… | 1163.078239292499 |
| Fp (bar⁻¹) | 3.188159805 | 3.188159804848 |
| CTPL redondeado | 1.0357 | 1.0357 |

> [!TIP]
> No convierta la presión a psig: pase el valor tal como lo mide el instrumento e indique la unidad. `fp` se devuelve en la misma unidad (kPa⁻¹ o bar⁻¹).

---

<a id="g9"></a>
## G9 · Sistema métrico: densidad a 15 °C o 20 °C → condiciones de línea

> `📘 Norma 11.1.7.1 · Ej. 1 · pág. PDF 92` `📘 Norma 11.1.7.1 · Ej. 2 · pág. PDF 93`

**Datos:** crudo (A) con densidad 772.3 kg/m³ a la temperatura base, en línea a −32.8 °C y 24.6 bar.

```python
>>> from api_mpms import correct_metric_base_to_alternate
>>> res15 = correct_metric_base_to_alternate(
...     rho_base=772.3, t_base_c=15, t_c=-32.8, p=24.6, pressure_unit="bar", commodity_type="A",
... )
>>> res15.ctpl_rounded
1.05015
>>> round(9885 * res15.ctpl_rounded, 5)       # 9885 m³ en línea → m³ a 15 °C
10380.73275
>>> res20 = correct_metric_base_to_alternate(
...     rho_base=772.3, t_base_c=20, t_c=-32.8, p=24.65, pressure_unit="bar", commodity_type="A",
... )
>>> res20.ctpl_rounded
1.05504

```

| Magnitud | Base 15 °C (Ej. 1) | Norma | Base 20 °C (Ej. 2) | Norma |
|---|---|---|---|---|
| ρ60 (kg/m³) | 771.858050 | 771.858049874826 | 775.822888 | 775.822887700255 |
| CTL | 1.048420095 | 1.048420095319 | 1.053312668 | 1.053312668251 |
| Fp (bar⁻¹) | 6.706348860 | 6.706348860257 | 6.622983078 | 6.622983078151 |
| CTPL redondeado | 1.05015 | 1.05015 | 1.05504 | 1.05504 |

> [!NOTE]
> `res.rho` (densidad en línea) se calcula con el CTPL sin redondear (ρ = CTL · CPL · ρbase), como indica la fórmula del paso 5 de 11.1.7.1: **811.0328506** kg/m³. Los ejemplos impresos de la norma usan el CTPL redondeado (772.3 × 1.05015 = **811.030845**). Si su procedimiento sigue el ejemplo impreso, calcule `rho_base * res.ctpl_rounded`.

---

<a id="g10"></a>
## G10 · Aplicación especial (C): α60 en °F⁻¹ con funciones métricas, y CTL sin densidad

### Funciones métricas con α en °F⁻¹

> `📘 Norma 11.1.7.2 · Ej. 8 · pág. PDF 111` `🔁 Conversión: α °F⁻¹ → °C⁻¹`

Las funciones métricas reciben α en **°C⁻¹** (`alpha_60_c`). Si el dato está en °F⁻¹, conviértalo con [`alpha_f_to_alpha_c`](06_ref_conversiones.md#alpha_f_to_alpha_c):

```python
>>> from api_mpms import correct_metric_observed_to_base
>>> from api_mpms.conversions import alpha_f_to_alpha_c
>>> res = correct_metric_observed_to_base(
...     rho_o=853.7, t_o_c=29.18, p_o=395, pressure_unit="kPa",
...     t_base_c=15, alpha_60_c=alpha_f_to_alpha_c(0.0005763),
... )
>>> res.ctpl_rounded
0.98553
>>> round(8501.3 * res.ctpl_rounded, 6)
8378.286189

```

| Magnitud | Resultado | Norma |
|---|---|---|
| ρ15 (kg/m³) | 866.235846… | 866.235845849433 |
| CTPL redondeado | 0.98553 | 0.98553 |
| Volumen a 15 °C | 8378.286189 | 8378.286189 |

### Solo CTL, sin densidad (presión 0)

> `📗 Tabla 6C · pág. PDF 188` `📐 Redondeo`

```python
>>> from api_mpms import ctl_from_alpha
>>> from api_mpms.conversions import api_round
>>> api_round(ctl_from_alpha(alpha_60=0.00047, t_f=90.0), 0.00001)
0.98584

```

Equivale a [`table_6c_24c`](05_ref_tablas.md#table_6c_24c) (que además redondea las entradas). Para bases métricas use [`table_54c`](05_ref_tablas.md#table_54c) o [`table_60c`](05_ref_tablas.md#table_60c).

---

<a id="g11"></a>
## G11 · Obtener el valor de una tabla impresa

> `📗 Tabla 6A · pág. PDF 148` `📗 Tabla 54B · pág. PDF 172`

Cuando el procedimiento interno exige el valor “de la tabla” (entradas y salida redondeadas):

```python
>>> from api_mpms import tables
>>> tables.table_6x(api_base=95.0, t_f_obs=120.0, commodity_type="A")       # Tabla 6A
0.94671
>>> tables.table_54x(den_base=925.0, t_c_obs=40.0, commodity_type="B")      # Tabla 54B
0.98129

```

Todas las tablas: [05 · Referencia de tablas](05_ref_tablas.md).

---

<a id="g12"></a>
## G12 · Manejo de errores en la integración

> `📘 Norma 11.1.6.2 · Ej. 15 · pág. PDF 71` `⚠️ Error`

Patrón recomendado: separar los datos fuera de rango (que el operador debe revisar) de los datos inválidos (un error del sistema que llama).

```python
>>> from api_mpms import correct_observed_to_base
>>> from api_mpms import MPMSRangeError, MPMSValidationError, MPMSConvergenceError
>>> def vcf(rho_o, t_o, p_o, commodity_type):
...     try:
...         return correct_observed_to_base(
...             rho_o=rho_o, t_o=t_o, p_o=p_o, commodity_type=commodity_type
...         ).ctpl_rounded
...     except MPMSRangeError as exc:          # fuera de los límites de la norma
...         return f"fuera de rango: {exc}"
...     except MPMSValidationError as exc:     # dato inválido (tipo, NaN, combinación)
...         return f"dato inválido: {exc}"
...     except MPMSConvergenceError as exc:    # sin convergencia (caso excepcional)
...         return f"sin convergencia: {exc}"
>>> vcf(714.015375290433, 72.32, 0, "D")      # lubricante con densidad observada < 714.3
'fuera de rango: rho_o 714.015375290433 kg/m3 out of range for commodity type D (714.3 to 1208.3 kg/m3)'
>>> vcf(823.7, 80.3, 0, "X")
"dato inválido: commodity_type must be 'A', 'B', 'C' or 'D', got 'X'"

```

> [!IMPORTANT]
> Capture `MPMSRangeError` **antes** que `MPMSValidationError`: es una subclase de esta. Detalle de cada excepción en [08 · Errores](08_errores.md).

---

[⬅ Anterior: Conceptos](01_conceptos.md) · [Índice](README.md) · [Siguiente: Referencia · correcciones a 60 °F ➡](03_ref_correcciones_60f.md)
