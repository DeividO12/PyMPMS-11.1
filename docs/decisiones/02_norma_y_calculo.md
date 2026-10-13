# 02 · Norma y cálculo

[⬅ Anterior: Proceso y repositorio](01_proceso_y_repositorio.md) · [Índice](README.md) · [Siguiente: API pública ➡](03_api_publica.md)

Cómo interpreta la librería API MPMS 11.1 (2004). Las páginas citadas son del PDF (`PDFs/API MPMS 11.1.pdf`). El detalle de cada punto está en los anexos [A (núcleo)](../informe_2026-10-09_1420/11_anexo_norma_nucleo.md) y [B (tablas)](../informe_2026-10-09_1420/12_anexo_norma_tablas.md).

## 📑 Contenido

| ID | Decisión | Estado |
|---|---|:---:|
| [ADR-007](#adr-007) | No extrapolar: fuera de límites se lanza un error de rango | ✅ |
| [ADR-008](#adr-008) | Redondeo decimal exacto; solo se redondea el CTPL final | ✅ |
| [ADR-009](#adr-009) | CTL desde densidad observada sin redondear la densidad base intermedia | ✅ |
| [ADR-010](#adr-010) | Presión en kPa o bar con `pressure_unit` obligatorio en 11.1.7 | ✅ |
| [ADR-011](#adr-011) | `alpha_60` solo para el tipo C; CTL sin densidad con `ctl_from_alpha` | ✅ |
| [ADR-012](#adr-012) | Máximo de 15 iteraciones; `iterations` es el índice m de la norma | ✅ |
| [ADR-013](#adr-013) | Conservar el cambio de subgrupo entre iteraciones (tipo B) | ✅ |
| [ADR-014](#adr-014) | Densidad alterna de 11.1.7.1 con el CTPL sin redondear | ✅ |
| [ADR-015](#adr-015) | Base métrica solo 15/20 °C; ITS-90 devuelve la unidad de entrada | ✅ |

---

<a id="adr-007"></a>
## ADR-007 · No extrapolar: fuera de límites se lanza un error de rango

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 📘 Norma — 11.1.2.3 (pág. 15), 11.1.6.1 paso 1 (págs. 40-41), 11.1.6.2 pasos 1 y 7 (págs. 57-59) | commits `62fc683`, `5b0e53a`; 30 casos de error de la norma en [`test_norm_examples.py`](../../tests/test_norm_examples.py) |

**Contexto.** La versión auditada asignaba el «grupo más cercano» a cualquier densidad, aunque fuera absurda (5000 kg/m³ o negativa), y reportaba las entradas fuera de rango como error de convergencia.

**Decisión.**
- Se validan los límites de la norma, todos **inclusivos**: temperatura, presión, α60, ρ60 por tipo y ρo observada por tipo (tabla de la pág. 57).
- Fuera de límites se lanza `MPMSRangeError`. Nunca se extrapola ni se devuelve 0.
- Tres excepciones distintas:

| Excepción | Cuándo |
|---|---|
| `MPMSRangeError` (subclase de `MPMSValidationError`) | Dato válido fuera de los límites, o densidad base resultante fuera de límites |
| `MPMSValidationError` | Dato inválido: tipo, `NaN`, combinación de parámetros |
| `MPMSConvergenceError` | No convergencia real. Guarda `last_result`, porque la nota del paso 6 (pág. 59) permite usar la última iteración marcada |

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Devolver ceros como «condición de error» (lo sugiere la norma como ejemplo) | Un 0 se confunde con un dato válido |
| Extrapolar con advertencia | La norma dice «set an error condition and exit» |

**Consecuencias.**
- Si al agotar las iteraciones la densidad base está anclada a un límite, se informa como **error de rango**, como en el ejemplo 7.2-17 (pág. 116).
- La validación se omite dentro de la iteración de 11.1.6.2 («Do not check», pág. 57).

---

<a id="adr-008"></a>
## ADR-008 · Redondeo decimal exacto; solo se redondea el CTPL final

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 📘 Norma — 11.1.5.4 (págs. 37-39), 11.1.3.9 (pág. 28), 11.1.5 (pág. 29) | commits `968c0fe`, `5b0e53a`, `869cc63`; [`test_rounding.py`](../../tests/test_rounding.py) |

**Contexto.** `api_round` detectaba los empates en coma flotante binaria y fallaba en el 26 % de los empates de CTL ([N-01](../informe_2026-10-09_1420/03_precision_numerica.md#n-01)). Además, el CTPL nunca se redondeaba.

**Decisión.**
1. Los empates se resuelven al par interpretando el número **como el decimal escrito**. Así lo trata la norma en su ejemplo: 10.05 / 0.1 = 100.5 exacto → 10.0.
2. Se calcula con `decimal` cerca de un empate y en coma flotante lejos de él. Ambas vías dan resultados idénticos: verificado con 720 000 casos.
3. Solo se redondea el **CTPL final** (`ctpl_rounded`, a 0.00001). Los valores intermedios nunca se redondean.
4. Las entradas se redondean solo en las funciones de tabla (`api_mpms.tables`).

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Tolerancia mayor en la comparación binaria | Sigue fallando en otras magnitudes |
| Solo `Decimal` | Correcto, pero unas 3.5 veces más lento (3.9 frente a 1.1 µs por llamada) |

**Consecuencias.** Algunos valores de tabla cambiaron en el último decimal respecto a la versión auditada (eran incorrectos). Cada resultado de corrección incluye `ctpl_rounded`, el factor de volumen oficial.

---

<a id="adr-009"></a>
## ADR-009 · CTL desde densidad observada sin redondear la densidad base intermedia

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 👤 Usuario (opción «normativo, con otro nombre»), con base en 11.1.3.9 (pág. 28) | commit `5b0e53a`; [NORM-T10](../informe_2026-10-09_1420/12_anexo_norma_tablas.md#norm-t10) |

**Contexto.** `table_5x_6x`, `table_23x_24x`, `table_53x_54x` y `table_59x_60x` emulaban la consulta manual de dos tablas: buscaban la densidad base, la **redondeaban** y luego buscaban el CTL. La norma prohíbe redondear valores intermedios. Ambos métodos difieren en el 20-60 % de los casos, hasta 23×10⁻⁵.

**Decisión.** Se reemplazaron por `ctl_from_observed_api`, `ctl_from_observed_relative_density`, `ctl_from_observed_density_15c` y `ctl_from_observed_density_20c`, que devuelven el CTL directo de 11.1.6.2 o 11.1.7.2.

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| Mantener ambas variantes (la manual renombrada como no normativa) | Una variante no normativa invita a usarla por error |
| Dejarlas igual | Contradice la norma |

**Consecuencias.** Cambio incompatible, documentado en `CHANGELOG.md`. Los resultados pueden diferir de los anteriores en el quinto decimal.

---

<a id="adr-010"></a>
## ADR-010 · Presión en kPa o bar con `pressure_unit` obligatorio en 11.1.7

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 👤 Usuario (unidad obligatoria), con base en 11.1.7.1/11.1.7.2 (págs. 89-90, 101-102) | commits `5b0e53a`, `2e12236`; 17 ejemplos de 11.1.7 en las pruebas |

**Contexto.** Las funciones métricas tomaban la presión como psig. La norma la pide en kPa o bar y devuelve Fp en kPa⁻¹ o bar⁻¹: con 1235 kPa, el CTPL salía 1.4 % desviado.

**Decisión.** Parámetro `pressure_unit` (`"kPa"` o `"bar"`) **obligatorio y sin valor por defecto**, para que nadie pase psig por error. Fp se devuelve en la misma unidad. Desde `2e12236`, la temperatura (°C) y la presión se validan en las unidades del usuario antes de calcular.

**Alternativas consideradas.**
| Alternativa | Por qué no |
|---|---|
| `"kPa"` por defecto | Un valor en bar o psig pasaría sin aviso |

**Consecuencias.** Las funciones se renombraron: `correct_metric_base_to_alternate` (11.1.7.1) y `correct_metric_observed_to_base` (11.1.7.2).

---

<a id="adr-011"></a>
## ADR-011 · `alpha_60` solo para el tipo C; CTL sin densidad con `ctl_from_alpha`

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 📘 Norma — págs. 39 y 55 (grupo **o** α60), pág. 40 (230–930×10⁻⁶ °F⁻¹), págs. 187 y 190 (tablas C a P = 0) | commits `b21e5d8`, `62fc683`, `5b0e53a` |

**Contexto.** Las tablas C pasaban una densidad ficticia de 0, que solo funcionaba por efectos laterales de la implementación. Además, se aceptaba α junto con los tipos A, B o D.

**Decisión.**
- `alpha_60` es exclusivo del tipo C. Con A, B o D lanza `MPMSValidationError`.
- α60 debe estar entre 230 y 930×10⁻⁶ °F⁻¹.
- `ctl_from_alpha` calcula el CTL sin densidad (P = 0).
- Con presión distinta de 0 se exige densidad, porque Fp la necesita.

**Consecuencias.** `alpha_60 = 0` ya no se confunde con «no informado»: es un error de rango. Las tablas 6C, 24C, 54C y 60C también redondean α a 0.1×10⁻⁶ °F⁻¹ o 0.2×10⁻⁶ °C⁻¹ (págs. 187 y 190).

---

<a id="adr-012"></a>
## ADR-012 · Máximo de 15 iteraciones; `iterations` es el índice m de la norma

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 📘 Norma — paso 6 (pág. 59) y ejemplo 7.2-17 (pág. 116) | 9 ejemplos de 11.1.6.2 comparan `iterations` |

**Contexto.** El texto del paso 6 admite leerse como 16 evaluaciones; el ejemplo de la pág. 116 muestra m = 0…14 y «after 15 iterations».

**Decisión.** 15 evaluaciones (m = 0…14), como en el ejemplo. `iterations` devuelve el índice m en que converge, que coincide con los 9 ejemplos de la norma.

---

<a id="adr-013"></a>
## ADR-013 · Conservar el cambio de subgrupo entre iteraciones (tipo B)

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 📘 Norma — pág. 55 («sub-group switching is automatically performed») y pág. 58 | Ejemplos 6.2-5, 6.2-6, 7.2-1, 7.2-6 y 7.2-7 |

**Contexto.** La auditoría marcó como riesgo ([F-10](../informe_2026-10-09_1420/01_errores_funcionales.md#f-10)) que el subgrupo de productos refinados pudiera cambiar durante la iteración.

**Decisión.** Se conserva: la norma lo exige. No se «congela» el subgrupo. El extremo 1163.5 kg/m³ de fuel oils es inclusivo y usa Da = 1.3 (pág. 58).

---

<a id="adr-014"></a>
## ADR-014 · Densidad alterna de 11.1.7.1 con el CTPL sin redondear

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 🔧 Técnica — la norma es ambigua: paso 5 (pág. 91) frente a sus ejemplos | [NORM-28](../informe_2026-10-09_1420/11_anexo_norma_nucleo.md#norm-28); [guía G9](../api/02_guias.md#g9) |

**Contexto.** La fórmula del paso 5 es ρ = CTL · CPL · ρT, sin redondear. Los ejemplos impresos de 11.1.7.1 usan en cambio ρT × CTPL redondeado (811.030845 frente a 811.0328506).

**Decisión.** Se sigue la **fórmula** (sin redondear), igual que en 11.1.6.1. La documentación explica cómo obtener el valor de los ejemplos (`rho_base * res.ctpl_rounded`).

---

<a id="adr-015"></a>
## ADR-015 · Base métrica solo 15/20 °C; ITS-90 devuelve la unidad de entrada

| Estado | Fecha | Decidido por | Evidencia |
|---|---|---|---|
| ✅ Aceptada | 2026-10-09 | 📘 Norma — 11.1.3.1 (pág. 22), 11.1.5.3 (págs. 36-37) | commits `b21e5d8`, `5b0e53a` |

**Decisión.**
- `t_base_c` solo admite 15 o 20 °C y es obligatorio.
- `its90_to_ipts68` recibe **exactamente una** temperatura y la devuelve en su misma unidad.
- Las funciones de corrección reciben temperaturas ITS-90 y hacen el ajuste a IPTS-68 internamente: el integrador no tiene que llamarlo.

---

[⬅ Anterior: Proceso y repositorio](01_proceso_y_repositorio.md) · [Índice](README.md) · [Siguiente: API pública ➡](03_api_publica.md)
