# 09 · Límites y unidades

[⬅ Anterior: Errores](08_errores.md) · [Índice](README.md) · [Siguiente: Generador de tablas ➡](10_generador_tablas.md)

Rangos que acepta cada función. Fuera de ellos se lanza [`MPMSRangeError`](08_errores.md#range): la norma no extrapola.

## 📑 Contenido

1. [Límites generales (11.1.2.3)](#generales)
2. [Densidad por tipo de producto](#densidad)
3. [Equivalencias en otras unidades](#equivalencias)
4. [Rangos de las tablas](#tablas)

---

<a id="generales"></a>
## 1. Límites generales (11.1.2.3)

| Magnitud | Límite | Equivalencias | Fuera de límite |
|---|---|---|---|
| Temperatura | −58.0 a 302.0 °F | −50.00 a 150.00 °C | `MPMSRangeError` |
| Presión | 0 a 1500 psig | 0 a 10 342.1 kPa · 0 a 103.421 bar | < 0 → se toma como 0 · > 1500 psig → `MPMSRangeError` |
| α60 (tipo C) | 230.0×10⁻⁶ a 930.0×10⁻⁶ °F⁻¹ | 414.0×10⁻⁶ a 1674.0×10⁻⁶ °C⁻¹ | `MPMSRangeError` |
| Temperatura base métrica | 15 °C o 20 °C | — | `MPMSValidationError` |

Todos los límites son **inclusivos**: −58.0 °F, 302.0 °F, 1500 psig, etc. son válidos.

---

<a id="densidad"></a>
## 2. Densidad por tipo de producto

| Tipo | Densidad a 60 °F (ρ60) | Densidad observada (ρo) |
|:---:|---|---|
| A — crudos | 610.6 – 1163.5 kg/m³ | 470.5 – 1201.8 kg/m³ |
| B — productos refinados | 610.6 – 1163.5 kg/m³ | 470.4 – 1209.5 kg/m³ |
| C — aplicaciones especiales | Sin límite (> 0) | Sin límite (> 0) |
| D — lubricantes | 800.9 – 1163.5 kg/m³ | 714.3 – 1208.3 kg/m³ |

| Función | Qué densidad se valida |
|---|---|
| [`correct_base_to_alternate`](03_ref_correcciones_60f.md#correct_base_to_alternate) | ρ60 de entrada |
| [`correct_observed_to_base`](03_ref_correcciones_60f.md#correct_observed_to_base), [`correct_observed_to_alternate`](03_ref_correcciones_60f.md#correct_observed_to_alternate) | ρo de entrada **y** la ρ60 resultante |
| [`correct_metric_observed_to_base`](04_ref_correcciones_metricas.md#correct_metric_observed_to_base) | ρo de entrada **y** la ρ60 resultante |
| [`correct_metric_base_to_alternate`](04_ref_correcciones_metricas.md#correct_metric_base_to_alternate) | La ρ60 equivalente a `rho_base` |

> [!NOTE]
> Una densidad observada dentro de su rango puede corresponder a una ρ60 fuera de límites (por ejemplo, un lubricante muy caliente). En ese caso también se lanza `MPMSRangeError`; ver el [ejemplo 17 de 11.1.7.2](04_ref_correcciones_metricas.md#correct_metric_observed_to_base).

---

<a id="equivalencias"></a>
## 3. Equivalencias en otras unidades

Valores aproximados de los límites de ρ60 en otras unidades, para validar formularios o mostrar ayudas en pantalla. **La validación oficial se hace siempre sobre ρ60 en kg/m³.** Los valores convertidos pueden quedar justo por fuera de los límites reales (11.1.2.3).

| Tipo | °API a 60 °F | Densidad relativa 60/60 °F | Densidad a 15 °C (kg/m³) | Densidad a 20 °C (kg/m³) |
|:---:|---|---|---|---|
| A | −10.0 a 100.0 | 0.6113 a 1.1646 | 611.16 a 1163.79 | 606.12 a 1161.15 |
| B | −10.0 a 100.0 | 0.6113 a 1.1646 | 611.16 a 1163.86 | 606.12 a 1160.62 |
| D | −10.0 a 45.0 | 0.8017 a 1.1646 | 801.25 a 1163.85 | 798.11 a 1160.71 |

```python
>>> from api_mpms.conversions import api_to_rho, rho_to_api, api_round
>>> round(api_to_rho(100.0), 3), round(api_to_rho(-10.0), 3)
(610.63, 1163.463)
>>> api_round(rho_to_api(800.9), 0.1)
45.0

```

---

<a id="tablas"></a>
## 4. Rangos de las tablas

Rangos de las tablas impresas de 11.1.8. Las funciones de [`api_mpms.tables`](05_ref_tablas.md) aceptan cualquier valor que cumpla los [límites generales](#generales) y los de [densidad](#densidad); estos son los rangos que usa el [generador](10_generador_tablas.md).

| Tabla | Columna (entrada) | Rango | Incremento | Temperatura |
|---|---|---|---|---|
| 5A | °API observada | −13.4 a 168.9 | 0.1 | −58.0 a 302.0 °F, Δ 0.1 |
| 5B | °API observada | −14.2 a 168.9 | 0.1 | ídem |
| 5D | °API observada | −14.1 a 66.3 | 0.1 | ídem |
| 6A, 6B | °API a 60 °F | −10.0 a 100.0 | 0.1 | ídem |
| 6D | °API a 60 °F | −10.0 a 45.0 | 0.1 | ídem |
| 23A | Densidad relativa observada | 0.4710 a 1.1989 | 0.0001 | ídem |
| 23B | Densidad relativa observada | 0.4709 a 1.2065 | 0.0001 | ídem |
| 23D | Densidad relativa observada | 0.7151 a 1.2053 | 0.0001 | ídem |
| 24A, 24B | Densidad relativa 60/60 °F | 0.6113 a 1.1646 | 0.0001 | ídem |
| 24D | Densidad relativa 60/60 °F | 0.8017 a 1.1646 | 0.0001 | ídem |
| 53A, 59A | Densidad observada (kg/m³) | 470.6 a 1197.7 | 0.1 | −50.00 a 150.00 °C, Δ 0.05 |
| 53B, 59B | Densidad observada (kg/m³) | 470.5 a 1205.4 | 0.1 | ídem |
| 53D, 59D | Densidad observada (kg/m³) | 714.5 a 1204.1 | 0.1 | ídem |
| 54A | Densidad a 15 °C (kg/m³) | 611.2 a 1163.7 | 0.1 | ídem |
| 54B | Densidad a 15 °C (kg/m³) | 611.2 a 1163.8 | 0.1 | ídem |
| 54D | Densidad a 15 °C (kg/m³) | 801.3 a 1163.8 | 0.1 | ídem |
| 60A | Densidad a 20 °C (kg/m³) | 606.2 a 1161.1 | 0.1 | ídem |
| 60B | Densidad a 20 °C (kg/m³) | 606.2 a 1160.6 | 0.1 | ídem |
| 60D | Densidad a 20 °C (kg/m³) | 798.2 a 1160.7 | 0.1 | ídem |
| 6C, 24C | α60 (°F⁻¹) | 230.0×10⁻⁶ a 930.0×10⁻⁶ | 0.1×10⁻⁶ | −58.0 a 302.0 °F, Δ 0.1 |
| 54C, 60C | α60 (°C⁻¹) | 414.0×10⁻⁶ a 1674.0×10⁻⁶ | 0.2×10⁻⁶ | −50.00 a 150.00 °C, Δ 0.05 |

En las tablas 5, 23, 53 y 59 (densidad observada) no todas las combinaciones de densidad y temperatura tienen valor: si la densidad base resultante queda fuera de límites, la celda está vacía en la tabla impresa y la función lanza `MPMSRangeError`.

---

[⬅ Anterior: Errores](08_errores.md) · [Índice](README.md) · [Siguiente: Generador de tablas ➡](10_generador_tablas.md)
