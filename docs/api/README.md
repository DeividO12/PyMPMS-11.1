# Documentación API — `api_mpms`

Guía para **integrar** la librería en una aplicación: qué funciones existen, qué reciben, qué devuelven, qué errores lanzan y cómo usarlas en cada caso. No explica cómo se calcula internamente cada factor; para eso está la norma.

| | |
|---|---|
| **Versión** | 0.2.0 |
| **Norma** | API MPMS Capítulo 11.1 (2004) — *Temperature and Pressure Volume Correction Factors for Generalized Crude Oils, Refined Products, and Lubricating Oils* |
| **Paquete** | distribución `pympms-11-1` · import `api_mpms` |
| **Python** | 3.9 o superior (probado en 3.9, 3.12 y 3.13) |
| **Dependencias** | Ninguna para la librería. `numpy` y `pandas` solo para el [generador de tablas](10_generador_tablas.md). |

---

## 📑 Tabla de contenido

1. [Requisitos e instalación](#instalacion)
2. [Inicio rápido](#inicio-rapido)
3. [¿Qué función necesito?](#selector)
4. [Mapa de la documentación](#mapa)
5. [Etiquetas usadas en los ejemplos](#etiquetas)
6. [Cómo se verifican los ejemplos](#verificacion)

---

<a id="instalacion"></a>
## 1. Requisitos e instalación

| Requisito | Detalle |
|---|---|
| Python | ≥ 3.9 |
| Sistema operativo | Cualquiera (Windows, Linux, macOS) |
| Dependencias de ejecución | Ninguna (solo biblioteca estándar) |
| Extra `tables` | `numpy ≥ 1.24`, `pandas ≥ 2.0` — solo para `scripts/generate_tables.py` |

Desde una copia del repositorio (la librería es de uso interno y no está publicada en PyPI):

```bash
pip install .                 # solo la librería
pip install ".[tables]"       # + generador de tablas CSV
```

Comprobación:

```python
>>> import api_mpms
>>> api_mpms.__version__
'0.2.0'

```

---

<a id="inicio-rapido"></a>
## 2. Inicio rápido

Corregir a condiciones base (60 °F, 0 psig) un crudo medido a 80.3 °F con densidad observada de 823.7 kg/m³, y obtener el volumen a 60 °F de 1000 bbl observados.

> `📘 Norma 11.1.6.2 · Ej. 1 · pág. PDF 61`

```python
>>> from api_mpms import correct_observed_to_base
>>> res = correct_observed_to_base(rho_o=823.7, t_o=80.3, p_o=-5, commodity_type="A")
>>> res.ctpl_rounded                    # factor de corrección (VCF) a usar
0.98997
>>> round(res.rho_60, 6)                # densidad a 60 °F, kg/m³
832.048516
>>> round(1000 * res.ctpl_rounded, 2)   # volumen a 60 °F
989.97

```

| Magnitud | Resultado | Valor impreso en la norma |
|---|---|---|
| ρ60 | 832.048516… kg/m³ | 832.048516184234 |
| CTPL redondeado | 0.98997 | 0.98997 |
| Volumen a 60 °F | 989.97 | 989.97 |

> [!NOTE]
> La presión negativa (−5 psig) se toma como 0 psig, como indica la norma. Ver [Conceptos › Presión](01_conceptos.md#presion).

---

<a id="selector"></a>
## 3. ¿Qué función necesito?

| Tengo… | Quiero… | Función | Guía |
|---|---|---|---|
| Densidad, API o densidad relativa **observada** · °F · psig | Factores y densidad a **60 °F** | [`correct_observed_to_base`](03_ref_correcciones_60f.md#correct_observed_to_base) | [G1](02_guias.md#g1)–[G5](02_guias.md#g5) |
| Densidad o API **a 60 °F** · °F · psig | Factores y densidad a **otra temperatura/presión** | [`correct_base_to_alternate`](03_ref_correcciones_60f.md#correct_base_to_alternate) | [G6](02_guias.md#g6) |
| Densidad **observada** · °F · psig | Pasar de unas condiciones de operación a otras | [`correct_observed_to_alternate`](03_ref_correcciones_60f.md#correct_observed_to_alternate) | [G7](02_guias.md#g7) |
| Densidad **observada** · °C · kPa o bar | Factores y densidad a **15 °C o 20 °C** | [`correct_metric_observed_to_base`](04_ref_correcciones_metricas.md#correct_metric_observed_to_base) | [G8](02_guias.md#g8) |
| Densidad **a 15 °C o 20 °C** · °C · kPa o bar | Factores y densidad a **otra temperatura/presión** | [`correct_metric_base_to_alternate`](04_ref_correcciones_metricas.md#correct_metric_base_to_alternate) | [G9](02_guias.md#g9) |
| Coeficiente α60 (producto especial, sin densidad) | Solo CTL | [`ctl_from_alpha`](03_ref_correcciones_60f.md#ctl_from_alpha) o [tablas C](05_ref_tablas.md#tablas-c) | [G10](02_guias.md#g10) |
| Un valor “de tabla” (5A, 6B, 54D, 60C…) | El mismo número que la tabla impresa | [`api_mpms.tables`](05_ref_tablas.md) | [G11](02_guias.md#g11) |
| API, densidad relativa, °C, kPa, bar, α en °C⁻¹ | Convertir a las unidades que pide la función | [`api_mpms.conversions`](06_ref_conversiones.md) | — |

---

<a id="mapa"></a>
## 4. Mapa de la documentación

| # | Documento | Contenido |
|:---:|---|---|
| 01 | [Conceptos y convenciones](01_conceptos.md) | Tipos de producto, unidades, resultados, redondeo, volúmenes, presión |
| 02 | [Guías por caso de uso](02_guias.md) | Recetas paso a paso por producto y sistema de unidades |
| 03 | [Referencia · correcciones a 60 °F](03_ref_correcciones_60f.md) | `correct_observed_to_base`, `correct_base_to_alternate`, `correct_observed_to_alternate`, `ctl_from_alpha` |
| 04 | [Referencia · correcciones métricas](04_ref_correcciones_metricas.md) | `correct_metric_observed_to_base`, `correct_metric_base_to_alternate` |
| 05 | [Referencia · tablas](05_ref_tablas.md) | `api_mpms.tables`: tablas 5, 6, 23, 24, 53, 54, 59, 60 y C |
| 06 | [Referencia · conversiones](06_ref_conversiones.md) | `api_mpms.conversions`: densidad, temperatura, presión, α, Fp, redondeo |
| 07 | [Referencia · resultados](07_ref_resultados.md) | Campos y unidades de cada tipo de resultado |
| 08 | [Errores](08_errores.md) | Excepciones, cuándo ocurren y cómo manejarlas |
| 09 | [Límites y unidades](09_limites.md) | Rangos admitidos por función y por tabla |
| 10 | [Generador de tablas](10_generador_tablas.md) | Generar tablas completas en CSV |

---

<a id="etiquetas"></a>
## 5. Etiquetas usadas en los ejemplos

| Etiqueta | Significado |
|---|---|
| `📘 Norma 11.1.x · Ej. n · pág. PDF p` | Ejemplo resuelto de API MPMS 11.1; los valores esperados son los impresos en esa página del PDF |
| `📗 Tabla 6A · pág. PDF p` | Valor de una tabla de muestra impresa en la norma |
| `🔁 Conversión: X → Y` | El ejemplo necesita convertir unidades; el enlace lleva a la función de [conversiones](06_ref_conversiones.md) |
| `📐 Redondeo` | El ejemplo redondea un valor según 11.1.5.4 (ver [`api_round`](06_ref_conversiones.md#api_round)) |
| `⚠️ Error` | El ejemplo muestra una condición de error (ver [Errores](08_errores.md)) |

---

<a id="verificacion"></a>
## 6. Cómo se verifican los ejemplos

Todos los bloques de código con `>>>` de esta documentación se ejecutan como pruebas automáticas (doctest) junto con la suite de la librería:

```bash
pytest
```

Si una función cambia y un ejemplo deja de producir el resultado documentado, la suite falla. Los valores sin redondear se muestran con `round(…, n)` para que la comparación no dependa de la plataforma.
