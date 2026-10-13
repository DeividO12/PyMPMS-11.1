# Informe de Auditoría de Código — `api_mpms` (PyMPMS-11.1)

| Campo | Valor |
|---|---|
| **Fecha** | 2026-10-09 14:20 |
| **Rama auditada** | `dev_deivid` |
| **Commit** | `4f1216d` — *chore: Excluir carpeta PDFs del control de versiones* |
| **Alcance** | Integridad del código: errores, fallos potenciales, casos no contemplados, optimizaciones, mantenibilidad |
| **Fuera de alcance** | Conformidad matemática/normativa con API MPMS 11.1 (se revisará en otra fase) |
| **Líneas auditadas** | ~1 830 (22 archivos `.py` + `pyproject.toml`, `README.md`, `.gitignore`) |
| **Entorno de verificación** | Python 3.12.10 · Windows 11 |
| **Corrección** | 2026-10-09 · commits `6b68257` … `a9f9076` en `dev_deivid` · versión `1.0.0` (tag `v1.0.0`) |
| **Estado de cierre** | **36 de 38 hallazgos cerrados al 100 %**, 2 parciales · cierre promedio **98.7 %** ([detalle](#estado-de-cierre)) |
| **Conformidad normativa** | Verificada en paralelo contra API MPMS 11.1 (2004) → [10 · Conformidad con la norma](10_conformidad_norma.md) |

> [!NOTE]
> Todos los hallazgos marcados como **✅ Verificado** fueron reproducidos ejecutando el código. Los scripts y salidas están en el [Anexo de evidencias](08_anexo_evidencias.md).

---

## 📑 Tabla de contenido

1. [Resumen ejecutivo](#resumen-ejecutivo)
   - [Estado de cierre](#estado-de-cierre)
2. [Escala de severidad](#escala-de-severidad)
3. [Mapa de hallazgos](#mapa-de-hallazgos)
4. [Documentos del informe](#documentos-del-informe)
5. [Metodología](#metodología)
6. [Inventario de módulos auditados](#inventario-de-módulos-auditados)

---

<a id="resumen-ejecutivo"></a>
## 1. Resumen ejecutivo

La librería tiene una **arquitectura modular razonable** (constantes, validadores, excepciones y secciones separadas) y los algoritmos centrales (`correct_base_to_alternate`, `correct_observed_to_base`) funcionan para entradas dentro de rango. Sin embargo, la auditoría encontró problemas que **pueden producir resultados incorrectos sin ningún aviso**:

| # | Hallazgo más relevante | Severidad |
|---|---|---|
| 1 | `api_round` **no detecta empates (x.5)** cuando el valor es grande: ~26 % de los empates de CTL en `[0.8, 1.1]` y 901 empates de densidad en `[610, 1163] kg/m³` se redondean al lado incorrecto. → [N-01](03_precision_numerica.md#n-01) | 🔴 Crítico |
| 2 | `generar_tabla_23a` convierte la **temperatura** a densidad en lugar de la densidad relativa: toda la tabla es inválida. → [F-01](01_errores_funcionales.md#f-01) | 🔴 Crítico |
| 3 | **Existen dos implementaciones distintas** de las mismas funciones de tabla (`mpms_11_1/tables.py` y `Tables/*.py`) que **devuelven valores diferentes** para la misma entrada. → [E-01](04_estructura_empaquetado.md#e-01) | 🟠 Alto |
| 4 | La protección `if rho_60 <= 0` en la sección 6.1 es **inalcanzable**: con densidad 0 el código falla con `ZeroDivisionError`, y con densidad negativa devuelve resultados absurdos. → [F-02](01_errores_funcionales.md#f-02) | 🟠 Alto |
| 5 | **No hay pruebas automatizadas reales**: los archivos `test_*.py` solo imprimen; `pytest` recolecta 0 pruebas. → [T-01](05_pruebas.md#t-01) | 🟠 Alto |

### Conteo por severidad

| Severidad | Cantidad |
|---|:---:|
| 🔴 Crítico | 2 |
| 🟠 Alto | 9 |
| 🟡 Medio | 15 |
| 🔵 Bajo | 12 |
| **Total** | **38** |

### Conteo por categoría

| Categoría | Documento | Hallazgos |
|---|---|:---:|
| Errores funcionales | [01_errores_funcionales.md](01_errores_funcionales.md) | 10 |
| Validación y manejo de errores | [02_validacion_y_errores.md](02_validacion_y_errores.md) | 7 |
| Precisión numérica y redondeo | [03_precision_numerica.md](03_precision_numerica.md) | 4 |
| Estructura y empaquetado | [04_estructura_empaquetado.md](04_estructura_empaquetado.md) | 6 |
| Pruebas | [05_pruebas.md](05_pruebas.md) | 3 |
| Rendimiento / optimizaciones | [06_rendimiento.md](06_rendimiento.md) | 4 |
| Calidad y mantenibilidad | [07_calidad_mantenibilidad.md](07_calidad_mantenibilidad.md) | 4 (+2 recomendaciones) |

<a id="estado-de-cierre"></a>
### Estado de cierre

> [!TIP]
> Cada hallazgo muestra su porcentaje de cierre en el título (p. ej. *F-01 · … — ✅ 100 %*) y termina con una sección **Resolución** que indica commits y verificación.

| Categoría | Hallazgos | Cerrados 100 % | Parciales | Cierre promedio |
|---|:---:|:---:|:---:|:---:|
| [Errores funcionales](01_errores_funcionales.md) | 10 | 10 | 0 | ✅ 100 % |
| [Validación y manejo de errores](02_validacion_y_errores.md) | 7 | 7 | 0 | ✅ 100 % |
| [Precisión numérica y redondeo](03_precision_numerica.md) | 4 | 4 | 0 | ✅ 100 % |
| [Estructura y empaquetado](04_estructura_empaquetado.md) | 6 | 6 | 0 | ✅ 100 % |
| [Pruebas](05_pruebas.md) | 3 | 3 | 0 | ✅ 100 % |
| [Rendimiento / optimizaciones](06_rendimiento.md) | 4 | 3 | 1 ([P-03](06_rendimiento.md#p-03) 70 %) | 🟡 92.5 % |
| [Calidad y mantenibilidad](07_calidad_mantenibilidad.md) | 4 (+2) | 3 (+2) | 1 ([C-03](07_calidad_mantenibilidad.md#c-03) 80 %) | 🟡 95 % |
| **Total** | **38** | **36** | **2** | **98.7 %** |

| Indicador | Antes (`4f1216d`) | Después (`1.0.0`) |
|---|---|---|
| Pruebas automatizadas | 0 | **493** (105 ejemplos resueltos y 253 valores de tablas de la norma) |
| Cobertura | — | **99 %** |
| `ruff` / `mypy` | sin configurar | sin errores |
| `correct_observed_to_base` (tipo B) | 22.4 µs | 16.7 µs |

---

<a id="escala-de-severidad"></a>
## 2. Escala de severidad

| Nivel | Criterio |
|---|---|
| 🔴 **Crítico** | Produce resultados numéricos incorrectos **silenciosamente** en casos de uso normales. |
| 🟠 **Alto** | Rompe una funcionalidad, provoca excepciones no controladas en entradas plausibles o deja el proyecto sin red de seguridad. |
| 🟡 **Medio** | Comportamiento inesperado en casos borde, contratos de API inconsistentes, mensajes de error engañosos. |
| 🔵 **Bajo** | Mantenibilidad, estilo, documentación, optimizaciones menores. |

---

<a id="mapa-de-hallazgos"></a>
## 3. Mapa de hallazgos

| ID | Severidad | Título | Ubicación | Verif. | Cierre |
|---|---|---|---|:---:|:---:|
| [N-01](03_precision_numerica.md#n-01) | 🔴 Crítico | `api_round` no detecta empates en valores grandes | `section_5_4.py:54` | ✅ | ✅ 100 % |
| [F-01](01_errores_funcionales.md#f-01) | 🔴 Crítico | Tabla 23A usa temperatura como densidad relativa | `generator_tables.py:317` | ✅ | ✅ 100 % |
| [E-01](04_estructura_empaquetado.md#e-01) | 🟠 Alto | Dos implementaciones divergentes de las funciones de tabla | `tables.py` / `Tables/` | ✅ | ✅ 100 % |
| [F-02](01_errores_funcionales.md#f-02) | 🟠 Alto | Guardia `rho_60 <= 0` inalcanzable → `ZeroDivisionError` | `section_6_1.py:64-81` | ✅ | ✅ 100 % |
| [F-03](01_errores_funcionales.md#f-03) | 🟠 Alto | `generator_tables.py` no se puede importar | `generator_tables.py:1-9` | ✅ | ✅ 100 % |
| [N-02](03_precision_numerica.md#n-02) | 🟠 Alto | Limpieza final de `api_round` corrompe deltas no decimales | `section_5_4.py:74-78` | ✅ | ✅ 100 % |
| [V-01](02_validacion_y_errores.md#v-01) | 🟠 Alto | No se valida la densidad en ningún punto | `section_6_1.py`, `section_6_2.py` | ✅ | ✅ 100 % |
| [V-02](02_validacion_y_errores.md#v-02) | 🟠 Alto | `except:` desnudo oculta errores en el generador | `generator_tables.py` | ✅ | ✅ 100 % |
| [T-01](05_pruebas.md#t-01) | 🟠 Alto | Los tests no son pruebas (sin `assert`, 0 recolectadas) | `tests/` | ✅ | ✅ 100 % |
| [E-02](04_estructura_empaquetado.md#e-02) | 🟠 Alto | `Tables` vs `tables`: mayúsculas distintas en git y disco | `src/api_mpms/Tables` | ✅ | ✅ 100 % |
| [E-03](04_estructura_empaquetado.md#e-03) | 🟠 Alto | Dependencias no declaradas (`numpy`, `pandas`) | `pyproject.toml` | ✅ | ✅ 100 % |
| [F-04](01_errores_funcionales.md#f-04) | 🟡 Medio | Anotaciones de retorno no coinciden con lo devuelto | varios | ✅ | ✅ 100 % |
| [F-05](01_errores_funcionales.md#f-05) | 🟡 Medio | `alpha_60_c = 0.0` se trata como “no proporcionado” | `section_7_1.py:26`, `section_7_2.py:26` | ✅ | ✅ 100 % |
| [F-06](01_errores_funcionales.md#f-06) | 🟡 Medio | `commodity_type=None` por defecto produce `AttributeError` | `section_7_1.py:14`, `section_7_2.py:14` | ✅ | ✅ 100 % |
| [F-07](01_errores_funcionales.md#f-07) | 🟡 Medio | Ambas temperaturas en `its90_to_ipts68`: se ignora una sin aviso | `section_5_3.py:45-52` | ✅ | ✅ 100 % |
| [F-08](01_errores_funcionales.md#f-08) | 🟡 Medio | Presión ignorada silenciosamente cuando `rho_60 <= 0` (tipo C) | `section_6_1.py:81-83` | ✅ | ✅ 100 % |
| [V-03](02_validacion_y_errores.md#v-03) | 🟡 Medio | Presión `NaN` pasa la validación | `inputs.py:13-20` | ✅ | ✅ 100 % |
| [V-04](02_validacion_y_errores.md#v-04) | 🟡 Medio | `alpha_60` no se valida (CTL=0, `OverflowError`) | `section_6_1.py:47` | ✅ | ✅ 100 % |
| [V-05](02_validacion_y_errores.md#v-05) | 🟡 Medio | Entradas fuera de rango se reportan como error de convergencia | `section_6_2.py:55-102` | ✅ | ✅ 100 % |
| [V-06](02_validacion_y_errores.md#v-06) | 🟡 Medio | Validación de tipo de producto inconsistente entre módulos | varios | ✅ | ✅ 100 % |
| [N-03](03_precision_numerica.md#n-03) | 🟡 Medio | Rangos con `np.arange` de paso flotante | `generator_tables.py` | — | ✅ 100 % |
| [N-04](03_precision_numerica.md#n-04) | 🟡 Medio | Constantes y límites duplicados en varios archivos | varios | — | ✅ 100 % |
| [E-04](04_estructura_empaquetado.md#e-04) | 🟡 Medio | README desactualizado / ruta de import incorrecta | `README.md` | ✅ | ✅ 100 % |
| [T-02](05_pruebas.md#t-02) | 🟡 Medio | Módulos sin ninguna cobertura | `tests/` | — | ✅ 100 % |
| [P-01](06_rendimiento.md#p-01) | 🟡 Medio | Trabajo invariante recalculado en cada iteración | `section_6_2.py:59-98` | ✅ | ✅ 100 % |
| [P-03](06_rendimiento.md#p-03) | 🟡 Medio | Generador de tablas: coste y memoria | `generator_tables.py` | ✅ | 🟡 70 % |
| [F-09](01_errores_funcionales.md#f-09) | 🔵 Bajo | Valores calculados y no usados en 7.1 | `section_7_1.py:29` | — | ✅ 100 % |
| [F-10](01_errores_funcionales.md#f-10) | 🔵 Bajo | Cambio de grupo entre iteraciones (zona de transición) | `section_6_1.py:57` | ✅ | ✅ 100 % |
| [V-07](02_validacion_y_errores.md#v-07) | 🔵 Bajo | Conversiones de unidades sin protección | `section_5_1.py` | ✅ | ✅ 100 % |
| [E-05](04_estructura_empaquetado.md#e-05) | 🔵 Bajo | Tests empaquetados dentro de la librería | `src/api_mpms/tests` | — | ✅ 100 % |
| [E-06](04_estructura_empaquetado.md#e-06) | 🔵 Bajo | Sin API pública (`__init__` vacíos, sin `py.typed`) | `__init__.py` | — | ✅ 100 % |
| [T-03](05_pruebas.md#t-03) | 🔵 Bajo | Sin configuración de pytest / CI | `pyproject.toml` | — | ✅ 100 % |
| [P-02](06_rendimiento.md#p-02) | 🔵 Bajo | `resolve_commodity_group` reconstruye listas en cada llamada | `commodity_groups.py:45-69` | — | ✅ 100 % |
| [P-04](06_rendimiento.md#p-04) | 🔵 Bajo | Código del generador duplicado 7 veces | `generator_tables.py` | — | ✅ 100 % |
| [C-01](07_calidad_mantenibilidad.md#c-01) | 🔵 Bajo | Variables e imports sin uso | varios | — | ✅ 100 % |
| [C-02](07_calidad_mantenibilidad.md#c-02) | 🔵 Bajo | Retornos como tuplas posicionales | varios | — | ✅ 100 % |
| [C-03](07_calidad_mantenibilidad.md#c-03) | 🔵 Bajo | Nombres inconsistentes y errores tipográficos | varios | — | 🟡 80 % |
| [C-04](07_calidad_mantenibilidad.md#c-04) | 🔵 Bajo | Docstrings y cabeceras incorrectas | varios | — | ✅ 100 % |

> [!TIP]
> Los hallazgos C-05 y C-06 (logging y rutas de salida) se documentan en [07_calidad_mantenibilidad.md](07_calidad_mantenibilidad.md) como recomendaciones sin severidad asignada.

---

<a id="documentos-del-informe"></a>
## 4. Documentos del informe

| # | Documento | Contenido |
|:---:|---|---|
| 01 | [Errores funcionales](01_errores_funcionales.md) | Bugs que producen resultados erróneos o excepciones |
| 02 | [Validación y manejo de errores](02_validacion_y_errores.md) | Entradas no validadas, excepciones mal clasificadas |
| 03 | [Precisión numérica y redondeo](03_precision_numerica.md) | `api_round`, aritmética flotante, constantes |
| 04 | [Estructura y empaquetado](04_estructura_empaquetado.md) | Organización del paquete, `pyproject.toml`, README |
| 05 | [Pruebas](05_pruebas.md) | Estado de la suite de pruebas y propuesta |
| 06 | [Rendimiento y optimizaciones](06_rendimiento.md) | Mediciones y mejoras de eficiencia |
| 07 | [Calidad y mantenibilidad](07_calidad_mantenibilidad.md) | Estilo, nombres, contratos de API, documentación |
| 08 | [Anexo de evidencias](08_anexo_evidencias.md) | Scripts de verificación y salidas obtenidas |
| 09 | [Plan de acción](09_plan_de_accion.md) | Priorización y orden sugerido de corrección |
| 10 | [Conformidad con la norma](10_conformidad_norma.md) | Resultado de la verificación contra API MPMS 11.1, estado de cada punto NORM, decisiones y pendientes |
| 11 | [Anexo A — Núcleo](11_anexo_norma_nucleo.md) | Verificación detallada de 11.1.2–11.1.7 (29 puntos, ejemplos resueltos) |
| 12 | [Anexo B — Tablas](12_anexo_norma_tablas.md) | Verificación detallada de 11.1.8 (17 puntos, tablas de muestra) |

---

<a id="metodología"></a>
## 5. Metodología

1. **Lectura completa** de todos los archivos versionados en `src/`, `pyproject.toml`, `README.md`, `.gitignore` y `LICENSE`.
2. **Análisis estático manual**: flujo de datos, contratos de funciones, rutas de error, imports, duplicación.
3. **Pruebas dinámicas dirigidas** (scripts en el anexo):
   - Casos borde: `NaN`, `inf`, `None`, `0`, negativos, valores fuera de rango.
   - Comparación de `api_round` contra `decimal.Decimal` con `ROUND_HALF_EVEN` (referencia exacta).
   - Barrido de convergencia de `correct_observed_to_base` (≈ 78 000 combinaciones densidad × temperatura).
   - Comparación de las dos implementaciones de tablas.
   - Medición de tiempos por llamada.
4. **Clasificación** por severidad e impacto, con recomendación concreta para cada hallazgo.

> [!IMPORTANT]
> Esta auditoría **no** evalúa si las fórmulas, coeficientes o criterios de convergencia son fieles a API MPMS 11.1. Cuando un hallazgo toca una fórmula, se analiza solo su robustez como código (divisiones por cero, desbordamientos, flujo de control).

---

<a id="inventario-de-módulos-auditados"></a>
## 6. Inventario de módulos auditados

> [!NOTE]
> Inventario del commit auditado `4f1216d`. Los enlaces de los documentos 01 a 08 apuntan a esa versión fija en GitHub (`blob/4f1216d`), de modo que las rutas y líneas citadas siguen siendo exactas tras las correcciones.

| Módulo | Archivo | Líneas | Hallazgos |
|---|---|:---:|---|
| Constantes | [`constants/commodity_groups.py`](../../src/api_mpms/constants/commodity_groups.py) | 69 | V-06, N-04, P-02, F-10 |
| Constantes | [`constants/iteration_coefficients.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/constants/iteration_coefficients.py) | 36 | N-04 |
| Excepciones | [`exceptions/*.py`](../../src/api_mpms/exceptions/) | 8 | — |
| Validadores | [`validators/inputs.py`](../../src/api_mpms/validators/inputs.py) | 20 | V-01, V-03 |
| 11.1.5.1 | [`mpms_11_1/section_5_1.py`](../../src/api_mpms/mpms_11_1/section_5_1.py) | 42 | V-07, N-04 |
| 11.1.5.3 | [`mpms_11_1/section_5_3.py`](../../src/api_mpms/mpms_11_1/section_5_3.py) | 70 | F-07 |
| 11.1.5.4 | [`mpms_11_1/section_5_4.py`](../../src/api_mpms/mpms_11_1/section_5_4.py) | 78 | N-01, N-02 |
| 11.1.6.1 | [`mpms_11_1/section_6_1.py`](../../src/api_mpms/mpms_11_1/section_6_1.py) | 102 | F-02, F-04, F-08, V-01, V-04 |
| 11.1.6.2 | [`mpms_11_1/section_6_2.py`](../../src/api_mpms/mpms_11_1/section_6_2.py) | 102 | V-05, P-01, C-01 |
| 11.1.7.1 | [`mpms_11_1/section_7_1.py`](../../src/api_mpms/mpms_11_1/section_7_1.py) | 36 | F-05, F-06, F-09 |
| 11.1.7.2 | [`mpms_11_1/section_7_2.py`](../../src/api_mpms/mpms_11_1/section_7_2.py) | 36 | F-04, F-05, F-06, C-04 |
| Tablas (unificado) | [`mpms_11_1/tables.py`](../../src/api_mpms/mpms_11_1/tables.py) | 253 | E-01, F-04, C-03 |
| Tablas (módulos) | [`Tables/table_*.py`] *(eliminado)*(https://github.com/DeividO12/PyMPMS-11.1/tree/4f1216d/src/api_mpms/Tables/) | 11 × ~25 | E-01, E-02, F-04 |
| Generador | [`Tables/generator_tables.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/Tables/generator_tables.py) *(hoy `scripts/generate_tables.py`)* | 341 | F-01, F-03, V-02, N-03, P-03, P-04 |
| Pruebas | [`tests/test_6_1.py`, `tests/test_6_2.py`](https://github.com/DeividO12/PyMPMS-11.1/tree/4f1216d/src/api_mpms/tests/) | 175 | T-01, T-02, E-05 |
| Empaquetado | [`pyproject.toml`](../../pyproject.toml), [`README.md`](../../README.md) | — | E-03, E-04, E-06, T-03 |
