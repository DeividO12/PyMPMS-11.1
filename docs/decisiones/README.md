# Registro de decisiones — PyMPMS-11.1

Decisiones de arquitectura, normativas, de API, de calidad y de distribución tomadas en el proyecto, con su contexto, las alternativas consideradas y sus consecuencias. Sirve para no volver a discutir lo ya decidido y para saber **por qué** el código es como es.

## 📑 Contenido

1. [Cómo leer este registro](#como-leer)
2. [Índice de decisiones](#indice)
3. [Decisiones pendientes](#pendientes)
4. [Cómo registrar una decisión nueva](#nueva)

| Documento | Área |
|---|---|
| [01 · Proceso y repositorio](01_proceso_y_repositorio.md) | Flujo de trabajo, ramas, espejo en SYZ |
| [02 · Norma y cálculo](02_norma_y_calculo.md) | Cómo se interpreta API MPMS 11.1 |
| [03 · API pública](03_api_publica.md) | Contrato con el integrador |
| [04 · Calidad y documentación](04_calidad_y_documentacion.md) | Pruebas, CI, idioma y documentación |
| [05 · Versionado y distribución](05_versionado_y_distribucion.md) | Versiones, ofuscación, wheels y liberación |
| [06 · Pendientes](06_pendientes.md) | Decisiones abiertas, con opciones y recomendación |

---

<a id="como-leer"></a>
## 1. Cómo leer este registro

Cada decisión (ADR, *Architecture Decision Record*) tiene:

| Campo | Contenido |
|---|---|
| **Estado** | ✅ Aceptada e implementada · 🟡 Aceptada, pendiente de implementar · ⏳ Pendiente de decidir · ❌ Reemplazada |
| **Fecha** | Cuándo se tomó |
| **Decidido por** | 👤 **Usuario** (decisión explícita del responsable del proyecto) · 📘 **Norma** (lo exige API MPMS 11.1; se cita la página del PDF) · 🔧 **Técnica** (propuesta durante el desarrollo y aceptada) |
| **Evidencia** | Commits, documentos o pruebas que la respaldan |
| **Contexto · Decisión · Alternativas · Consecuencias** | El porqué, el qué, lo que se descartó y lo que implica |

> [!IMPORTANT]
> Una decisión aceptada no se cambia en silencio. Si deja de servir, se registra una nueva que la **reemplaza** y la anterior pasa a ❌ con un enlace a la nueva.

---

<a id="indice"></a>
## 2. Índice de decisiones

### Proceso y repositorio

| ID | Decisión | Estado | Fecha | Decidido por |
|---|---|:---:|---|:---:|
| [ADR-001](01_proceso_y_repositorio.md#adr-001) | Auditar la integridad del código por separado de la conformidad normativa | ✅ | 2026-10-09 | 👤 |
| [ADR-002](01_proceso_y_repositorio.md#adr-002) | Corregir verificando cada cambio contra la norma; la norma manda | ✅ | 2026-10-09 | 👤 |
| [ADR-003](01_proceso_y_repositorio.md#adr-003) | Commits por fase en `dev_deivid`; push solo cuando se pide | ✅ | 2026-10-09 | 👤 |
| [ADR-004](01_proceso_y_repositorio.md#adr-004) | Entorno `.venv` local; no modificar el Python global | ✅ | 2026-10-09 | 👤 |
| [ADR-005](01_proceso_y_repositorio.md#adr-005) | Repositorio de trabajo personal con espejo en `sistemasSYZ` | ✅ | 2026-10-13 | 👤 |
| [ADR-006](01_proceso_y_repositorio.md#adr-006) | Integrar `dev_deivid` en `master` con merge `--no-ff` | ✅ | 2026-10-13 | 👤 |

### Norma y cálculo

| ID | Decisión | Estado | Fecha | Decidido por |
|---|---|:---:|---|:---:|
| [ADR-007](02_norma_y_calculo.md#adr-007) | No extrapolar: fuera de límites se lanza un error de rango | ✅ | 2026-10-09 | 📘 |
| [ADR-008](02_norma_y_calculo.md#adr-008) | Redondeo decimal exacto; solo se redondea el CTPL final | ✅ | 2026-10-09 | 📘 |
| [ADR-009](02_norma_y_calculo.md#adr-009) | CTL desde densidad observada sin redondear la densidad base intermedia | ✅ | 2026-10-09 | 👤 |
| [ADR-010](02_norma_y_calculo.md#adr-010) | Presión en kPa o bar con `pressure_unit` obligatorio en 11.1.7 | ✅ | 2026-10-09 | 👤 |
| [ADR-011](02_norma_y_calculo.md#adr-011) | `alpha_60` solo para el tipo C; CTL sin densidad con `ctl_from_alpha` | ✅ | 2026-10-09 | 📘 |
| [ADR-012](02_norma_y_calculo.md#adr-012) | Máximo de 15 iteraciones; `iterations` es el índice m de la norma | ✅ | 2026-10-09 | 📘 |
| [ADR-013](02_norma_y_calculo.md#adr-013) | Conservar el cambio de subgrupo entre iteraciones (tipo B) | ✅ | 2026-10-09 | 📘 |
| [ADR-014](02_norma_y_calculo.md#adr-014) | Densidad alterna de 11.1.7.1 con el CTPL sin redondear | ✅ | 2026-10-09 | 🔧 |
| [ADR-015](02_norma_y_calculo.md#adr-015) | Base métrica solo 15/20 °C; ITS-90 devuelve la unidad de entrada | ✅ | 2026-10-09 | 📘 |

### API pública

| ID | Decisión | Estado | Fecha | Decidido por |
|---|---|:---:|---|:---:|
| [ADR-016](03_api_publica.md#adr-016) | Ruptura limpia de la API, sin alias de compatibilidad | ✅ | 2026-10-09 | 👤 |
| [ADR-017](03_api_publica.md#adr-017) | Argumentos solo por nombre y resultados `NamedTuple` | ✅ | 2026-10-09 | 🔧 |
| [ADR-018](03_api_publica.md#adr-018) | Tres puntos de importación públicos | ✅ | 2026-10-13 | 🔧 |
| [ADR-019](03_api_publica.md#adr-019) | Mensajes de error en ASCII; validación en las unidades del usuario | ✅ | 2026-10-13 | 🔧 |
| [ADR-020](03_api_publica.md#adr-020) | Generador de tablas como script fuera del paquete | ✅ | 2026-10-09 | 🔧 |

### Calidad y documentación

| ID | Decisión | Estado | Fecha | Decidido por |
|---|---|:---:|---|:---:|
| [ADR-021](04_calidad_y_documentacion.md#adr-021) | Ejemplos de la norma y de la documentación como pruebas automáticas | ✅ | 2026-10-09 | 🔧 |
| [ADR-022](04_calidad_y_documentacion.md#adr-022) | CI en Python 3.9 y 3.12; no se agrega 3.13 | ✅ | 2026-10-13 | 👤 |
| [ADR-023](04_calidad_y_documentacion.md#adr-023) | Documentación en español; la del integrador no explica el cálculo | ✅ | 2026-10-13 | 👤 |
| [ADR-024](04_calidad_y_documentacion.md#adr-024) | Informes de auditoría por hallazgo con porcentaje de cierre | ✅ | 2026-10-09 | 👤 |

### Versionado y distribución

| ID | Decisión | Estado | Fecha | Decidido por |
|---|---|:---:|---|:---:|
| [ADR-025](05_versionado_y_distribucion.md#adr-025) | Versión derivada del tag de git (setuptools-scm); primera versión `v1.0.0` | ✅ | 2026-10-13 | 👤 |
| [ADR-026](05_versionado_y_distribucion.md#adr-026) | Publicar versiones ofuscadas con Cython en wheels por plataforma | 🟡 | 2026-10-13 | 👤 |
| [ADR-027](05_versionado_y_distribucion.md#adr-027) | Sin archivos de tipos `.pyi` en los wheels | 🟡 | 2026-10-13 | 👤 |
| [ADR-028](05_versionado_y_distribucion.md#adr-028) | Configuración de build en `packaging/` del repositorio principal | 🟡 | 2026-10-13 | 👤 |
| [ADR-029](05_versionado_y_distribucion.md#adr-029) | Distribuir por GitHub Releases y una rama `dist`, sin índice de paquetes | 🟡 | 2026-10-13 | 👤 |
| [ADR-030](05_versionado_y_distribucion.md#adr-030) | Liberación automatizada desde el repositorio personal con GitHub Actions | 🟡 | 2026-10-13 | 👤 |

---

<a id="pendientes"></a>
## 3. Decisiones pendientes

| ID | Pregunta | Recomendación | Bloquea |
|---|---|---|---|
| [PEND-1](06_pendientes.md#pend-1) | ¿La rama `dist` guarda solo la última versión o todas? | Una carpeta por versión | [ADR-029](05_versionado_y_distribucion.md#adr-029) |
| [PEND-2](06_pendientes.md#pend-2) | ¿Se siguen compilando wheels para Python 3.9? | Mantenerlo si la herramienta lo permite | [ADR-026](05_versionado_y_distribucion.md#adr-026) |
| [PEND-3](06_pendientes.md#pend-3) | ¿Se sigue documentando la instalación desde el código fuente? | Solo para desarrollo | [ADR-029](05_versionado_y_distribucion.md#adr-029) |

---

<a id="nueva"></a>
## 4. Cómo registrar una decisión nueva

1. Usar el siguiente número libre (`ADR-031`, …) en el documento del área que corresponda.
2. Copiar la plantilla y agregar la fila al [índice](#indice).
3. Si reemplaza otra decisión, marcar la anterior como ❌ y enlazarlas en ambos sentidos.

```markdown
<a id="adr-0NN"></a>
## ADR-0NN · Título corto en forma de decisión

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | AAAA-MM-DD | 👤 Usuario | commit `abc1234`, enlace a la prueba o documento |

**Contexto.** Qué problema o pregunta obligó a decidir.

**Decisión.** Qué se decidió, en una o dos frases.

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|

**Consecuencias.** Qué implica, qué se gana y qué se paga.
```
