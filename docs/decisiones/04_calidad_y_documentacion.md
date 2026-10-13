# 04 · Calidad y documentación

[⬅ Anterior: API pública](03_api_publica.md) · [Índice](README.md) · [Siguiente: Versionado y distribución ➡](05_versionado_y_distribucion.md)

## 📑 Contenido

| ID | Decisión | Estado |
|---|---|:---:|
| [ADR-021](#adr-021) | Ejemplos de la norma y de la documentación como pruebas automáticas | ✅ |
| [ADR-022](#adr-022) | CI en Python 3.9 y 3.12; no se agrega 3.13 | ✅ |
| [ADR-023](#adr-023) | Documentación en español; la del integrador no explica el cálculo | ✅ |
| [ADR-024](#adr-024) | Informes de auditoría por hallazgo con porcentaje de cierre | ✅ |

---

<a id="adr-021"></a>
## ADR-021 · Ejemplos de la norma y de la documentación como pruebas automáticas

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 🔧 Técnica | [`tests/data/`](../../tests/data/), `pyproject.toml` › `--doctest-glob=*.md` |

**Contexto.** Los «tests» originales solo imprimían resultados: `pytest` no recolectaba ninguna prueba ([T-01](../informe_2026-10-09_1420/05_pruebas.md#t-01)).

**Decisión.**
- Los ejemplos resueltos de la norma (105) y los valores de sus tablas de muestra (253) se guardan como datos (`tests/data/*.json`). Las pruebas los comparan con al menos 8 cifras significativas, como exige la norma (págs. 29-30), y los valores redondeados de forma exacta.
- Los bloques `>>>` del README y de `docs/api` se ejecutan como doctest.
- Cobertura objetivo: 99 % (alcanzada).

**Consecuencias.** 515 pruebas. Un cambio que altere un resultado normativo o un ejemplo documentado rompe la suite. Las mismas pruebas validarán los wheels compilados ([ADR-026](05_versionado_y_distribucion.md#adr-026)).

---

<a id="adr-022"></a>
## ADR-022 · CI en Python 3.9 y 3.12; no se agrega 3.13

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-13 | 👤 Usuario | [`.github/workflows/tests.yml`](../../.github/workflows/tests.yml) |

**Contexto.** Se verificó a mano que la librería funciona en Python 3.13.7 (515 pruebas y mypy en verde). Se ofreció agregar 3.13 a la CI.

**Decisión.** La CI corre en Python 3.9 (mínimo declarado) y 3.12 sobre Linux, con ruff, mypy y pytest. No se agrega 3.13 por ahora.

**Consecuencias.** La compatibilidad con 3.13 está verificada una vez, pero no se vigila en cada push. Los wheels compilados sí cubrirán 3.13 ([ADR-026](05_versionado_y_distribucion.md#adr-026)).

---

<a id="adr-023"></a>
## ADR-023 · Documentación en español; la del integrador no explica el cálculo

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-13 | 👤 Usuario | [README](../../README.md), [documentación API](../api/README.md) |

**Decisión.**
- README, documentación API, informes y este registro van en **español**. Los nombres de funciones y parámetros, y los mensajes de error ([ADR-019](03_api_publica.md#adr-019)), quedan en inglés.
- La documentación API está pensada para el **integrador**: qué consume, qué devuelve, qué errores lanza y guías por caso. No explica cómo se calcula cada factor; para eso está la norma.
- Los ejemplos usan los ejemplos resueltos y las tablas de muestra de la norma, con etiquetas (`📘 Norma`, `🔁 Conversión`, `📐 Redondeo`, `⚠️ Error`) y enlaces a las conversiones que requieren.
- Índices y tablas de contenido con hipervínculos, con anclas explícitas (`<a id>`).

---

<a id="adr-024"></a>
## ADR-024 · Informes de auditoría por hallazgo con porcentaje de cierre

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 👤 Usuario | [`docs/informe_2026-10-09_1420/`](../informe_2026-10-09_1420/README.md) |

**Decisión.**
- Los informes van en `docs/informe_<AAAA-MM-DD_HHMM>/`, divididos por categoría, con índices enlazados.
- Cada hallazgo muestra su porcentaje de cierre en el título y termina con una sección **Resolución** que indica commits y verificación.
- Los enlaces al código auditado apuntan al commit fijo en GitHub (`blob/<hash>`), para que las líneas citadas sigan siendo exactas después de corregir.

---

[⬅ Anterior: API pública](03_api_publica.md) · [Índice](README.md) · [Siguiente: Versionado y distribución ➡](05_versionado_y_distribucion.md)
