# 01 · Conceptos y convenciones

[⬅ Índice](README.md) · [Siguiente: Guías por caso de uso ➡](02_guias.md)

Reglas comunes a todas las funciones. Leerlas una vez evita la mayoría de errores de integración.

## 📑 Contenido

1. [Puntos de importación](#importacion)
2. [Argumentos por nombre](#argumentos)
3. [Tipos de producto (A, B, C, D)](#tipos)
4. [Sistemas de unidades](#unidades)
5. [Temperatura: ITS-90](#temperatura)
6. [Presión](#presion)
7. [Resultados](#resultados)
8. [Redondeo: qué valor usar](#redondeo)
9. [Corrección de volúmenes](#volumenes)

---

<a id="importacion"></a>
## 1. Puntos de importación

| Importar desde | Contiene | Referencia |
|---|---|---|
| `api_mpms` | Funciones de corrección, `ctl_from_alpha`, tipos de resultado, excepciones, `CommodityType` | [03](03_ref_correcciones_60f.md), [04](04_ref_correcciones_metricas.md), [07](07_ref_resultados.md), [08](08_errores.md) |
| `api_mpms.conversions` | Conversión de unidades y `api_round` | [06](06_ref_conversiones.md) |
| `api_mpms.tables` | Valores en formato de tabla (11.1.8) | [05](05_ref_tablas.md) |

> [!WARNING]
> Importe solo desde estos tres módulos. Los módulos internos (`api_mpms.mpms_11_1.*`, `api_mpms.validators`, `api_mpms.constants.*`) pueden cambiar sin aviso.

```python
>>> import api_mpms
>>> from api_mpms import correct_observed_to_base, MPMSRangeError
>>> from api_mpms.conversions import api_to_rho
>>> from api_mpms.tables import table_6x

```

---

<a id="argumentos"></a>
## 2. Argumentos por nombre

Todas las funciones públicas exigen los argumentos **por nombre**. Así no se puede pasar una temperatura donde va una presión:

```python
>>> correct_observed_to_base(823.7, 80.3, 0, "A")
Traceback (most recent call last):
    ...
TypeError: correct_observed_to_base() takes 0 positional arguments but 4 were given
>>> correct_observed_to_base(rho_o=823.7, t_o=80.3, p_o=0, commodity_type="A").ctpl_rounded
0.98997

```

Los números pueden ser `int`, `float` o tipos numéricos de NumPy. Los textos (`"823.7"`), `None`, `NaN` e infinitos se rechazan con [`MPMSValidationError`](08_errores.md#validation).

---

<a id="tipos"></a>
## 3. Tipos de producto (A, B, C, D)

Cada corrección necesita **el tipo de producto** (`commodity_type`) **o** el coeficiente de expansión térmica `alpha_60`; nunca ambos con A, B o D.

| `commodity_type` | Producto | Qué se informa | Límites de densidad a 60 °F |
|:---:|---|---|---|
| `"A"` | Crudos | `commodity_type="A"` | 610.6 – 1163.5 kg/m³ |
| `"B"` | Productos refinados (gasolinas, zona de transición, jet, fuel oils) | `commodity_type="B"`; el subgrupo se elige solo según la densidad | 610.6 – 1163.5 kg/m³ |
| `"C"` | Aplicaciones especiales (producto con α60 medido) | `alpha_60=…` (y opcionalmente `commodity_type="C"`) | Sin límite de densidad; α60 de 230×10⁻⁶ a 930×10⁻⁶ °F⁻¹ |
| `"D"` | Aceites lubricantes | `commodity_type="D"` | 800.9 – 1163.5 kg/m³ |

- No distingue mayúsculas ni espacios: `"a"`, `" B "` y `api_mpms.CommodityType.CRUDE_OIL` son válidos.
- La clasificación es **por densidad**, no por el nombre comercial del producto: un producto refinado se informa como `"B"` y la librería elige su subgrupo.

```python
>>> from api_mpms import CommodityType
>>> [ct.value for ct in CommodityType]
['a', 'b', 'c', 'd']
>>> correct_observed_to_base(rho_o=823.7, t_o=80.3, p_o=0, commodity_type=CommodityType.CRUDE_OIL).ctpl_rounded
0.98997

```

Ejemplos por tipo: [A](02_guias.md#g1) · [B](02_guias.md#g3) · [C](02_guias.md#g5) · [D](02_guias.md#g4).

---

<a id="unidades"></a>
## 4. Sistemas de unidades

Cada función trabaja en **un** sistema de unidades. Si sus datos están en otro, convierta primero con [`api_mpms.conversions`](06_ref_conversiones.md).

| Función | Densidad | Temperatura | Presión | α60 | Fp devuelto |
|---|---|---|---|---|---|
| [`correct_observed_to_base`](03_ref_correcciones_60f.md#correct_observed_to_base), [`correct_base_to_alternate`](03_ref_correcciones_60f.md#correct_base_to_alternate), [`correct_observed_to_alternate`](03_ref_correcciones_60f.md#correct_observed_to_alternate) | kg/m³ | °F | psig | °F⁻¹ | psi⁻¹ |
| [`correct_metric_observed_to_base`](04_ref_correcciones_metricas.md#correct_metric_observed_to_base), [`correct_metric_base_to_alternate`](04_ref_correcciones_metricas.md#correct_metric_base_to_alternate) | kg/m³ | °C | kPa **o** bar (`pressure_unit`) | °C⁻¹ | kPa⁻¹ o bar⁻¹ |
| [`api_mpms.tables`](05_ref_tablas.md) | °API, densidad relativa o kg/m³ (según la tabla) | °F o °C (según la tabla) | — (siempre 0) | °F⁻¹ o °C⁻¹ | — |

> [!IMPORTANT]
> La densidad siempre se pasa en **kg/m³**. Si tiene °API o densidad relativa, convierta con [`api_to_rho`](06_ref_conversiones.md#api_to_rho) o [`gamma_t_to_rho`](06_ref_conversiones.md#gamma_t_to_rho). Las tablas son la excepción: reciben directamente la unidad de la tabla impresa.

---

<a id="temperatura"></a>
## 5. Temperatura: ITS-90

Pase las temperaturas **tal como se miden hoy (escala ITS-90)**, en °F o °C según la función. La librería hace internamente el ajuste a IPTS-68 que exige la norma; el integrador **no** necesita llamar a [`its90_to_ipts68`](06_ref_conversiones.md#its90_to_ipts68).

| Unidad | Límites |
|---|---|
| °F | −58.0 a 302.0 |
| °C | −50.00 a 150.00 |

---

<a id="presion"></a>
## 6. Presión

- Siempre **manométrica** (gauge): 0 = presión atmosférica.
- Una presión **negativa se toma como 0** y el cálculo continúa (norma 11.1.6.1, paso 1).
- Máximo 1500 psig = 10 342.1 kPa = 103.421 bar. Por encima se lanza [`MPMSRangeError`](08_errores.md#range).
- En las funciones métricas la unidad es **obligatoria**: `pressure_unit="kPa"` o `pressure_unit="bar"`.

```python
>>> correct_observed_to_base(rho_o=823.7, t_o=80.3, p_o=-5, commodity_type="A").cpl
1.0

```

---

<a id="resultados"></a>
## 7. Resultados

Las funciones de corrección devuelven tuplas con nombre (`NamedTuple`). Se leen por atributo, se pueden desempaquetar o convertir a `dict` (por ejemplo, para JSON):

```python
>>> res = correct_observed_to_base(rho_o=823.7, t_o=80.3, p_o=-5, commodity_type="A")
>>> res.ctl == res[1]
True
>>> sorted(res._asdict())
['cpl', 'ctl', 'ctpl', 'ctpl_rounded', 'fp', 'iterations', 'rho_60']

```

Campos de cada tipo: [07 · Referencia de resultados](07_ref_resultados.md).

---

<a id="redondeo"></a>
## 8. Redondeo: qué valor usar

| Valor | Redondeado | Uso |
|---|:---:|---|
| `ctpl_rounded` | Sí (5 decimales) | **Factor de corrección de volumen (VCF) oficial** para reportes y liquidación |
| `ctl`, `cpl`, `ctpl`, `fp`, densidades | No | Valores de cálculo con precisión completa; la norma prohíbe redondear valores intermedios |
| Funciones de [`api_mpms.tables`](05_ref_tablas.md) | Entrada y salida redondeadas | Reproducir las tablas impresas |

- Las funciones de corrección **no redondean las entradas**. Si su procedimiento interno exige redondear una lectura, use [`api_round`](06_ref_conversiones.md#api_round).
- Para reportar una densidad o un °API con la resolución de la norma, redondee el resultado con `api_round` (ver la [guía G3](02_guias.md#g3)).

---

<a id="volumenes"></a>
## 9. Corrección de volúmenes

La librería devuelve factores; el volumen lo calcula el integrador con el **CTPL redondeado**, como en los ejemplos de la norma.

> [!IMPORTANT]
> El CTPL **siempre** convierte un volumen medido a condiciones distintas de la base (observadas o alternas) en volumen a condiciones base: **V_base = V × CTPL**. Para ir de la base a otras condiciones se **divide**.

| Función | Fórmula | Ejemplo de la norma |
|---|---|---|
| [`correct_observed_to_base`](03_ref_correcciones_60f.md#correct_observed_to_base) | `V_60 = V_observado × res.ctpl_rounded` | 11.1.6.2 Ej. 1: 1000 × 0.98997 = 989.97 |
| [`correct_base_to_alternate`](03_ref_correcciones_60f.md#correct_base_to_alternate) | `V_60 = V_alterno × res.ctpl_rounded` → `V_alterno = V_60 / res.ctpl_rounded` | 11.1.6.1 Ej. 1: 987.99 × 1.03301 = 1020.6035499 |
| [`correct_observed_to_alternate`](03_ref_correcciones_60f.md#correct_observed_to_alternate) | `V_60 = V_o × res.observed.ctpl_rounded` y `V_alterno = V_60 / res.alternate.ctpl_rounded` | 11.1.6.3 Ej. 1: 989.99 / 1.05697 = 936.63018 |
| [`correct_metric_observed_to_base`](04_ref_correcciones_metricas.md#correct_metric_observed_to_base) | `V_15 o V_20 = V_observado × res.ctpl_rounded` | 11.1.7.2 Ej. 1: 10000 × 0.93547 = 9354.7 |
| [`correct_metric_base_to_alternate`](04_ref_correcciones_metricas.md#correct_metric_base_to_alternate) | `V_15 o V_20 = V_alterno × res.ctpl_rounded` | 11.1.7.1 Ej. 1: 9885 × 1.05015 = 10380.73275 |

> `📘 Norma 11.1.6.2 · Ej. 1 · pág. PDF 61` `📘 Norma 11.1.6.1 · Ej. 1 · pág. PDF 44`

```python
>>> round(1000 * res.ctpl_rounded, 2)            # 11.1.6.2 Ej. 1: observado → 60 °F
989.97
>>> from api_mpms import correct_base_to_alternate
>>> alt = correct_base_to_alternate(rho_60=946.918739324112, t_f=-27.7, p_psig=0, commodity_type="A")
>>> round(987.99 * alt.ctpl_rounded, 7)           # 11.1.6.1 Ej. 1: 987.99 a −27.7 °F → 60 °F
1020.6035499

```

---

[⬅ Índice](README.md) · [Siguiente: Guías por caso de uso ➡](02_guias.md)
