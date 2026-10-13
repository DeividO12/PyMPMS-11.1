# 06 · Decisiones pendientes

[⬅ Anterior: Versionado y distribución](05_versionado_y_distribucion.md) · [Índice](README.md)

Preguntas abiertas que requieren una decisión. Al resolverse, cada una se convierte en un ADR en el documento de su área y pasa al historial.

## 📑 Contenido

1. [Pendientes abiertas](#abiertas)
2. [Historial de pendientes resueltas](#historial)

---

<a id="abiertas"></a>
## 1. Pendientes abiertas

No hay decisiones pendientes.

---

<a id="historial"></a>
## 2. Historial de pendientes resueltas

<a id="pend-1"></a>
### PEND-1 · ¿La rama `dist` guarda solo la última versión o todas?

| Opciones evaluadas | Recomendación | Resolución (2026-10-13) |
|---|---|---|
| Solo la última (como `pymlii`) · una carpeta por versión | Una carpeta por versión | Aceptada → [ADR-031](05_versionado_y_distribucion.md#adr-031) |

<a id="pend-2"></a>
### PEND-2 · ¿Se siguen compilando wheels para Python 3.9?

| Opciones evaluadas | Recomendación | Resolución (2026-10-13) |
|---|---|---|
| Mantener 3.9 · retirarlo de los wheels | Mantenerlo si las herramientas lo permiten | Aceptada; las herramientas lo soportan → [ADR-032](05_versionado_y_distribucion.md#adr-032) |

<a id="pend-3"></a>
### PEND-3 · ¿Se sigue documentando la instalación desde el código fuente?

| Opciones evaluadas | Recomendación | Resolución (2026-10-13) |
|---|---|---|
| Solo wheels para el integrador · ambas formas | Solo wheels; el código fuente en la guía de desarrollo | Aceptada → [ADR-033](05_versionado_y_distribucion.md#adr-033) |

---

[⬅ Anterior: Versionado y distribución](05_versionado_y_distribucion.md) · [Índice](README.md)
