# 05 · Versionado y distribución

[⬅ Anterior: Calidad y documentación](04_calidad_y_documentacion.md) · [Índice](README.md) · [Siguiente: Pendientes ➡](06_pendientes.md)

## 📑 Contenido

| ID | Decisión | Estado |
|---|---|:---:|
| [ADR-025](#adr-025) | Versión derivada del tag de git (setuptools-scm); primera versión `v1.0.0` | ✅ |
| [ADR-026](#adr-026) | Publicar versiones ofuscadas con Cython en wheels por plataforma | 🟡 |
| [ADR-027](#adr-027) | Sin archivos de tipos `.pyi` en los wheels | 🟡 |
| [ADR-028](#adr-028) | Configuración de build en `packaging/` del repositorio principal | 🟡 |
| [ADR-029](#adr-029) | Distribuir por GitHub Releases y una rama `dist`, sin índice de paquetes | 🟡 |
| [ADR-030](#adr-030) | Liberación automatizada desde el repositorio personal con GitHub Actions | 🟡 |
| [ADR-031](#adr-031) | La rama `dist` guarda una carpeta por versión | 🟡 |
| [ADR-032](#adr-032) | Se mantienen los wheels para Python 3.9 | 🟡 |
| [ADR-033](#adr-033) | La documentación del integrador muestra solo la instalación de wheels | 🟡 |
| [Flujo resultante](#flujo) | Cómo encajan ADR-025 a ADR-033 | — |

---

<a id="adr-025"></a>
## ADR-025 · Versión derivada del tag de git (setuptools-scm); primera versión `v1.0.0`

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-13 | 👤 Usuario | commit `24ba7bb`; tag `v1.0.0` sobre `2ca3fd7` |

**Contexto.** El usuario gestionará las versiones con tags. El código decía `0.2.0` mientras el primer tag sería `v1.0.0`: un paquete instalado desde el tag habría reportado una versión distinta.

**Decisión.**
- La versión **no se escribe en el código**. `setuptools-scm` la deriva del tag `vX.Y.Z` al instalar o construir, y genera `src/api_mpms/_version.py` (ignorado en git).
- Antes de crear un tag se verifica que no existan tags previos o en conflicto.
- La primera versión es `v1.0.0` (no había tags previos).
- Versionado semántico: un cambio incompatible sube la versión mayor ([ADR-016](03_api_publica.md#adr-016)).

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Fijar la versión en `__init__.py` y actualizarla a mano | El tag y el código pueden desalinearse |

**Consecuencias.**
- Entre tags la versión es de desarrollo (`1.0.1.devN+g<hash>`).
- La CI hace checkout con el historial completo (`fetch-depth: 0`) para ver los tags.
- Instalar desde una copia del código sin historial de git da `0+unknown`.

---

<a id="adr-026"></a>
## ADR-026 · Publicar versiones ofuscadas con Cython en wheels por plataforma

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| 🟡 Aceptada, pendiente de implementar | 2026-10-13 | 👤 Usuario | Prueba de concepto del 2026-10-13 (abajo); antecedente: `pymlii` (`packaging/README.md`) |

**Contexto.** Se desarrolla y mantiene el código fuente, pero se quieren publicar versiones en las que el código no sea legible. Se instala en Linux y Windows, de Python 3.9 a 3.13.

**Decisión.**
- Compilar con **Cython** todos los módulos excepto los `__init__.py`.
- Distribuir **wheels binarios por plataforma y versión de Python**: Windows x64 y Linux x64 (manylinux), CPython 3.9 a 3.13. Son 10 wheels por versión.
- Opciones obligatorias de compilación:

| Opción | Motivo |
|---|---|
| `annotation_typing=False` | Sin ella, Cython convierte las anotaciones en comprobaciones de tipo en C y un dato inválido lanza `TypeError` en lugar de `MPMSValidationError` (9 pruebas fallaron en la prueba de concepto) |
| `-ffp-contract=off` en Linux | Impide que el compilador fusione operaciones de punto flotante y cambie el último decimal |
| Quitar los símbolos de depuración de los `.so` de Linux | Como en `pymlii`: menos información interna y menos tamaño |
| Pruebas contra cada wheel instalado | Lo que se publica es exactamente lo que se probó |

**Prueba de concepto (Windows, Python 3.12, Cython 3.3).**
| Verificación | Resultado |
|---|---|
| Compilación | 19 módulos, sin cambiar el código fuente; Cython compila los `.py` directamente |
| Pruebas contra el binario (sin los `.py`) | 497 pasan, 1 omitida (generador, sin pandas) |
| Resultados | Huella sha256 de 80 000 resultados **idéntica** a la de Python puro |
| Rendimiento | ~8 % más rápido (no es motivo para compilar) |
| Qué queda oculto | Estructura del cálculo, comentarios, nombres internos, constantes como texto |
| Qué sigue visible | Nombres de funciones y parámetros públicos, docstrings, fragmentos de mensajes |

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Wheel único de Python puro | No oculta el código |
| Wheels solo con `.pyc` | Se descompilan con facilidad y también dependen de la versión de Python |
| API estable de Python (`abi3`, 2 wheels) | Soporte aún experimental en Cython; se puede evaluar más adelante |
| PyArmor / Nuitka | Más dependencias o licencias, para un beneficio similar |

**Consecuencias.**
- La protección dificulta la lectura y la modificación casual, pero no impide la ingeniería inversa. Las fórmulas son públicas en la norma; lo que se protege es la implementación.
- Cada versión nueva de Python exige compilar wheels nuevos.
- Las pruebas que inspeccionan el código fuente no aplican al wheel (hoy no hay ninguna).

---

<a id="adr-027"></a>
## ADR-027 · Sin archivos de tipos `.pyi` en los wheels

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| 🟡 Aceptada, pendiente de implementar | 2026-10-13 | 👤 Usuario | — |

**Contexto.** Al compilar se pierde la información de tipos para el autocompletado de los editores. Se propuso generar `.pyi` con las firmas públicas.

**Decisión.** No se generan. El integrador se apoya en la [documentación API](../api/README.md).

**Consecuencias.** En los wheels compilados conviene no incluir `py.typed`: ese archivo declara que el paquete trae tipos, y sin `.pyi` sería falso.

---

<a id="adr-028"></a>
## ADR-028 · Configuración de build en `packaging/` del repositorio principal

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| 🟡 Aceptada, pendiente de implementar | 2026-10-13 | 👤 Usuario | Mismo esquema que `pymlii` (`packaging/build_release.py`) |

**Contexto.** No se quiere subir código Cython a git. No es posible crear un repositorio aparte solo para el build. Se planteó usar una rama dedicada.

**Decisión.**
- La configuración de compilación vive en una carpeta `packaging/` y el workflow en `.github/workflows/`, ambos en `master`.
- No es código Cython: el código sigue siendo Python puro, y los `.c` y binarios se generan dentro del build y **nunca se versionan**.

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Repositorio aparte solo para el build | No se puede crear |
| Rama dedicada para el build | GitHub ejecuta el workflow de un tag desde el commit etiquetado: la configuración tiene que estar en ese commit, no en otra rama |

**Consecuencias.** La rama dedicada sí se usa, pero para **distribuir** los wheels ([ADR-029](#adr-029)).

---

<a id="adr-029"></a>
## ADR-029 · Distribuir por GitHub Releases y una rama `dist`, sin índice de paquetes

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| 🟡 Aceptada, pendiente de implementar | 2026-10-13 | 👤 Usuario | Verificaciones de acceso documentadas en `pymlii` (`packaging/README.md`, 2026-08-21) |

**Contexto.** No hay índice de paquetes privado, y siempre es SYZ quien instala la librería.

**Decisión.** Cada versión se publica en `sistemasSYZ/PyMPMS-11.1`:

| Canal | Uso |
|---|---|
| **GitHub Release** del tag, con los wheels como assets | Archivo de todas las versiones: `gh release download vX.Y.Z` y luego `pip install ./archivo.whl` |
| **Rama `dist`** con los wheels guardados en git | `pip install` en un solo comando desde `raw.githubusercontent.com` con un token |

No se publica el paquete con el código fuente (sdist).

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Índice privado (pypiserver, Azure Artifacts, CodeArtifact) | Infraestructura nueva para un solo consumidor |
| Solo `pip install` desde el asset del Release | No funciona: pip no puede descargar assets de un Release privado (verificado en `pymlii`) |
| Seguir instalando desde git (`git+https://…`) | Instala el código fuente |

**Consecuencias.**
- Quien instala necesita un token con lectura sobre el repositorio de SYZ, y el nombre exacto del wheel de su plataforma y versión de Python.
- La rama guarda una carpeta por versión: [ADR-031](#adr-031).
- La documentación del integrador solo muestra la instalación de wheels: [ADR-033](#adr-033).

---

<a id="adr-030"></a>
## ADR-030 · Liberación automatizada desde el repositorio personal con GitHub Actions

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| 🟡 Aceptada, pendiente de implementar | 2026-10-13 | 👤 Usuario | `gh run list`: el CI corrió en verde en `DeividO12/PyMPMS-11.1` **y** en `sistemasSYZ/PyMPMS-11.1` (2026-10-13) |

**Contexto.** En `pymlii` la liberación es manual porque GitHub Actions no se ejecuta en ese repositorio. Aquí se comprobó que Actions sí funciona en los dos repositorios.

**Decisión.** Al hacer push de un tag `vX.Y.Z` al repositorio personal, un workflow:

1. Valida: ruff, mypy y las pruebas.
2. Compila los wheels con **cibuildwheel** en Windows y Linux ([ADR-026](#adr-026)) y prueba cada uno.
3. Replica ramas y tags en `sistemasSYZ` (reemplaza el push doble de [ADR-005](01_proceso_y_repositorio.md#adr-005)).
4. Crea el Release en SYZ con los wheels y actualiza la rama `dist` ([ADR-029](#adr-029)).

El workflow solo se ejecuta en el repositorio personal (condición sobre `github.repository`), para que el espejo no lo repita.

**Requisitos.**
| Requisito | Responsable |
|---|---|
| Token de acceso con escritura en `sistemasSYZ/PyMPMS-11.1`, guardado como secreto `SYZ_RELEASE_TOKEN` del repositorio personal. **Clásico con `repo` y `workflow`**: la cuenta es colaboradora externa de la organización y no puede usar tokens de grano fino sobre sus repositorios privados (ver [`packaging/README.md`](../../packaging/README.md#configuracion)). Configurado el 2026-10-13. | Usuario ✅ |
| Unos 25 minutos de Actions por versión (los de Windows cuentan doble); cabe en los 2000 minutos mensuales del plan gratuito para repos privados | — |

**Implementación.** [`packaging/`](../../packaging/README.md), [`release.yml`](../../.github/workflows/release.yml) y [`mirror.yml`](../../.github/workflows/mirror.yml). Pasa a ✅ con la primera publicación real.

**Consecuencias.** El único paso manual de una versión es crear el tag y hacer push. El espejo pasa a funcionar también para cambios hechos desde la web de GitHub.

---

<a id="adr-031"></a>
## ADR-031 · La rama `dist` guarda una carpeta por versión

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| 🟡 Aceptada, pendiente de implementar | 2026-10-13 | 👤 Usuario (antes [PEND-1](06_pendientes.md#pend-1)) | — |

**Contexto.** `pymlii` rehace su rama `dist/latest` en cada versión, así que solo la última se instala con un único comando.

**Decisión.** La rama `dist` de `sistemasSYZ/PyMPMS-11.1` acumula una carpeta por versión (`vX.Y.Z/`) con sus wheels. Cualquier versión se instala con un solo `pip install <URL>`.

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Solo la última versión (como `pymlii`) | Para fijar una versión anterior en un despliegue hacen falta dos pasos |

**Consecuencias.** La rama crece con cada versión. Medido el 2026-10-13 en el build de prueba: **~4.5 MB por versión** (10 wheels de 406 a 489 KB).

---

<a id="adr-032"></a>
## ADR-032 · Se mantienen los wheels para Python 3.9

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| 🟡 Aceptada, pendiente de implementar | 2026-10-13 | 👤 Usuario (antes [PEND-2](06_pendientes.md#pend-2)) | Verificado el 2026-10-13: cibuildwheel 4.3.1 lista `cp39-win_amd64` y `cp39-manylinux_x86_64`; Cython 3.3.0 publica wheel `cp39` |

**Contexto.** Python 3.9 ya no recibe soporte oficial; podía ocurrir que las herramientas de compilación lo hubieran retirado.

**Decisión.** Se compilan wheels para Python 3.9 a 3.13 (10 por versión) mientras haya equipos de SYZ que usen 3.9 y las herramientas lo permitan. Las versiones de cibuildwheel y Cython se **fijan** en la configuración de build, para que una actualización no retire 3.9 sin aviso y para que un binario se pueda reconstruir.

**Consecuencias.** Cuando las herramientas fijadas dejen de soportar 3.9, se registra una decisión nueva que la retire.

---

<a id="adr-033"></a>
## ADR-033 · La documentación del integrador muestra solo la instalación de wheels

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| 🟡 Aceptada, pendiente de implementar | 2026-10-13 | 👤 Usuario (antes [PEND-3](06_pendientes.md#pend-3)) | — |

**Contexto.** Hoy el README y la documentación API indican `pip install "pympms-11-1 @ git+https://…"`, que instala el código fuente: contradice el objetivo de la distribución ofuscada en los equipos de destino.

**Decisión.** El README y la documentación API muestran solo la instalación de wheels (desde el Release o la rama `dist`). La instalación desde git o desde una copia local queda en la sección de desarrollo.

**Consecuencias.** La documentación se actualiza cuando exista la primera versión con wheels publicados.

---

<a id="flujo"></a>
## Flujo resultante

```text
Desarrollo (dev_deivid, Python puro)
        │  merge --no-ff                                          ADR-006
        ▼
master ── git tag -a vX.Y.Z ── git push ─────────────────────────  ADR-025
        │
        ▼  GitHub Actions en DeividO12/PyMPMS-11.1                 ADR-030
   1. ruff + mypy + pruebas
   2. cibuildwheel: Windows y Linux × Python 3.9–3.13              ADR-026
      (Cython, annotation_typing=False, sin .pyi, pruebas por wheel)  ADR-027
   3. espejo de ramas y tags ──────────► sistemasSYZ/PyMPMS-11.1    ADR-005
   4. Release vX.Y.Z + rama dist/vX.Y.Z ► sistemasSYZ/PyMPMS-11.1   ADR-029, ADR-031
        │
        ▼
SYZ instala el wheel de su plataforma (gh release download / pip install <URL>)
```

---

[⬅ Anterior: Calidad y documentación](04_calidad_y_documentacion.md) · [Índice](README.md) · [Siguiente: Pendientes ➡](06_pendientes.md)
