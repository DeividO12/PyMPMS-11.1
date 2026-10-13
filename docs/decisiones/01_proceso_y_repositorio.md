# 01 · Proceso y repositorio

[⬅ Índice](README.md) · [Siguiente: Norma y cálculo ➡](02_norma_y_calculo.md)

## 📑 Contenido

| ID | Decisión | Estado |
|---|---|:---:|
| [ADR-001](#adr-001) | Auditar la integridad del código por separado de la conformidad normativa | ✅ |
| [ADR-002](#adr-002) | Corregir verificando cada cambio contra la norma; la norma manda | ✅ |
| [ADR-003](#adr-003) | Commits por fase en `dev_deivid`; push solo cuando se pide | ✅ |
| [ADR-004](#adr-004) | Entorno `.venv` local; no modificar el Python global | ✅ |
| [ADR-005](#adr-005) | Repositorio de trabajo personal con espejo en `sistemasSYZ` | ✅ |
| [ADR-006](#adr-006) | Integrar `dev_deivid` en `master` con merge `--no-ff` | ✅ |

---

<a id="adr-001"></a>
## ADR-001 · Auditar la integridad del código por separado de la conformidad normativa

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 👤 Usuario | [Informe de auditoría](../informe_2026-10-09_1420/README.md) |

**Contexto.** La librería (commit `4f1216d`) no tenía pruebas automáticas y había dudas sobre su robustez. Revisar a la vez el código y la fidelidad a la norma mezclaba dos preguntas distintas.

**Decisión.** Primero, una auditoría solo de integridad del código: errores, casos no contemplados, optimizaciones y mantenibilidad. La conformidad con API MPMS 11.1 quedó fuera de esa fase.

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Auditar código y norma a la vez | Mezcla hallazgos de naturaleza distinta y dificulta priorizar |

**Consecuencias.** 38 hallazgos clasificados por severidad, con evidencia reproducible y un plan de acción. La revisión normativa se hizo en la fase de corrección ([ADR-002](#adr-002)).

---

<a id="adr-002"></a>
## ADR-002 · Corregir verificando cada cambio contra la norma; la norma manda

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 👤 Usuario | [Conformidad con la norma](../informe_2026-10-09_1420/10_conformidad_norma.md), anexos [A](../informe_2026-10-09_1420/11_anexo_norma_nucleo.md) y [B](../informe_2026-10-09_1420/12_anexo_norma_tablas.md) |

**Contexto.** «Esta librería se construyó para seguir la norma.» Varias correcciones de la auditoría (límites, redondeo, unidades) dependían de lo que dijera la norma.

**Decisión.** Cada corrección se verificó en paralelo contra `PDFs/API MPMS 11.1.pdf`. Ante un conflicto entre la conveniencia del código y la norma, **prevalece la norma**. Cuando la norma es ambigua, se documenta la interpretación elegida (ver [ADR-014](02_norma_y_calculo.md#adr-014)).

**Consecuencias.** El núcleo reproduce 49 ejemplos resueltos y los 9 996 valores de las tablas de muestra. Las decisiones normativas de este registro se marcan con 📘 y citan la página del PDF. El PDF no se versiona (`.gitignore`, `PDFs/`).

---

<a id="adr-003"></a>
## ADR-003 · Commits por fase en `dev_deivid`; push solo cuando se pide

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 👤 Usuario | `git log 4f1216d..v1.0.0` |

**Contexto.** La corrección tocaba casi todo el código; un único commit gigante haría imposible revisar o revertir partes.

**Decisión.** Un commit por fase o bloque coherente (pruebas, estructura, validación, redondeo, núcleo normativo, documentación…) en la rama `dev_deivid`, con mensajes descriptivos en español. Publicar en el remoto (`git push`) solo cuando el usuario lo pide expresamente.

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Sin commits, todo en el árbol de trabajo | Revisión difícil y sin puntos de retorno |
| Rama nueva por la corrección | Innecesaria: `dev_deivid` ya es la rama de trabajo |

**Consecuencias.** 15 commits entre `4f1216d` y `v1.0.0`, cada uno con las pruebas en verde.

---

<a id="adr-004"></a>
## ADR-004 · Entorno `.venv` local; no modificar el Python global

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 👤 Usuario | `.venv` (ignorado en git), `pip install -e ".[dev,tables]"` |

**Contexto.** Las pruebas necesitaban pytest, numpy y pandas, que no estaban instalados.

**Decisión.** Entorno virtual `.venv` en el repositorio, instalado en modo editable con los extras de desarrollo y tablas. El Python global no se toca, ni siquiera para corregir vulnerabilidades encontradas por `pip-audit` (se informan y el usuario decide).

**Consecuencias.** Entorno reproducible y aislado. Las pruebas en otras versiones de Python (3.9, 3.13) se hicieron en entornos temporales con rutas cortas, por el límite de 260 caracteres de Windows.

---

<a id="adr-005"></a>
## ADR-005 · Repositorio de trabajo personal con espejo en `sistemasSYZ`

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-13 | 👤 Usuario | commit `7e5a41c` (README › Repositorios y versiones) |

**Contexto.** El código estaba en `DeividO12/PyMPMS-11.1` (cuenta personal), pero debe estar disponible en la organización `sistemasSYZ` para instalarse desde allí.

**Decisión.** Se trabaja en el repositorio personal y se replica a `sistemasSYZ/PyMPMS-11.1`. Mientras no exista la automatización de [ADR-030](05_versionado_y_distribucion.md#adr-030), el espejo se mantiene con **dos URLs de push** en `origin`: cada `git push origin` publica en ambos repositorios.

**Alternativas consideradas.**
| Alternativa | Por qué no (por ahora) |
|---|---|
| Mover el desarrollo a `sistemasSYZ` | El usuario prefiere trabajar en su repositorio |
| GitHub Action que replica | Requiere un token; se adoptará con la liberación automática ([ADR-030](05_versionado_y_distribucion.md#adr-030)) |

**Consecuencias.**
- El push doble solo existe en el clon configurado; en otro equipo hay que repetir dos comandos (documentados en el README).
- Lo que se edite desde la web de GitHub no se replica hasta el siguiente push.
- Existe además un remoto `syz` solo para verificar el espejo.

---

<a id="adr-006"></a>
## ADR-006 · Integrar `dev_deivid` en `master` con merge `--no-ff`

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-13 | 👤 Usuario | merge `2ca3fd7` (`v1.0.0`) |

**Contexto.** `master` debía recibir los cambios de `dev_deivid` para la primera versión.

**Decisión.** Merge con commit (`git merge --no-ff dev_deivid`) en `master`. El tag de versión se crea sobre ese commit de merge.

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Fast-forward | Historial lineal, pero no se distingue qué entró en cada versión |

**Consecuencias.** Cada versión queda agrupada en un commit de merge identificable en `master`.

---

[⬅ Índice](README.md) · [Siguiente: Norma y cálculo ➡](02_norma_y_calculo.md)
