# 06 · Referencia · conversiones (`api_mpms.conversions`)

[⬅ Anterior: Referencia · tablas](05_ref_tablas.md) · [Índice](README.md) · [Siguiente: Referencia · resultados ➡](07_ref_resultados.md)

Conversiones de unidades de API MPMS 11.1.5.1 y redondeo de 11.1.5.4. Úselas para llevar sus datos a las unidades que piden las [funciones de corrección](01_conceptos.md#unidades) y para expresar los resultados en las unidades de su reporte.

```python
>>> from api_mpms import conversions

```

## 📑 Contenido

| Grupo | Función | Conversión |
|---|---|---|
| Densidad | [`api_to_rho`](#api_to_rho) | °API → kg/m³ |
| | [`rho_to_api`](#rho_to_api) | kg/m³ → °API |
| | [`gamma_t_to_rho`](#gamma_t_to_rho) | Densidad relativa → kg/m³ |
| | [`rho_to_gamma_t`](#rho_to_gamma_t) | kg/m³ → densidad relativa |
| Temperatura | [`celsius_to_fahrenheit`](#celsius_to_fahrenheit) | °C → °F |
| | [`its90_to_ipts68`](#its90_to_ipts68) | ITS-90 → IPTS-68 (uso informativo) |
| Presión | [`pressure_to_psig`](#pressure_to_psig) | kPa o bar → psig |
| | [`fp_from_psi`](#fp_from_psi) | Fp psi⁻¹ → kPa⁻¹ o bar⁻¹ |
| Expansión térmica | [`alpha_c_to_alpha_f`](#alpha_c_to_alpha_f) | α °C⁻¹ → °F⁻¹ |
| | [`alpha_f_to_alpha_c`](#alpha_f_to_alpha_c) | α °F⁻¹ → °C⁻¹ |
| Redondeo | [`api_round`](#api_round) | Redondeo según 11.1.5.4 |

> [!NOTE]
> Todas las densidades relativas y gravedades API son **en vacío** y referidas al agua a 60 °F (999.016 kg/m³), como en la norma. Las funciones devuelven el valor **sin redondear**; para reportarlo use [`api_round`](#api_round).

---

## Densidad

<a id="api_to_rho"></a>
### `api_to_rho(api) -> float`

Gravedad API (°API) → densidad (kg/m³). **Error:** [`MPMSValidationError`](08_errores.md#validation) si `api ≤ −131.5`.

> `📘 Norma 11.1.6.1 · Ej. 1 · pág. PDF 44` `📘 Norma 11.1.6.2 · Ej. 4 · pág. PDF 64`

```python
>>> round(conversions.api_to_rho(17.785), 9)     # norma: 946.918739324112
946.918739324
>>> round(conversions.api_to_rho(41.4), 9)       # norma: 817.586836321573
817.586836322

```

Usado en: [G3](02_guias.md#g3), [G4](02_guias.md#g4), [G6](02_guias.md#g6).

<a id="rho_to_api"></a>
### `rho_to_api(rho) -> float`

Densidad (kg/m³) → gravedad API (°API). **Error:** [`MPMSValidationError`](08_errores.md#validation) si `rho ≤ 0`.

> `📘 Norma 11.1.6.1 · Ej. 1 · pág. PDF 44` `📐 Redondeo`

```python
>>> conversions.api_round(conversions.rho_to_api(946.918739324112), 0.001)
17.785

```

Para reportar °API a 60 °F con la resolución de la norma (0.1): `api_round(rho_to_api(res.rho_60), 0.1)`, ver [G3](02_guias.md#g3).

<a id="gamma_t_to_rho"></a>
### `gamma_t_to_rho(gamma_t) -> float`

Densidad relativa → densidad (kg/m³). **Error:** [`MPMSValidationError`](08_errores.md#validation) si `gamma_t ≤ 0`.

> `📘 Norma 11.1.6.2 · Ej. 2 · pág. PDF 62` `📘 Norma 11.1.6.1 · Ej. 4 · pág. PDF 47`

```python
>>> conversions.gamma_t_to_rho(0.72332)          # norma: 722.608253120000
722.60825312
>>> conversions.gamma_t_to_rho(0.7943)           # norma: 793.5184088
793.5184088

```

Usado en: [G2](02_guias.md#g2), [G7](02_guias.md#g7).

<a id="rho_to_gamma_t"></a>
### `rho_to_gamma_t(rho) -> float`

Densidad (kg/m³) → densidad relativa. **Error:** [`MPMSValidationError`](08_errores.md#validation) si `rho ≤ 0`.

> `📘 Norma 11.1.6.2 · Ej. 2 · pág. PDF 62` `📐 Redondeo`

```python
>>> conversions.api_round(conversions.rho_to_gamma_t(663.445062852402), 0.0001)
0.6641

```

---

## Temperatura

<a id="celsius_to_fahrenheit"></a>
### `celsius_to_fahrenheit(t_c) -> float`

°C → °F (t°F = 1.8 · t°C + 32). Úsela si tiene temperaturas en °C pero necesita las [funciones de base 60 °F](03_ref_correcciones_60f.md). Las [funciones métricas](04_ref_correcciones_metricas.md) ya reciben °C.

> `📘 Norma 11.1.7.1 · Ej. 1 · pág. PDF 92` `📘 Norma 11.1.7.2 · Ej. 1 · pág. PDF 104`

```python
>>> conversions.celsius_to_fahrenheit(-32.8)     # norma: −27.04
-27.04
>>> conversions.celsius_to_fahrenheit(82.35)     # norma: 180.23
180.23

```

<a id="its90_to_ipts68"></a>
### `its90_to_ipts68(*, t_f_90=None, t_c_90=None) -> float`

Convierte una temperatura de la escala ITS-90 a IPTS-68 y la devuelve en la **misma unidad** de entrada. Se da exactamente uno de los dos argumentos.

> [!NOTE]
> **El integrador no la necesita para corregir**: todas las funciones reciben temperaturas ITS-90 y hacen este ajuste internamente. Se expone para auditoría o para reproducir valores intermedios de la norma.

> `📘 Norma 11.1.6.1 · Ej. 1 · pág. PDF 44`

```python
>>> round(conversions.its90_to_ipts68(t_f_90=-27.7), 9)   # norma: −27.712499233089
-27.712499233

```

**Error:** [`MPMSValidationError`](08_errores.md#validation) si se dan ambas temperaturas o ninguna.

---

## Presión

<a id="pressure_to_psig"></a>
### `pressure_to_psig(p, unit) -> float`

Presión manométrica en kPa o bar → psig (psig = kPa / 6.894757 = bar / 0.06894757). `unit` es `"kPa"` o `"bar"` (no distingue mayúsculas). Úsela si tiene presión métrica pero necesita las [funciones de base 60 °F](03_ref_correcciones_60f.md). Las [funciones métricas](04_ref_correcciones_metricas.md) ya reciben kPa o bar.

> `📘 Norma 11.1.7.1 · Ej. 1 · pág. PDF 92` `📘 Norma 11.1.7.2 · Ej. 1 · pág. PDF 104`

```python
>>> round(conversions.pressure_to_psig(24.6, "bar"), 9)    # norma: 356.792849987316
356.792849987
>>> round(conversions.pressure_to_psig(10005, "kPa"), 8)   # norma: 1451.10262769
1451.10262769

```

**Error:** [`MPMSValidationError`](08_errores.md#validation) si `unit` no es `"kPa"` ni `"bar"`.

<a id="fp_from_psi"></a>
### `fp_from_psi(fp_psi, unit) -> float`

Factor de compresibilidad Fp en psi⁻¹ → kPa⁻¹ o bar⁻¹. Las funciones de base 60 °F devuelven `fp` en psi⁻¹; las métricas ya lo devuelven en la unidad de presión de entrada.

> `📘 Norma 11.1.7.1 · Ej. 1 · pág. PDF 92` `📘 Norma 11.1.7.2 · Ej. 1 · pág. PDF 104`

```python
>>> round(conversions.fp_from_psi(0.462386457487, "bar"), 9)    # norma: 6.706348860257
6.70634886
>>> round(conversions.fp_from_psi(1.076685418863, "kPa"), 9)    # norma: 0.156160024039
0.156160024

```

---

## Expansión térmica

<a id="alpha_c_to_alpha_f"></a>
### `alpha_c_to_alpha_f(alpha_c) -> float`

<a id="alpha_f_to_alpha_c"></a>
### `alpha_f_to_alpha_c(alpha_f) -> float`

Coeficiente de expansión térmica entre °C⁻¹ y °F⁻¹ (α°F = α°C / 1.8). Las funciones de base 60 °F reciben `alpha_60` en **°F⁻¹**; las métricas y las tablas 54C/60C, en **°C⁻¹**.

> `📘 Norma 11.1.7.1 · Ej. 7 · pág. PDF 98` (la norma da α = 0.000446759 °F⁻¹ para una función métrica)

```python
>>> conversions.alpha_f_to_alpha_c(0.000446759)
0.0008041662000000001
>>> round(conversions.alpha_c_to_alpha_f(0.0008041662), 12)
0.000446759

```

Usado en: [G10](02_guias.md#g10), [`correct_metric_base_to_alternate`](04_ref_correcciones_metricas.md#correct_metric_base_to_alternate).

---

## Redondeo

<a id="api_round"></a>
### `api_round(x, delta) -> float`

Redondea `x` al múltiplo de `delta` más cercano según 11.1.5.4. Los empates exactos (…5) se resuelven **al par**, interpretando el número como el decimal que se escribió.

| Variable | `delta` según la norma |
|---|---|
| °API | 0.1 |
| Densidad relativa | 0.0001 |
| Densidad (kg/m³) | 0.1 |
| Temperatura °F / °C | 0.1 / 0.05 |
| Presión psig / kPa / bar | 1 / 5 / 0.05 |
| α60 °F⁻¹ / °C⁻¹ | 0.0000001 / 0.0000002 |
| CTL, CPL, CTPL | 0.00001 |
| Fp psi⁻¹ / kPa⁻¹ / bar⁻¹ | 0.001 / 0.0001 / 0.01 |

> `📘 Norma 11.1.5.4 · pág. PDF 38`

```python
>>> conversions.api_round(5.34, 0.05)
5.35
>>> conversions.api_round(-5.34, 0.05)
-5.35
>>> conversions.api_round(10.05, 0.1)         # empate: se redondea al par
10.0
>>> conversions.api_round(10.15, 0.1)
10.2

```

**Errores:** [`MPMSValidationError`](08_errores.md#validation) si `x` no es finito o `delta ≤ 0`.

> [!TIP]
> Las funciones de corrección ya devuelven `ctpl_rounded`; no hace falta redondear el CTPL a mano.

---

[⬅ Anterior: Referencia · tablas](05_ref_tablas.md) · [Índice](README.md) · [Siguiente: Referencia · resultados ➡](07_ref_resultados.md)
