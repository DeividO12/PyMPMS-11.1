# 10 · Conformidad con API MPMS 11.1 (2004)

[⬅ Anterior: Plan de acción](09_plan_de_accion.md) · [Índice](README.md) · [Siguiente: Anexo A — Núcleo ➡](11_anexo_norma_nucleo.md)

La auditoría de integridad se corrigió verificando **en paralelo** cada cambio contra la norma (`PDFs/API MPMS 11.1.pdf`). Este documento resume el resultado. El detalle de cada punto, con página, fórmula y cita, está en los anexos [A (núcleo)](11_anexo_norma_nucleo.md) y [B (tablas)](12_anexo_norma_tablas.md).

## 📑 Contenido

1. [Resultado global](#resultado-global)
2. [Evidencia numérica](#evidencia-numérica)
3. [Estado de los puntos del núcleo (NORM-01 … NORM-29)](#estado-núcleo)
4. [Estado de los puntos de tablas (NORM-T01 … NORM-T17)](#estado-tablas)
5. [Decisiones tomadas](#decisiones)
6. [Pendientes](#pendientes)

---

<a id="resultado-global"></a>
## 1. Resultado global

| Aspecto | Antes (`4f1216d`) | Ahora (`1.0.0`) |
|---|---|---|
| Ecuaciones (ITS-90, ρ*, α60, CTL, Fp, CPL, Newton) | ✅ Conformes | ✅ Conformes, sin cambios numéricos |
| Validación de límites (ρ60, ρo, α60, t, P) | ❌ Extrapolaba densidad y α | ✅ Error de rango, sin extrapolar |
| Redondeo (11.1.5.4 y 11.1.3.9) | ❌ Empates mal resueltos; CTPL nunca redondeado | ✅ Decimal exacto; `ctpl_rounded` como salida final |
| Unidades métricas (11.1.7) | ❌ Presión tomada como psig | ✅ kPa o bar; Fp en kPa⁻¹/bar⁻¹ |
| Tablas (11.1.8) | ❌ 23A inválida; funciones combinadas no normativas; tablas C sin redondear α | ✅ 28 tablas conformes |
| Errores | ❌ Fuera de rango reportado como no convergencia | ✅ `MPMSRangeError` / `MPMSConvergenceError` (con última iteración) |

> [!IMPORTANT]
> El núcleo matemático ya era correcto: reproducía todos los ejemplos con cálculo. Las correcciones normativas están en la **frontera** del cálculo: qué entradas se aceptan, en qué unidades, qué se redondea y qué error se informa. Los cálculos válidos de 6.1 y 6.2 no cambian.

---

<a id="evidencia-numérica"></a>
## 2. Evidencia numérica

| Conjunto | Casos | Resultado actual | Prueba |
|---|:---:|---|---|
| Ejemplos 11.1.6.1 (pp. 44-54) | 15 | ✅ 9 cálculos a ≤ 1e-8 relativo + 6 errores de rango | [`test_norm_examples.py`](../../tests/test_norm_examples.py) |
| Ejemplos 11.1.6.2 (pp. 61-71) | 16 | ✅ 9 cálculos (con el **número de iteraciones** y los cambios de subgrupo) + 7 errores | ídem |
| Ejemplos 11.1.6.3 (pp. 74-88) | 18 | ✅ 12 cálculos + 6 errores, con la nueva `correct_observed_to_alternate` | ídem |
| Ejemplos 11.1.7.1 (pp. 92-100) | 11 | ✅ 7 cálculos + 4 errores, con presión en **kPa/bar** (antes solo funcionaban con psig) | ídem |
| Ejemplos 11.1.7.2 (pp. 104-116) | 17 | ✅ 10 cálculos + 7 errores, ídem | ídem |
| ITS-90 (t* impresos) | 19 | ✅ ≤ 1e-14 | ídem |
| Redondeo 11.1.5.4 (p. 38) | 3 | ✅ exactos | ídem + [`test_rounding.py`](../../tests/test_rounding.py) |
| Tablas 6C/54C sin densidad | 6 | ✅ con `ctl_from_alpha` | ídem |
| Tablas de muestra 11.1.8 (pp. 142-192) | 254 | ✅ exactos: 253 valores impresos (de 9 996 verificados durante la auditoría) + 1 caso de regresión del redondeo de α | [`test_tables_norm.py`](../../tests/test_tables_norm.py) |

---

<a id="estado-núcleo"></a>
## 3. Estado de los puntos del núcleo

| ID | Tema | Veredicto inicial | Cierre | Resolución |
|---|---|:---:|:---:|---|
| [NORM-01](11_anexo_norma_nucleo.md#norm-01) | Conversiones de densidad | ✅ | ✅ 100 % | Sin cambios en las fórmulas; validación de dominio (V-07) |
| [NORM-02](11_anexo_norma_nucleo.md#norm-02) | Conversiones de presión, Fp y α | ❌ | ✅ 100 % | `pressure_to_psig`, `fp_from_psi`, `alpha_f_to_alpha_c` con las constantes completas |
| [NORM-03](11_anexo_norma_nucleo.md#norm-03) | ITS-90 → IPTS-68 | ⚠️ | ✅ 100 % | Una sola entrada; salida en la unidad de entrada |
| [NORM-04](11_anexo_norma_nucleo.md#norm-04) | Algoritmo de redondeo | ❌ | ✅ 100 % | Aritmética decimal (N-01, N-02) |
| [NORM-05](11_anexo_norma_nucleo.md#norm-05) | Qué se redondea | ❌ | ✅ 100 % | `ctpl_rounded` en 6.1, 6.2, 6.3, 7.1 y 7.2; intermedios sin redondear |
| [NORM-06](11_anexo_norma_nucleo.md#norm-06) | Ecuaciones de 11.1.6.1 | ✅ | ✅ 100 % | Sin cambios |
| [NORM-07](11_anexo_norma_nucleo.md#norm-07) | Límites de ρ60 y α60 | ❌ | ✅ 100 % | Límites inclusivos; sin *fallback*; sin validación dentro de la iteración |
| [NORM-08](11_anexo_norma_nucleo.md#norm-08) | Límites de t y P; NaN | ✅ / ⚠️ | ✅ 100 % | NaN rechazado |
| [NORM-09](11_anexo_norma_nucleo.md#norm-09) | Rama `rho_60 <= 0` | ❌ | ✅ 100 % | Eliminada; `ctl_from_alpha` para CTL sin densidad |
| [NORM-10](11_anexo_norma_nucleo.md#norm-10) | Subgrupo por densidad | ✅ | ✅ 100 % | Extremo 1163.5 inclusivo explícito |
| [NORM-11](11_anexo_norma_nucleo.md#norm-11) | Da en el borde 1163.5 | ❌ | ✅ 100 % | Da derivado del subgrupo (fuel oil, 1.3) |
| [NORM-12](11_anexo_norma_nucleo.md#norm-12) | Rango de ρo (Paso 1) | ❌ | ✅ 100 % | Valores de la tabla de la p. 57 |
| [NORM-13](11_anexo_norma_nucleo.md#norm-13) | Máximo de iteraciones | ⚠️ | ✅ 100 % | Se mantiene 15, como el ejemplo de la p. 116 ([decisión](#decisiones)) |
| [NORM-14](11_anexo_norma_nucleo.md#norm-14) | Rango vs no convergencia | ❌ | ✅ 100 % | `MPMSRangeError` y `MPMSConvergenceError.last_result` |
| [NORM-15](11_anexo_norma_nucleo.md#norm-15) | Cambio de subgrupo | ✅ | ✅ 100 % | Se conserva; protegido por 5 ejemplos |
| [NORM-16](11_anexo_norma_nucleo.md#norm-16) | α con A/B/D | ⚠️ | ✅ 100 % | Excluyentes ([decisión](#decisiones)) |
| [NORM-17](11_anexo_norma_nucleo.md#norm-17) | 11.1.6.3 | ⚠️ | ✅ 100 % | Nueva `correct_observed_to_alternate` |
| [NORM-18](11_anexo_norma_nucleo.md#norm-18) | Tipos A/B/C/D | ❌ | ✅ 100 % | `CommodityType` + validador único |
| [NORM-19](11_anexo_norma_nucleo.md#norm-19) | Unidades de presión en 7.x | ❌ | ✅ 100 % | `pressure_unit` obligatorio ([decisión](#decisiones)) |
| [NORM-20](11_anexo_norma_nucleo.md#norm-20) | Salidas de 7.1 | ❌ | ✅ 100 % | `correct_metric_base_to_alternate` devuelve ρ, ρ60 y factores |
| [NORM-21](11_anexo_norma_nucleo.md#norm-21) | Salidas de 7.2 | ⚠️ | ✅ 100 % | `correct_metric_observed_to_base` |
| [NORM-22](11_anexo_norma_nucleo.md#norm-22) | Base 15/20 °C | ❌ | ✅ 100 % | `t_base_c` obligatorio y validado |
| [NORM-23](11_anexo_norma_nucleo.md#norm-23) | Unidad de α en 7.x | ⚠️ | ✅ 100 % | Parámetro `alpha_60_c` documentado en °C⁻¹ |
| [NORM-24](11_anexo_norma_nucleo.md#norm-24) | Errores de rango en 7.x | ❌ | ✅ 100 % | Se propagan como `MPMSRangeError` |
| [NORM-25](11_anexo_norma_nucleo.md#norm-25) | Límites generales | ❌ / ✅ | ✅ 100 % | Validación contra ρ60 (no contra valores convertidos) |
| [NORM-26](11_anexo_norma_nucleo.md#norm-26) | Tipo C sin densidad | ⚠️ | ✅ 100 % | `ctl_from_alpha` (P = 0); con presión se exige ρ > 0 |
| [NORM-27](11_anexo_norma_nucleo.md#norm-27) | 11.1.5.2 (α desde mediciones) | ⚠️ | ⬜ 0 % | No implementado: fuera del alcance de esta fase ([pendiente](#pendientes)) |
| [NORM-28](11_anexo_norma_nucleo.md#norm-28) | ρ en 7.1: CTPL redondeado o no | ⚠️ | ✅ 100 % | Se usa la fórmula del Paso 5 sin redondear ([decisión](#decisiones)) |
| [NORM-29](11_anexo_norma_nucleo.md#norm-29) | Precisión de 64 bits | ✅ | ✅ 100 % | Sin cambios |

---

<a id="estado-tablas"></a>
## 4. Estado de los puntos de tablas

| ID | Tema | Veredicto inicial | Cierre | Resolución |
|---|---|:---:|:---:|---|
| [NORM-T01](12_anexo_norma_tablas.md#norm-t01) | Motor vs tablas de muestra | ✅ | ✅ 100 % | 253 valores impresos en la suite |
| [NORM-T02](12_anexo_norma_tablas.md#norm-t02) | Conversiones | ✅ | ✅ 100 % | — |
| [NORM-T03](12_anexo_norma_tablas.md#norm-t03) | Presión, base y procedimiento | ✅ | ✅ 100 % | — |
| [NORM-T04](12_anexo_norma_tablas.md#norm-t04) | Redondeo de entradas y salidas | ✅ | ✅ 100 % | — |
| [NORM-T05](12_anexo_norma_tablas.md#norm-t05) | Redondeo de α en tablas C | ❌ | ✅ 100 % | 0.1e-6 °F⁻¹ / 0.2e-6 °C⁻¹ |
| [NORM-T06](12_anexo_norma_tablas.md#norm-t06) | Rango de α en tablas C | ❌ | ✅ 100 % | 230–930e-6 °F⁻¹ (414–1674e-6 °C⁻¹) |
| [NORM-T07](12_anexo_norma_tablas.md#norm-t07) | Tablas C con densidad ficticia 0 | ⚠️ | ✅ 100 % | `ctl_from_alpha` |
| [NORM-T08](12_anexo_norma_tablas.md#norm-t08) | Generador 23A | ❌ | ✅ 100 % | F-01 + rango 0.4710–1.1989 |
| [NORM-T09](12_anexo_norma_tablas.md#norm-t09) | Rangos del generador | ✅ | ✅ 100 % | Rangos con enteros (`Grid`) |
| [NORM-T10](12_anexo_norma_tablas.md#norm-t10) | Funciones combinadas x_y | ❌ | ✅ 100 % | Reemplazadas por `ctl_from_observed_*` ([decisión](#decisiones)) |
| [NORM-T11](12_anexo_norma_tablas.md#norm-t11) | 6x/24x fuera de rango | ❌ | ✅ 100 % | `MPMSRangeError` |
| [NORM-T12](12_anexo_norma_tablas.md#norm-t12) | Tablas 54x/60x | ✅ | ✅ 100 % | — |
| [NORM-T13](12_anexo_norma_tablas.md#norm-t13) | Celdas no calculables | ⚠️ | ✅ 100 % | Celda vacía, nunca 0 |
| [NORM-T14](12_anexo_norma_tablas.md#norm-t14) | Cobertura de tablas | ⚠️ | 🟡 90 % | Las 28 tablas de temperatura y las funciones 5x/23x/53x/59x; **faltan** 11.2.1 y 11.2.1M ([pendiente](#pendientes)) |
| [NORM-T15](12_anexo_norma_tablas.md#norm-t15) | Erratas de la norma | ⚠️ | ✅ 100 % | Interpretación documentada |
| [NORM-T16](12_anexo_norma_tablas.md#norm-t16) | Formato de salida | ⚠️ | ✅ 100 % | Temperatura en filas; nota del hidrómetro en tablas impares |
| [NORM-T17](12_anexo_norma_tablas.md#norm-t17) | Referencias en docstrings | ⚠️ | ✅ 100 % | Cada función cita su sección 11.1.8.x |

---

<a id="decisiones"></a>
## 5. Decisiones tomadas

| Tema | Decisión | Fundamento |
|---|---|---|
| Funciones combinadas x_y (NORM-T10) | **Normativo, con otro nombre**: `ctl_from_observed_api`, `ctl_from_observed_relative_density`, `ctl_from_observed_density_15c`, `ctl_from_observed_density_20c` | Decisión del usuario. 11.1.3.9 prohíbe redondear valores intermedios. Los resultados pueden diferir de la versión anterior en el 5.º decimal |
| Presión en 7.x (NORM-19) | **`pressure_unit` obligatorio** ("kPa" o "bar"), sin valor por defecto | Decisión del usuario: evita pasar psig por error |
| Compatibilidad de la API | **Ruptura limpia** documentada en [`CHANGELOG.md`](../../CHANGELOG.md) | Decisión del usuario; versión 0.x privada |
| Máximo de iteraciones (NORM-13) | 15 evaluaciones (m = 0…14) | Coincide con el ejemplo 7.2-17 (p. 116) |
| `iterations` | Índice m de la iteración que converge | Coincide con los 9 ejemplos de 11.1.6.2 |
| α con A/B/D (NORM-16) | Error de validación | La norma pide grupo **o** α (pp. 39, 55) |
| ρ en 7.1 (NORM-28) | Fórmula del Paso 5 sin redondear (ρ = CTL·CPL·ρT) | Consistente con 6.1. Los ejemplos de 7.1 usan el CTPL redondeado; la prueba compara ρT·`ctpl_rounded` |
| Densidad intermedia en tablas impares | No se redondea antes de convertir | 11.1.8, paso 6 (p. 141) |

---

<a id="pendientes"></a>
## 6. Pendientes

| Pendiente | Referencia | Impacto |
|---|---|---|
| 11.1.5.2: α60 y ρ60 desde mediciones de densidad a varias temperaturas | [NORM-27](11_anexo_norma_nucleo.md#norm-27) | Funcionalidad nueva; el ejemplo de la p. 35 ya está identificado para su prueba |
| Tablas de compresibilidad 11.2.1 / 11.2.1M | [NORM-T14](12_anexo_norma_tablas.md#norm-t14) | Funcionalidad nueva (Fp tabulado) |
| Generador: CSV incremental y vectorización | [P-03](06_rendimiento.md#p-03) | Rendimiento al generar tablas completas |
| Unificar el idioma de mensajes y docstrings | [C-03](07_calidad_mantenibilidad.md#c-03) | Estilo |

---

[⬅ Anterior: Plan de acción](09_plan_de_accion.md) · [Índice](README.md) · [Siguiente: Anexo A — Núcleo ➡](11_anexo_norma_nucleo.md)
