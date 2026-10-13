# 06 · Decisiones pendientes

[⬅ Anterior: Versionado y distribución](05_versionado_y_distribucion.md) · [Índice](README.md)

Preguntas abiertas que hay que resolver antes de implementar la distribución ofuscada. Al decidir, cada una se convierte en un ADR en el documento de su área y se elimina de aquí.

## 📑 Contenido

| ID | Pregunta | Recomendación | Bloquea |
|---|---|---|---|
| [PEND-1](#pend-1) | ¿La rama `dist` guarda solo la última versión o todas? | Una carpeta por versión | [ADR-029](05_versionado_y_distribucion.md#adr-029) |
| [PEND-2](#pend-2) | ¿Se siguen compilando wheels para Python 3.9? | Mantenerlo si la herramienta lo permite | [ADR-026](05_versionado_y_distribucion.md#adr-026) |
| [PEND-3](#pend-3) | ¿Se sigue documentando la instalación desde el código fuente? | Solo para desarrollo | [ADR-029](05_versionado_y_distribucion.md#adr-029) |

---

<a id="pend-1"></a>
## PEND-1 · ¿La rama `dist` guarda solo la última versión o todas?

| Opción | A favor | En contra |
|---|---|---|
| **Solo la última** (como `pymlii`: rama huérfana rehecha en cada versión) | La rama siempre pesa lo mismo; mismo esquema que `pymlii` | Una versión anterior solo se instala en dos pasos (`gh release download` y luego `pip install`) |
| **Una carpeta por versión** (`dist/v1.1.0/…`) | Cualquier versión se instala con un solo `pip install <URL>`, útil para fijar versiones en despliegues | La rama crece con cada versión (estimado: del orden de 10 MB por versión; se mide al implementar) |

**Recomendación:** una carpeta por versión. Los wheels de esta librería son pequeños (los binarios de la prueba de concepto sumaron ~1 MB por plataforma y versión de Python) y poder fijar cualquier versión en un solo comando simplifica los despliegues.

---

<a id="pend-2"></a>
## PEND-2 · ¿Se siguen compilando wheels para Python 3.9?

**Contexto.** Python 3.9 dejó de recibir soporte oficial en octubre de 2025. El código fuente funciona en 3.9 (lo verifica la CI), pero las versiones recientes de las herramientas de compilación pueden haber retirado su soporte.

| Opción | Implica |
|---|---|
| **Mantener 3.9** | Confirmar que cibuildwheel y Cython lo soportan; si no, fijar versiones anteriores de esas herramientas |
| **Retirar 3.9 de los wheels** | 8 wheels por versión. Los equipos con 3.9 tendrían que actualizar Python o quedarse en una versión anterior |

**Recomendación:** mantener 3.9 mientras haya equipos de SYZ que lo usen y las herramientas lo permitan. Se confirma al implementar.

---

<a id="pend-3"></a>
## PEND-3 · ¿Se sigue documentando la instalación desde el código fuente?

**Contexto.** Hoy la documentación indica `pip install "pympms-11-1 @ git+https://github.com/sistemasSYZ/PyMPMS-11.1.git@vX.Y.Z"`, que instala **el código fuente**. Con versiones ofuscadas, eso contradice el objetivo en los equipos de destino.

| Opción | Implica |
|---|---|
| **Solo wheels en la documentación del integrador; código fuente solo en la guía de desarrollo** | Los despliegues usan siempre el binario |
| Documentar ambas formas | Riesgo de instalar el código fuente en un equipo de destino por costumbre |

**Recomendación:** la documentación API y el README muestran solo la instalación de wheels. La instalación desde git queda en la sección de desarrollo.

---

[⬅ Anterior: Versionado y distribución](05_versionado_y_distribucion.md) · [Índice](README.md)
