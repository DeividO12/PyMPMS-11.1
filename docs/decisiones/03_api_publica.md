# 03 · API pública

[⬅ Anterior: Norma y cálculo](02_norma_y_calculo.md) · [Índice](README.md) · [Siguiente: Calidad y documentación ➡](04_calidad_y_documentacion.md)

Contrato entre la librería y el integrador. La referencia de uso está en la [documentación API](../api/README.md).

## 📑 Contenido

| ID | Decisión | Estado |
|---|---|:---:|
| [ADR-016](#adr-016) | Ruptura limpia de la API, sin alias de compatibilidad | ✅ |
| [ADR-017](#adr-017) | Argumentos solo por nombre y resultados `NamedTuple` | ✅ |
| [ADR-018](#adr-018) | Tres puntos de importación públicos | ✅ |
| [ADR-019](#adr-019) | Mensajes de error en ASCII; validación en las unidades del usuario | ✅ |
| [ADR-020](#adr-020) | Generador de tablas como script fuera del paquete | ✅ |

---

<a id="adr-016"></a>
## ADR-016 · Ruptura limpia de la API, sin alias de compatibilidad

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 👤 Usuario | [`CHANGELOG.md`](../../CHANGELOG.md) › Cambios incompatibles |

**Contexto.** Las correcciones exigían renombrar parámetros (`commodity_group` → `commodity_type`, `alpa_obs` → `alpha_obs`), cambiar la forma de los resultados y eliminar el paquete duplicado `Tables/`.

**Decisión.** Cambiar la API directamente, sin alias ni avisos de obsolescencia. Se documentan todos los cambios en el CHANGELOG.

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Mantener los nombres viejos con `DeprecationWarning` | Más código para una versión 0.x privada sin consumidores externos |

**Consecuencias.** La v1.0.0 nace con una API limpia. A partir de ella, un cambio incompatible exige subir la versión mayor ([ADR-025](05_versionado_y_distribucion.md#adr-025)).

---

<a id="adr-017"></a>
## ADR-017 · Argumentos solo por nombre y resultados `NamedTuple`

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 🔧 Técnica | commits `b21e5d8`, `5b0e53a`; [Referencia de resultados](../api/07_ref_resultados.md) |

**Contexto.** Las funciones devolvían tuplas de 5 o 6 valores en distinto orden según la función, y aceptaban argumentos por posición. Así era fácil pasar una temperatura donde iba una presión, o tomar el valor equivocado al desempaquetar ([F-04](../informe_2026-10-09_1420/01_errores_funcionales.md#f-04), [C-02](../informe_2026-10-09_1420/07_calidad_mantenibilidad.md#c-02)).

**Decisión.**
- Todas las funciones públicas usan solo argumentos por nombre (`*`).
- Los resultados son `NamedTuple` con campos en minúscula (`rho_60`, `ctl`, `fp`, `cpl`, `ctpl`, `ctpl_rounded`…). Se leen por nombre y siguen pudiendo desempaquetarse.

**Consecuencias.** El orden y los nombres de los campos forman parte de la API pública: agregar o reordenar campos es un cambio incompatible.

---

<a id="adr-018"></a>
## ADR-018 · Tres puntos de importación públicos

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-13 | 🔧 Técnica | commit `2e12236`; [Conceptos › Puntos de importación](../api/01_conceptos.md#importacion) |

**Contexto.** Las conversiones y las tablas solo se podían importar desde módulos internos (`api_mpms.mpms_11_1.section_5_1`…).

**Decisión.** La API pública son tres módulos; todo lo demás es interno y puede cambiar sin aviso.

| Módulo | Contenido |
|---|---|
| `api_mpms` | Correcciones, `ctl_from_alpha`, resultados, excepciones, `CommodityType` |
| `api_mpms.conversions` | Conversiones de unidades y `api_round` |
| `api_mpms.tables` | Valores en formato de tabla (11.1.8) |

---

<a id="adr-019"></a>
## ADR-019 · Mensajes de error en ASCII; validación en las unidades del usuario

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-13 | 🔧 Técnica | commit `2e12236`; `test_error_messages_are_ascii` |

**Contexto.** Al preparar la documentación API se comprobó que los mensajes con `°F⁻¹` o `kg/m³` provocaban un `UnicodeEncodeError` al imprimirse o registrarse en consolas Windows (cp1252). Además, en 11.1.7 un error de temperatura se reportaba como error de densidad, con valores internos en °F.

**Decisión.**
- Los mensajes van en inglés y en ASCII, con unidades explícitas (`degF`, `degC`, `kg/m3`, `1/degF`).
- Las funciones métricas validan la temperatura y la presión en °C y kPa/bar antes de calcular.
- Los errores de rango de 11.1.7 incluyen los datos de entrada del usuario.

**Consecuencias.** El integrador debe decidir con el **tipo** de la excepción, no con el texto del mensaje, que puede mejorar entre versiones.

---

<a id="adr-020"></a>
## ADR-020 · Generador de tablas como script fuera del paquete

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 🔧 Técnica | commits `26df9a8`, `968c0fe`; [Generador de tablas](../api/10_generador_tablas.md) |

**Contexto.** El generador vivía dentro del paquete, no se podía importar, dependía de numpy y pandas sin declararlos, y tenía un error que invalidaba la tabla 23A ([F-01](../informe_2026-10-09_1420/01_errores_funcionales.md#f-01)).

**Decisión.** Pasó a ser `scripts/generate_tables.py`, una herramienta fuera del paquete con dependencias opcionales (`[tables]`).
- Una sola función parametrizada para las 28 tablas de 11.1.8, con los rangos de la norma generados con enteros.
- Temperatura en filas, como en las tablas impresas.
- Celdas no calculables **vacías, nunca 0**.
- Ejecución en paralelo.

---

[⬅ Anterior: Norma y cálculo](02_norma_y_calculo.md) · [Índice](README.md) · [Siguiente: Calidad y documentación ➡](04_calidad_y_documentacion.md)
