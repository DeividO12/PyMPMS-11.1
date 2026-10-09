# 11 · Anexo A — Verificación normativa del núcleo (11.1.2–11.1.7)

[⬅ Anterior: Conformidad con la norma](10_conformidad_norma.md) · [Índice](README.md) · [Siguiente: Anexo B — Tablas ➡](12_anexo_norma_tablas.md)

> [!NOTE]
> Este anexo describe el código del commit auditado `4f1216d`, **antes** de las correcciones.
> El estado actual de cada punto está en [10 · Conformidad con la norma](10_conformidad_norma.md).
> Las páginas citadas son páginas del PDF de API MPMS 11.1 (2004).

## 📑 Contenido

- [Resumen numérico de los ejemplos](#resumen-num-rico-de-los-ejemplos)
- [Hallazgos](#hallazgos)
  - [NORM-01 · 11.1.5.1: conversiones de densidad (agua 999.016, API, densidad relativa) — ✅ Conforme](#norm-01)
  - [NORM-02 · 11.1.5.1: temperatura, α y presión — ❌ No conforme (faltan conversiones)](#norm-02)
  - [NORM-03 · 11.1.5.3: ITS-90 → IPTS-68 — ✅ Conforme (interfaz ⚠️)](#norm-03)
  - [NORM-04 · 11.1.5.4: algoritmo de redondeo — ❌ No conforme en la detección de empates](#norm-04)
  - [NORM-05 · Política de redondeo: qué y cuándo — ❌ No conforme (CTPL nunca se redondea en las funciones de cálculo)](#norm-05)
  - [NORM-06 · 11.1.6.1: ecuaciones y constantes — ✅ Conforme](#norm-06)
  - [NORM-07 · 11.1.6.1 Paso 1: validación de ρ60 y α60 — ❌ No conforme](#norm-07)
  - [NORM-08 · 11.1.6.1/11.1.6.2: límites de temperatura y presión — ✅ Conforme (NaN ⚠️)](#norm-08)
  - [NORM-09 · 11.1.6.1: rama `rho_60 <= 0` → Fp = 0, CPL = 1 — ❌ No conforme (salvo P = 0)](#norm-09)
  - [NORM-10 · Asignación de subgrupo por densidad (tabla K y tabla Da) — ✅ Conforme en rango](#norm-10)
  - [NORM-11 · 11.1.6.2: esquema de Newton — ✅ Conforme, salvo Da(B, 1163.5) ❌](#norm-11)
  - [NORM-12 · 11.1.6.2 Paso 1: rango de ρo observada — ❌ No conforme](#norm-12)
  - [NORM-13 · 11.1.6.2: número máximo de iteraciones — ⚠️ Dudoso (el código es consistente con el ejemplo)](#norm-13)
  - [NORM-14 · 11.1.6.2: no convergencia frente a fuera de rango — ❌ No conforme (V-05)](#norm-14)
  - [NORM-15 · 11.1.6.2: cambio de subgrupo entre iteraciones (tipo B) — ✅ Conforme y exigido por la norma (F-10)](#norm-15)
  - [NORM-16 · 11.1.6.2 con α dado (tipo C) — ✅ Conforme (⚠️ con A/B/D + α)](#norm-16)
  - [NORM-17 · 11.1.6.3 (observada → alterna) — ⚠️ No implementado como función (composición conforme)](#norm-17)
  - [NORM-18 · 11.1.6.1/6.2: tipo de producto y sus parámetros — ✅ / ❌ (V-06)](#norm-18)
  - [NORM-19 · 11.1.7.1/11.1.7.2: unidades de presión y de Fp — ❌ No conforme (alto)](#norm-19)
  - [NORM-20 · 11.1.7.1: salidas — ❌ No conforme](#norm-20)
  - [NORM-21 · 11.1.7.2: salidas — ⚠️ Parcialmente conforme](#norm-21)
  - [NORM-22 · 11.1.7.x: temperatura base — ❌ No conforme (menor)](#norm-22)
  - [NORM-23 · 11.1.7.x: unidades de α60 — ⚠️ Dudoso](#norm-23)
  - [NORM-24 · 11.1.7.x: errores de rango — ❌ No conforme](#norm-24)
  - [NORM-25 · 11.1.2.3: límites generales y extrapolación — ❌ (densidad y α) / ✅ (t y P)](#norm-25)
  - [NORM-26 · Tipo C: ¿necesita densidad? — ⚠️ La API del código no lo modela bien](#norm-26)
  - [NORM-27 · 11.1.5.2: α60 a partir de mediciones — ⚠️ No implementado (informativo)](#norm-27)
  - [NORM-28 · Densidad a condiciones alternas en 7.1: ¿CTPL redondeado o no? — ⚠️ Dudoso](#norm-28)
  - [NORM-29 · Precisión exigida — ✅ Conforme](#norm-29)
- [Respuestas para la corrección de la auditoría](#respuestas-para-la-correcci-n-de-la-audi)

---


- **Norma**: `PDFs/API MPMS 11.1.pdf`. Las páginas se citan como **"p. N"**, que es la página del PDF (la página impresa es N−9). Las fórmulas se leyeron renderizando las páginas a imagen; los ejemplos se leyeron con OCR y luego se contrastaron con la imagen.
- **Código**: extraído de `git archive 4f1216d` (no del árbol de trabajo).
- **Banco de pruebas**: [`tests/data/norm_core_examples.json`](../../tests/data/norm_core_examples.json) (106 casos). Hoy los ejecuta `tests/test_norm_examples.py` (105 casos; se excluye el de 11.1.5.2, no implementado).
- **Veredictos**: ✅ Conforme · ❌ No conforme · ⚠️ Dudoso / no confirmable / solo informativo.

<a id="resumen-num-rico-de-los-ejemplos"></a>
## Resumen numérico de los ejemplos

| Bloque | Ejemplos | Resultado con el commit 4f1216d |
|---|---|---|
| 11.1.6.1 (pp. 44-54) | 15 | Los 8 cálculos válidos coinciden con todas las cifras impresas (diferencia relativa ≤ 1.6e-9, que es la resolución de impresión de α60). Los ejemplos 9, 10 y 11 (t o P fuera de rango) sí lanzan error. **Los ejemplos 12, 13 y 14 (densidad fuera de rango) NO lanzan error**: el código extrapola. |
| 11.1.6.2 (pp. 61-71) | 16 | Los 9 cálculos coinciden (≤ 2e-12), con el mismo nº de iteraciones y los mismos cambios de subgrupo. Los 7 casos de error lanzan excepción, pero 3 de ellos (ej. 14, 15 y 16, ρo fuera de rango) salen como `MPMSConvergenceError` y no como error de rango. |
| 11.1.6.3 (pp. 74-88), como 6.2 + 6.1 | 18 | Los 12 cálculos coinciden (≤ 2.3e-12) y los 6 casos de error lanzan excepción. |
| 11.1.7.1 (pp. 92-100) | 11 | Los 7 cálculos coinciden (≤ 8e-13) **solo si se pasa la presión ya convertida a psi**. Con la presión en kPa/bar, que es lo que pide la norma, falla (ver NORM-19). Los 4 casos de error salen como `MPMSConvergenceError`. |
| 11.1.7.2 (pp. 104-116) | 17 | Los 10 cálculos coinciden (≤ 5e-12), con la misma salvedad de unidades de presión. Los 7 casos de error lanzan excepción (el ej. 16 como error de convergencia). |
| 11.1.5.3 (t* impresos) | 19 | 9 valores con 12 decimales: diferencia ≤ 1e-14. 10 valores de tabla con 4 decimales: diferencia ≤ 4.3e-5, es decir, dentro del redondeo de la tabla. |
| 11.1.5.4 (pp. 38-39) | 3 | Exactos. |
| Tablas 6C/54C (pp. 188 y 191) | 6 | Coinciden si se pasa `rho=0` como centinela. **Fallan con `TypeError` si no se pasa densidad (`None`)**. |

**Conclusión**: las ecuaciones de cálculo (ITS-90, ρ*, α60, CTL, Fp, CPL y la iteración de Newton) están implementadas correctamente. Las no conformidades están en:
- la validación de entradas,
- el manejo de errores,
- las unidades de presión de 11.1.7.x,
- el redondeo final de CTPL,
- la forma de las salidas de 7.x.

---

<a id="hallazgos"></a>
## Hallazgos

<a id="norm-01"></a>
### NORM-01 · 11.1.5.1: conversiones de densidad (agua 999.016, API, densidad relativa) — ✅ Conforme
- **Norma** (p. 31): ρ = γT·ρw,T, con ρw,60 = **999.016 kg/m³**; ρ = 141.5/(G+131.5)·999.016; γ60 = ρ/999.016; G = 141.5/(ρ/999.016) − 131.5. Los valores son "in vacuo" (p. 30).
- **Código**: `section_5_1.py:20-34` aplica exactamente esas fórmulas.
- **Medición**: API 17.785 → 946.918739324112 y API −10 → 1163.463078189300. Ambos coinciden con las p. 44 y 45.
- **Corrección**: ninguna en las fórmulas. Solo la validación de dominio de V-07 (ρ > 0, G > −131.5).

<a id="norm-02"></a>
### NORM-02 · 11.1.5.1: temperatura, α y presión — ❌ No conforme (faltan conversiones)
- **Norma** (pp. 30-31):
  - t(°F) = 1.8·t°C + 32;
  - P(psig) = PkPa / **6.894757**;
  - P(psig) = Pbar / **0.06894757**;
  - α60 = α60,°C / 1.8;
  - α60,°C = 1.8·α60.
  - En 7.1/7.2 (p. 90 y p. 102): Fp,kPa = Fp,psi/6.894757 y Fp,bar = Fp,psi/0.06894757.
- **Código**: solo existen `celc_to_fahr` y `alphac_to_alphaf` (`section_5_1.py:36-42`). Faltan kPa→psi, bar→psi, α °F→°C y Fp psi→kPa/bar. Por eso 7.x no convierte la presión (ver NORM-19).
- **Corrección**: añadir `kpa_to_psi`, `bar_to_psi`, `alphaf_to_alphac`, `fp_psi_to_kpa` y `fp_psi_to_bar` con esas constantes exactas (la norma exige llevar las constantes con todos sus dígitos; p. 22, 11.1.3).

<a id="norm-03"></a>
### NORM-03 · 11.1.5.3: ITS-90 → IPTS-68 — ✅ Conforme (interfaz ⚠️)
- **Norma** (pp. 36-37):
  - t°C,90 = (t°F,90 − 32)/1.8;
  - τ = t°C,90/630;
  - Δt = (a1 + (a2 + (a3 + (a4 + (a5 + (a6 + (a7 + a8τ)τ)τ)τ)τ)τ)τ)τ;
  - coeficientes a1..a8 = −0.148759, −0.267408, 1.080760, 1.269056, −4.089591, −1.871251, 7.438081, −3.536296;
  - t°C,68 = t°C,90 − Δt;
  - t°F,68 = 1.8·t°C,68 + 32, **solo "si la entrada fue en °F"**.
  - La entrada es "either in units of °F … or °C", es decir, una sola.
- **Código**: `section_5_3.py`. Coeficientes, escala, evaluación de Horner y signo correctos.
- **Medición**: los 9 t* de 12 decimales (pp. 44-51, 54 y 104) coinciden con diferencia ≤ 1e-14.
- **Desviación de interfaz (⚠️)**: con entrada en °C devuelve °F por defecto, y si recibe ambas temperaturas ignora una (F-07).
- **Corrección**: exigir exactamente una entrada y devolver la temperatura en la misma unidad de entrada (o ambas).

<a id="norm-04"></a>
### NORM-04 · 11.1.5.4: algoritmo de redondeo — ❌ No conforme en la detección de empates
- **Norma** (pp. 37-39):
  - Paso 2: Y = |X|/δ.
  - Paso 3: "If the decimal portion of Y is **not exactly** equal to 0.5 then I = trunc(Y+0.5)". Si es exactamente 0.5: I = trunc(Y)+1 si trunc(Y) es impar, y trunc(Y) si es par (redondeo al par).
  - Paso 4: X_round = ±δ·I, con el signo del valor original.
  - Ejemplos: 5.34 °C → 5.35; −5.34 °C → −5.35; **10.05 °F → Y = 100.5 → 10.0**.
- **Código**: `section_5_4.py:30-78`. Los pasos son correctos, pero:
  1. El empate se detecta en coma flotante binaria con `isclose(rel_tol=1e-12)`. Falla en magnitudes grandes (N-01). El ejemplo de la norma trata Y = 10.05/0.1 como **exactamente** 100.5, es decir, como aritmética decimal. En binario, 10.05/0.1 = 100.49999999999999.
  2. Añade un `round()` posterior que la norma no contempla (N-02).
- **Medición**: los 3 ejemplos de la norma pasan (por coincidencia en el caso 10.05). La auditoría N-01 documenta, por ejemplo, 611.15 → 611.1 (lo correcto es 611.2).
- **Corrección**: implementar con `Decimal(str(x))` / `Decimal(str(delta))`, aplicar el paso 3 literal (o `ROUND_HALF_EVEN`), calcular X_round = δ·I en `Decimal` y luego pasar a `float`. Eliminar la "limpieza de precisión". Validar δ > 0 y x finito.
- **Incrementos (Paso 1, pp. 37-38)**: ✅ La tabla del docstring coincide: API 0.1; densidad relativa 0.0001; kg/m³ 0.1; °F 0.1; °C 0.05; psig 1; kPa 5; bar 0.05; α 0.1e-6 °F⁻¹ / 0.2e-6 °C⁻¹; CTL 0.00001; Fp 0.001 psi⁻¹ / 0.0001 kPa⁻¹ / 0.01 bar⁻¹; CPL y CTPL 0.00001.

<a id="norm-05"></a>
### NORM-05 · Política de redondeo: qué y cuándo — ❌ No conforme (CTPL nunca se redondea en las funciones de cálculo)
- **Norma**:
  - 11.1.3.9 (p. 28): "Implementation Procedures are now written with **no rounding of initial or intermediate values**. The final VCF is rounded to five decimal places. **Rounding of input values is only to be used when creating tabular representations** … intermediate values are never to be rounded".
  - 11.1.5 (p. 29): "The only value to be rounded is … **CTPL**".
  - 11.1.5.4 (p. 37): "All input values must be rounded when generating the tables in historical format".
  - 11.1.8 (p. 140): las tablas "are to be generated with rounded input and … rounded output".
  - 11.1.5.5 (p. 39): CTPL a 5 decimales; otras precisiones se permiten, pero nunca más de 8 decimales.
  - Pasos concretos: 6.1 Paso 8 (p. 42), 6.2 Paso 7 (p. 59), 6.3 Pasos 1-2 (p. 73), 7.1 y 7.2 Paso 4 (pp. 90 y 102): "Round this value of CTPL consistent with 11.1.5.4".
  - Excepción: en la iteración de 6.2 Paso 3 (p. 57), "**Do not round** the value of CTPL(m)".
- **Código**: `correct_base_to_alternate`, `correct_observed_to_base` y las funciones 7.x devuelven CTPL sin redondear. `tables.py` sí redondea las entradas, lo cual es correcto para tablas.
- **Corrección**: devolver CTPL sin redondear y además `ctpl_rounded = api_round(CTPL, 0.00001)` (o un parámetro `round_ctpl=True`). No redondear nunca ρ*, α, CTL, Fp ni CPL dentro del cálculo. Redondear las entradas solo en `tables.py`.
- **Volúmenes**: en los ejemplos, V60 = V·CTPL **redondeado** (p. 44: 987.99 × 1.03301 = 1020.6035499) ✅. Ver también NORM-28.

<a id="norm-06"></a>
### NORM-06 · 11.1.6.1: ecuaciones y constantes — ✅ Conforme
- **Norma** (pp. 41-42):
  - Paso 2: t*.
  - Paso 3: con α dado, ρ* = ρ60·exp[0.5·α60·δ60·(1+0.4·α60·δ60)]. Si no:

    ```
    ρ* = ρ60·{1 + (exp[A(1+0.8A)] − 1)/(1 + A(1+1.6A)B)}
    A = δ60/2·[(K0/ρ60 + K1)/ρ60 + K2]
    B = (2K0 + K1ρ60)/(K0 + (K1 + K2ρ60)ρ60)
    ```

  - Paso 4: α60 = (K0/ρ* + K1)/ρ* + K2.
  - Paso 5: Δt = t* − **60.0068749**; CTL = exp{−α60·Δt·[1 + 0.8·α60·(Δt + δ60)]} con δ60 = **0.01374979547**.
  - Paso 6: Fp = exp(−1.9947 + 0.00013427·t* + (793920 + 2326.0·t*)/ρ*²).
  - Paso 7: CPL = 1/(1 − 10⁻⁵·Fp·P).
  - Paso 8: CTPL = CTL·CPL.
  - Paso 9: ρ = CTL·CPL·ρ60 (sin redondear: p. 44, 946.9187·1.0330116 = 978.1780343640).
- **Código**: `section_6_1.py:19-100` aplica las mismas fórmulas. Fp usa ρ* (`rho_68`), correctamente.
- **Tabla K** (p. 41) ✅:

  | Grupo | K0 | K1 | K2 |
  |---|---|---|---|
  | Crudo | 341.0957 | 0 | 0 |
  | Fuel oil | 103.8720 | 0.2701 | 0 |
  | Jet | 330.3010 | 0 | 0 |
  | Zona de transición | 1489.0670 | 0 | −0.00186840 |
  | Gasolinas | 192.4571 | 0.2438 | 0 |
  | Lubricantes | 0 | 0.34878 | 0 |

- **Medición**: ej. 1-8 y 15 coinciden en t*, ρ*, α60, CTL, Fp, CPL, CTPL, ρ y V60 con diferencia ≤ 1.6e-9 relativa.

<a id="norm-07"></a>
### NORM-07 · 11.1.6.1 Paso 1: validación de ρ60 y α60 — ❌ No conforme
- **Norma** (pp. 40-41):
  - "Unless otherwise directed, check the input values": −58.0 °F ≤ t ≤ 302.0 °F; 0 ≤ P ≤ 1500 psig; **ρ60,min ≤ ρ60 ≤ ρ60,max** (si se especifica el tipo de producto); **230.0×10⁻⁶ ≤ α60 ≤ 930.0×10⁻⁶ °F⁻¹** (si se da α60 y no el tipo).
  - Límites de ρ60: crudo y productos 610.6–1163.5; lubricantes 800.9–1163.5. La comprobación de densidad "does not have to be done if α60 … is specified".
  - "If any of the other conditions are not true … **Set an error condition** (such as setting all output values to zero) **and exit**." El diagrama (p. 43) dice: "Flag error & Exit".
- **Código**: no valida ρ60 ni α60. Además, `resolve_commodity_group` (`commodity_groups.py:63-69`) asigna el "grupo más cercano" fuera de rango, es decir, extrapola.
- **Medición**: ej. 12 (ρ60 = 610.4714, A), 13 (1164.2296, B) y 14 (800.5480, D) no lanzan error. La norma exige error.
- **Corrección**:
  - En 6.1, validar `rho_min <= rho_60 <= rho_max` (ambos extremos inclusivos) según A/B/D, y `230e-6 <= alpha_60 <= 930e-6` cuando se da α.
  - Eliminar el *fallback* al grupo más cercano o convertirlo en error.
  - **Importante**: 6.2 Paso 3 (p. 57) dice "Do not check the input values for being in the proper range" al llamar a 6.1 en cada iteración. La validación debe poder desactivarse (`check_limits=False`) en la llamada interna.

<a id="norm-08"></a>
### NORM-08 · 11.1.6.1/11.1.6.2: límites de temperatura y presión — ✅ Conforme (NaN ⚠️)
- **Norma**: t inclusivo en [−58.0, 302.0] °F. "If P < 0 psig then set P = 0 psig and continue" (p. 41 y p. 57). P > 1500 es error.
- **Código**: `validators/inputs.py` hace exactamente eso, con límites inclusivos.
- **Medición**: ej. 6.1-3, 6.2-1, 6.3-1, 7.1-8 y 7.2-2 (P negativa) coinciden. Ej. 6.1-9/10/11 dan error.
- **NaN**: la norma no lo menciona, pero un NaN no cumple "0 ≤ P ≤ 1500", así que debe dar error. El código devuelve NaN (V-03). **Corrección**: `if not math.isfinite(p): raise …` antes de `P<0 → 0`.

<a id="norm-09"></a>
### NORM-09 · 11.1.6.1: rama `rho_60 <= 0` → Fp = 0, CPL = 1 — ❌ No conforme (salvo P = 0)
- **Norma**: ρ60 siempre es entrada de 6.1 (p. 39, "Input Values"), y Fp se calcula con ρ* (p. 42), que exige ρ60 > 0. El diagrama (p. 43) solo permite "Set CPL = 1" cuando "CPL needed? → No" (P = 0). Las tablas 6C/24C (p. 187) y 54C/60C (p. 190) fijan P = 0 y su salida es **solo CTL**.
- **Código**: `section_6_1.py:81-83` fija Fp = 0 y CPL = 1 con cualquier presión. Además, la guarda va después de dividir por ρ60 en la rama sin α (F-02).
- **Medición**: `b2a(0, 100, 500, alpha_60=0.0005)` → CPL = 1.0 con 500 psig. La norma daría error (no hay densidad para Fp).
- **Corrección**:
  - Tipos A/B/D: ρ60 debe estar en rango (NORM-07); ρ ≤ 0 es error.
  - Tipo C: permitir `rho_60=None` **solo si P == 0** (CTL puro, CPL = 1, Fp = `None`). Si P > 0, exigir ρ60 > 0 y calcular Fp con ρ* = ρ60·exp[0.5·α·δ60·(1+0.4·α·δ60)].
  - No devolver `Fp = 0`: es un valor físicamente falso.

<a id="norm-10"></a>
### NORM-10 · Asignación de subgrupo por densidad (tabla K y tabla Da) — ✅ Conforme en rango
- **Norma** (p. 41 y p. 58): los intervalos son [min, max) excepto fuel oils, que es 838.3127 ≤ ρ60 **≤** 1163.5. El subgrupo se determina con ρ60 (no con ρ*). Las clases se asignan por densidad y no por descriptor comercial (p. 19).
- **Código**: `rho_min <= rho < rho_max` más *fallback*. En 1163.5 el *fallback* elige fuel oil, crudo o lubricante: correcto por casualidad. Fronteras verificadas: 610.6 → gasolina, 770.352 → transición, 787.5195 → jet, 838.3127 → fuel oil, 1163.5 → fuel oil.
- **Corrección**: codificar el extremo superior inclusivo de fuel oil (y de crudo y lubricantes en 1163.5 para la validación) y quitar el *fallback* (NORM-07).

<a id="norm-11"></a>
### NORM-11 · 11.1.6.2: esquema de Newton — ✅ Conforme, salvo Da(B, 1163.5) ❌
- **Norma** (pp. 57-59):
  - Valor inicial ρ60(0) = ρo, recortado a [ρ60,min, ρ60,max].
  - Convergencia: |ρo − ρ60(m)·CTPL(m)| **< 0.000001 kg/m³** (sobre la densidad observada).
  - E = ρo/(CTL·CPL) − ρ60(m).
  - **DT = Da·α60(m)·Δt·(1 + 1.6·α60(m)·Δt), con Δt ≡ t_o − 60**. Es la temperatura **ITS-90 observada**, no t* ni 60.0068749.
  - DP = −2·CPL·Po·Fp·(7.93920 + 0.02326·t_o)/ρ60(m)², también con t_o ITS-90.
  - Δρ60 = E/(1 + DT + DP).
  - Si ρ60 + Δρ queda fuera de rango, se recorta Δρ hasta el límite.
- **Tabla Da** (p. 58):

  | Grupo | Da |
  |---|---|
  | Crudo | 2.0 |
  | Fuel oil (838.3127 ≤ ρ ≤ 1163.5) | 1.3 |
  | Jet | 2.0 |
  | Zona de transición | 8.5 |
  | Gasolinas | 1.5 |
  | Lubricantes | 1.0 |
  | Tipo C (α dado) | 0.0 |

- **Código**: `section_6_2.py:43-98` coincide en todo lo anterior. Usa `t_o - 60.0` y `t_o` en DP, correctamente.
- **Desviación**: `iteration_coefficients.py:26` usa `838.3127 <= rho_60 < 1163.5`, así que con ρ60 = 1163.5, que se alcanza al recortar, **Da(B) = 0.0** en lugar de 1.3.
  - **Impacto medido**: el resultado final no cambia, pero hay una iteración extra en casos como ρ60 = 1163.3 a −58 °F (4 evaluaciones frente a 3) y un mayor riesgo de no converger.
- **Corrección**: `838.3127 <= rho_60 <= 1163.5`. No devolver 0.0 por defecto para tipo B: lanzar error.
- **Medición**: 6.2 ej. 1-9, 6.3 y 7.2 coinciden en ρ60, CTL, Fp, CPL y CTPL (≤ 5e-12) y en el número de iteraciones.

<a id="norm-12"></a>
### NORM-12 · 11.1.6.2 Paso 1: rango de ρo observada — ❌ No conforme
- **Norma** (p. 57): ρmin ≤ ρo ≤ ρmax (si se da el tipo):

  | Tipo | ρo mín (kg/m³) | ρo máx (kg/m³) |
  |---|---|---|
  | Crudo | 470.5 | 1201.8 |
  | Productos | 470.4 | 1209.5 |
  | Lubricantes | 714.3 | 1208.3 |

  Además, α en [230, 930]×10⁻⁶ si se da α. "If any of the input variables are out of range set an error condition … and exit." También: "even if a ρo value is within these limits it may still not correspond to a valid ρ60" (eso se comprueba en el Paso 7).
- **Código**: no valida ρo. Usa límites `(-1e7, 1e6)` para el tipo C.
- **Medición**: ej. 6.2-14 (ρo = 1208.52, D), 6.2-15 (714.02, D), 6.2-16 (1208.31, D) y 7.2-16 (714.245, D) salen como `MPMSConvergenceError` tras 15 iteraciones. La norma los rechaza en el Paso 1 como fuera de rango.
- **⚠️ Erratas en la norma**:
  - Los textos de los ejemplos dicen "Density less than **470.4**" para crudo (p. 70, ej. 10) y "**470.3**" para productos (p. 70, ej. 12; p. 86), mientras la tabla dice 470.5 / 470.4.
  - El ej. 6.2-14 (p. 71) dice "greater than **1163.5**" para un lubricante a 60 °F.
  - **Usar los valores de la tabla de la p. 57**: son los que tienen la precisión definitoria.
- **Corrección**: validar ρo (inclusivo) contra esa tabla antes de iterar y lanzar `MPMSValidationError` (o un `MPMSRangeError` específico).

<a id="norm-13"></a>
### NORM-13 · 11.1.6.2: número máximo de iteraciones — ⚠️ Dudoso (el código es consistente con el ejemplo)
- **Norma**:
  - Paso 6 (p. 59): "Increment the iteration counter to m+1. If this value … is **less than or equal to 15** continue … Otherwise set an error condition for non-convergence". El diagrama (p. 60) dice "m > 15? → Flag error". Leído literalmente, permite evaluar CTPL en m = 0..15 (16 evaluaciones).
  - El ejemplo 7.2-17 (p. 116) muestra iteraciones m = 0 … **14** y el mensaje "convergence not achieved **after 15 iterations**".
- **Código**: `_MAX_ITER = 15` → evaluaciones m = 0..14. Coincide con el ejemplo; con la lectura literal falta una evaluación. Solo afecta a casos límite. El mensaje tiene "15" fijo en el texto.
- **Corrección**: mantener 15 como límite, documentado con la referencia al ejemplo de la p. 116, y usar `_MAX_ITER` en el mensaje. No cambia ningún resultado normativo.

<a id="norm-14"></a>
### NORM-14 · 11.1.6.2: no convergencia frente a fuera de rango — ❌ No conforme (V-05)
- **Norma**:
  - p. 25: "A special error condition is returned to signify non-convergence. The actual form … is not specified".
  - Nota del Paso 6 (p. 59): en productos refinados cerca de una frontera de subgrupo puede no converger por una "mathematical anomaly". En ese caso "the density from the last iteration **may be used** to calculate the CTPL and the result should be **flagged** with a note that it did not converge".
  - Paso 7 (p. 59): tras converger, si ρ60 < ρ60,min o ρ60 > ρ60,max, **error de rango**.
  - El ej. 7.2-17 (p. 116) muestra los dos mensajes a la vez: no convergencia y "Density is outside limits of procedure".
- **Código**: siempre lanza `MPMSConvergenceError`, tanto si la causa es de rango (ρ60 anclado al límite) como de convergencia real.
- **Corrección**:
  - Error de rango en el Paso 1 (ρo, t, P, α).
  - Si al no converger ρ60 está anclado en ρ60,min/max, lanzar error de rango ("ρ60 fuera de límites del procedimiento").
  - Si no converge por otro motivo, lanzar `MPMSConvergenceError` con la última iteración adjunta (`last_rho_60`, `last_ctpl`) para que el llamador pueda usarla marcada.
  - Mantener la comprobación del Paso 7.

<a id="norm-15"></a>
### NORM-15 · 11.1.6.2: cambio de subgrupo entre iteraciones (tipo B) — ✅ Conforme y exigido por la norma (F-10)
- **Norma** (p. 55): "when using the Generalized Refined Products group (the B Tables), the sub-group may change depending upon the iterative value of the base density, ρ60. This sub-group switching is **automatically performed as part of this iteration procedure**". En la p. 58, Da(m) puede cambiar de una iteración a otra.
- **Ejemplos con cambio de subgrupo**:
  - 6.2-5 (p. 65): jet → transición.
  - 6.2-6 (p. 66): gasolina → transición → gasolina.
  - 7.2-1 (p. 104): gasolina → transición → gasolina.
  - 7.2-6 y 7.2-7 (pp. 109-110).
- **Código**: re-resuelve el grupo con ρ60(m) en cada iteración ✅. Los 5 ejemplos se reproducen con ≤ 5e-12.
- **Corrección**: ninguna en la lógica. Añadir esos ejemplos como pruebas de regresión. NO "congelar" el grupo.

<a id="norm-16"></a>
### NORM-16 · 11.1.6.2 con α dado (tipo C) — ✅ Conforme (⚠️ con A/B/D + α)
- **Norma**: Da = 0 ⇒ DT = 0 (p. 58). El rango de ρ60 "does not have to be done if α60 … is specified" (p. 57). La entrada es "Commodity group (if α60 not input)" / "α60 (if commodity group not given)" (p. 55).
- **Código**: Da = 0 si `alpha_given` ✅. El ejemplo 6.2-7 coincide (≤ 1e-12). Sin embargo, si se pasa `commodity_type='a'` y α a la vez, usa α pero recorta ρ60 a los límites del crudo (⚠️, no está previsto en la norma).
- **Corrección**: tratar α y tipo A/B/D como mutuamente excluyentes (error si vienen ambos) o documentar la precedencia de α y, en ese caso, no aplicar los límites de densidad del tipo.

<a id="norm-17"></a>
### NORM-17 · 11.1.6.3 (observada → alterna) — ⚠️ No implementado como función (composición conforme)
- **Norma** (pp. 72-73):
  - Paso 1: 6.2, conservando CTL,o, Fp,o, CPL,o y CTPL,o, con **CTPL,o redondeado**.
  - Paso 2: 6.1 a (t, P), con **CTPL redondeado**.
  - V60 = Vo·CTPL,o y V = V60/CTPL.
- **Código**: no hay función, pero la composición `correct_observed_to_base` + `correct_base_to_alternate` reproduce los 12 ejemplos con cálculo (≤ 2.3e-12).
- **Corrección (opcional)**: añadir `correct_observed_to_alternate()` que devuelva ambos juegos de factores y los dos CTPL redondeados.

<a id="norm-18"></a>
### NORM-18 · 11.1.6.1/6.2: tipo de producto y sus parámetros — ✅ / ❌ (V-06)
- **Norma** (pp. 14-20, 41, 57-58):

  | Tipo | Producto | Subgrupos / α | Rango de ρ60 (kg/m³) |
  |---|---|---|---|
  | A | Crudo | — | 610.6–1163.5 |
  | B | Productos refinados | 4 subgrupos | 610.6–1163.5 |
  | C | Aplicaciones especiales | α60 medido, entrada obligatoria en [230, 930]×10⁻⁶ °F⁻¹ | sin límite de densidad |
  | D | Lubricantes | — | 800.9–1163.5 |

- **Código**: 6.1 acepta A/B/D y C implícito vía α; 6.2 acepta a/b/c/d; `resolve_commodity_group` acepta a/b/d. Con 'c' sin α el mensaje de error es engañoso.
- **Corrección**: un único validador. "C" ⇒ α obligatorio (y validado); A/B/D ⇒ α prohibido (o con precedencia documentada).

<a id="norm-19"></a>
### NORM-19 · 11.1.7.1/11.1.7.2: unidades de presión y de Fp — ❌ No conforme (alto)
- **Norma**:
  - 7.1 (p. 89): "P: Alternate pressure (**kPa or bar (gauge)**)". Paso 1 (p. 90): convertir T, t y P a unidades del sistema inglés (P_psi = P_kPa/6.894757 o P_bar/0.06894757). Salida "Fp (kPa⁻¹ or bar⁻¹)" (p. 89), con Fp = Fp,psi/6.894757 (kPa) o /0.06894757 (bar) (p. 90).
  - 7.2: igual para Po (p. 101) y Fp (p. 102).
- **Código**: `section_7_1.py:29` y `section_7_2.py:28` pasan `p_a`/`p_o` **tal cual como psig**, y devuelven `Fp_psi` (psi⁻¹).
- **Medición**:

  | Caso | CTPL con la presión sin convertir | CTPL de la norma |
  |---|---|---|
  | Ej. 7.1-6 (1235 kPa) | 0.998310 (1235 tomado como psig) | 0.984120 (error de 1.4 %) |
  | Ej. 7.1-3 (75 kPa) | 0.940929 | 0.940491 |

  Con la presión convertida a mano, todos los ejemplos 7.1/7.2 coinciden (≤ 5e-12), y Fp/6.894757 o Fp/0.06894757 reproduce los Fp kPa⁻¹/bar⁻¹ impresos.
- **Corrección**:
  - Añadir `p_unit: Literal["kPa","bar"]` (o funciones separadas) y convertir con 5.1 antes de llamar a 6.x. Aplicar "P < 0 → 0" (ej. 7.1-8 y 7.2-2) y el límite de 1500 psi tras convertir (1.034×10⁴ kPa / 103.4 bar, p. 15).
  - Devolver Fp en la unidad de entrada (kPa⁻¹ o bar⁻¹), y opcionalmente también en psi⁻¹.
  - Redondear Fp con δ = 0.0001 kPa⁻¹ o 0.01 bar⁻¹ solo en tablas.

<a id="norm-20"></a>
### NORM-20 · 11.1.7.1: salidas — ❌ No conforme
- **Norma** (pp. 89-91):
  - Salidas: CTL, CPL, Fp (kPa⁻¹/bar⁻¹), CTPL. Opcionales: **ρ (densidad a condiciones alternas)**, VT y ρ60.
  - Paso 2: ρ60 desde ρT a T°F con 6.2 y P = 0 → CTL,60.
  - Paso 3: 6.1 a (t°F, P_psi) → C*TL, CPL, C*TPL, Fp,psi.
  - Paso 4: CTL = C*TL/CTL,60; CTPL = CTL·CPL, **redondeado**.
  - Paso 5: ρ = CTL·CPL·ρT; VT = Vt,P·CTPL.
- **Código**: `correct_observed_to_alternate_C` hace bien los pasos 2-4 (CTL = CTL_a/CTL_60 ✅, CPL = CPL_a ✅), pero:
  - devuelve **ρ60 en lugar de ρ** (descarta `rho`);
  - Fp sale en psi⁻¹;
  - CTPL no se redondea;
  - el nombre y el docstring ("11.1.6.2", "observed") no corresponden a 7.1, cuya entrada es la densidad **base métrica** ρT.
- **Corrección**: devolver `(rho, rho_60, CTL, Fp[kPa⁻¹|bar⁻¹], CPL, CTPL, CTPL_rounded)` con nombres claros (por ejemplo, `correct_metric_base_to_alternate`).

<a id="norm-21"></a>
### NORM-21 · 11.1.7.2: salidas — ⚠️ Parcialmente conforme
- **Norma** (pp. 101-103):
  - Salidas: ρT, CTL, CPL, Fp (kPa⁻¹/bar⁻¹), CTPL. Opcionales: VT, ρ60.
  - Paso 2: 6.2 con (t_o°F, P_o,psi) → C*TL, CPL, C*TPL, Fp,psi.
  - Paso 3: 6.1 a T°F, P = 0 → ρT y CTL,60.
  - Paso 4: CTL = C*TL/CTL,60; CTPL = CTL·CPL, redondeado; Fp convertido.
  - Paso 5: VT = Vo·CTPL.
- **Código**: `correct_observed_to_base_C` devuelve ρT ✅, ρ60 ✅, CTL ✅, CPL ✅ y CTPL ✅ (sin redondear ❌). Fp sale en psi⁻¹ ❌ y la presión no se convierte ❌ (NORM-19). La anotación de tipo dice 5 valores y devuelve 6 (F-04).
- **Corrección**: igual que NORM-19 y NORM-20.

<a id="norm-22"></a>
### NORM-22 · 11.1.7.x: temperatura base — ❌ No conforme (menor)
- **Norma** (p. 89 y p. 101): T = **15 °C o 20 °C** (11.1.3.1, p. 22: "Accepted standard temperatures are 60 °F, 15 °C and 20 °C").
- **Código**: `t_b: Optional[int] = 20` acepta cualquier valor (por ejemplo, `t_b=17` devuelve un resultado).
- **Corrección**: validar `t_b in (15, 20)` y no usar un valor por defecto implícito; hacerlo obligatorio.

<a id="norm-23"></a>
### NORM-23 · 11.1.7.x: unidades de α60 — ⚠️ Dudoso
- **Norma**: 7.1/7.2 piden "Pre-calculated 60 °F thermal expansion factor" sin unidad explícita; las entradas "deben estar en las unidades propias" (°C, kPa/bar, kg/m³) o convertirse con 5.1. Los ejemplos 7.1-7 (p. 98) y 7.2-8 (p. 111) dan **α en °F⁻¹** (0.000446759 y 0.0005763). Las tablas 54C/60C (p. 190) usan α en **°C⁻¹**, en [414, 1674]×10⁻⁶.
- **Código**: espera °C⁻¹ y divide entre 1.8 ✅ (coincide con 5.1). Los ejemplos pasan con α°C = 1.8·α°F. El valor `0.0` se trata como ausente (F-05).
- **Corrección**: documentar la unidad, o aceptar `alpha_unit`. Usar `is not None`. Validar el rango en la unidad dada: [230, 930]×10⁻⁶ °F⁻¹ o [414, 1674]×10⁻⁶ °C⁻¹ (p. 15).

<a id="norm-24"></a>
### NORM-24 · 11.1.7.x: errores de rango — ❌ No conforme
- **Norma** (p. 90, Paso 2): "If this procedure returns with an error condition (i.e. fluid outside the limits of this Standard), exit this procedure". Los ejemplos 7.1-8 a 7.1-11 (pp. 99-100) y 7.2-11 a 7.2-16 (pp. 114-115) muestran errores de rango de t, P y densidad.
- **Código**: 7.1-8 a 7.1-11 y 7.2-16 salen como `MPMSConvergenceError`, porque la densidad no se valida (NORM-12) y en 7.1 la t alterna no se valida antes de iterar.
- **Corrección**: validar t (−50 a 150 °C), P (tras convertir) y la densidad de entrada al principio, y propagar el error de rango de 6.x.

<a id="norm-25"></a>
### NORM-25 · 11.1.2.3: límites generales y extrapolación — ❌ (densidad y α) / ✅ (t y P)
- **Norma** (p. 15). Valores definitorios, en negrita cursiva:

  | Magnitud | Límites | Equivalencias |
  |---|---|---|
  | Densidad a 60 °F | 610.6–1163.5 kg/m³ (crudo y productos); 800.9–1163.5 (lubricantes) | — |
  | Temperatura | −50.00 a 150.00 °C | −58.0 a 302.0 °F |
  | Presión | 0 a 1500 psig | 0 a 1.034×10⁴ kPa; 0 a 103.4 bar |
  | α60 | 230.0×10⁻⁶ a 930.0×10⁻⁶ °F⁻¹ | 414.0×10⁻⁶ a 1674.0×10⁻⁶ °C⁻¹ |

  - Equivalencias de densidad a otras bases: a 15 °C, 611.16–1163.79 (crudo), 611.16–1163.86 (productos) y 801.25–1163.85 (lubricantes); a 20 °C, 606.12–1161.15, 606.12–1160.62 y 798.11–1160.71. Estas conversiones "may numerically fall just outside of the actual limits": **validar siempre contra ρ60**, no contra los valores convertidos.
  - Dentro de los límites hay regiones "extendidas" (extrapolación matemática respecto a los datos de 1980) que "should be used with caution", pero siguen siendo válidas. **Fuera de los límites, la norma marca error y sale (no extrapola)** (pp. 40-41, 57).
- **Código**: t y P ✅; ρ y α no se validan y extrapolan ❌ (NORM-07, NORM-12).

<a id="norm-26"></a>
### NORM-26 · Tipo C: ¿necesita densidad? — ⚠️ La API del código no lo modela bien
- **Norma**:
  - CTL depende solo de α60 y t (p. 42, Paso 5).
  - ρ* con α dado = ρ60·exp[0.5·α·δ60·(1+0.4·α·δ60)] (p. 41). Fp = f(t*, ρ*) (p. 42), así que **CPL sí necesita densidad**.
  - Las tablas 6C/24C (p. 187) y 54C/60C (p. 190) se generan con P = 0 y salida = CTL, sin densidad.
  - Ejemplos con densidad y presión: 6.1-7 (p. 50), 6.2-7 (p. 67), 7.1-7 (p. 98), 7.2-8 (p. 111).
- **Código**: los ejemplos de tipo C con densidad coinciden (≤ 1e-11). Las tablas 6C y 54C se reproducen exactas (6 valores) **pasando ρ = 0 como centinela**; con `None` dan `TypeError`.
- **Corrección**: `rho_60: Optional[float]`. Si es `None`, exigir P == 0 y devolver CTL (CPL = 1, Fp = `None`). Si P > 0, exigir ρ60 > 0 (ver NORM-09).

<a id="norm-27"></a>
### NORM-27 · 11.1.5.2: α60 a partir de mediciones — ⚠️ No implementado (informativo)
- **Norma** (pp. 32-35): regresión de Newton con 6 iteraciones fijas. Ejemplo (p. 35): α60 = 446.655×10⁻⁶ °F⁻¹ y ρ60 = 867.756 kg/m³, redondeados a 446.7×10⁻⁶ y 867.8.
- **Código**: no existe. Se deja el ejemplo en el JSON por si se implementa.

<a id="norm-28"></a>
### NORM-28 · Densidad a condiciones alternas en 7.1: ¿CTPL redondeado o no? — ⚠️ Dudoso
- **Norma**: el Paso 5 de 7.1 (p. 91) da ρ = CTL·CPL·ρT, pero los ejemplos imprimen ρ = ρT·CTPL **redondeado**:
  - 7.1-1: 772.3 × 1.05015 = 811.030845; con CTPL sin redondear sería 811.0329.
  - 7.1-3: 865.6 × 0.94049 = 814.088144.

  En 6.1, en cambio, los ejemplos usan el CTPL sin redondear (p. 44).
- **Corrección**: devolver ρ con factores sin redondear (fórmula del Paso 5) y documentar que los ejemplos 7.1 usan el CTPL redondeado. En las pruebas, comparar ρ de 7.1 contra ρT·CTPL_redondeado, como hace [`tests/data/norm_core_examples.json`](../../tests/data/norm_core_examples.json).

<a id="norm-29"></a>
### NORM-29 · Precisión exigida — ✅ Conforme
- **Norma** (p. 29-30): cálculo en doble precisión (64 bits) como mínimo; "it is required that at least **eight of the significant digits** be matched" con los ejemplos.
- **Código**: usa `float` de Python (IEEE-754 de 64 bits) y supera las 8 cifras en todos los ejemplos con cálculo (peor caso 2e-9 relativo, limitado por la impresión).

---

<a id="respuestas-para-la-correcci-n-de-la-audi"></a>
## Respuestas para la corrección de la auditoría

| Hallazgo de la auditoría | Qué exige la norma | Referencia |
|---|---|---|
| **N-01 / N-02 (redondeo)** | Algoritmo de 4 pasos: Y = \|X\|/δ; si la parte decimal de Y **no es exactamente** 0.5, I = trunc(Y+0.5); si es exactamente 0.5, al par; X = ±δ·I con el signo original. El ejemplo 10.05 → 10.0 trata los valores como decimales exactos, así que la implementación con `Decimal` (half-even) es la interpretación fiel. No hay ningún "round" posterior. Solo se redondea el **CTPL final** a 5 decimales. Las **entradas se redondean solo al generar tablas** (y también la salida de la tabla). Los valores intermedios **nunca** se redondean; dentro de la iteración de 6.2, "Do not round CTPL(m)". | pp. 28, 29, 37-39, 57, 140 |
| **F-02 / F-08 / V-01 (densidad 0, negativa o fuera de rango; tipo C)** | A/B/D: comprobar ρ60,min ≤ ρ60 ≤ ρ60,max (inclusivo; 610.6/800.9 – 1163.5) en 6.1, y ρo en la tabla de la p. 57 (A 470.5–1201.8, B 470.4–1209.5, D 714.3–1208.3) en 6.2. Fuera de rango → **error y salida**, sin extrapolar. Tipo C: no se comprueba la densidad, pero Fp/CPL requieren ρ* > 0. Con P = 0 (tablas 6C/24C/54C/60C) basta CTL y no se necesita densidad. **Fp = 0 no es un valor normativo.** La comprobación en 6.1 debe poder desactivarse cuando la llama la iteración de 6.2. | pp. 40-41, 43, 57, 59, 187, 190 |
| **V-03 (presión)** | Si P < 0 se fija P = 0 y se continúa (comportamiento actual correcto, se puede emitir aviso). Si P > 1500 psig → error. Límites inclusivos 0 ≤ P ≤ 1500. NaN no cumple la condición → error. En 7.x se aplica tras convertir de kPa/bar a psig. | pp. 15, 41, 57; ej. 6.1-3, 7.1-8, 7.2-2 |
| **V-04 (α)** | Si se da α60, debe estar en 230.0×10⁻⁶ ≤ α60 ≤ 930.0×10⁻⁶ °F⁻¹ (414.0–1674.0×10⁻⁶ °C⁻¹). Fuera → error. | pp. 15, 40, 57 |
| **V-05 (fuera de rango frente a no convergencia)** | Son dos condiciones distintas: (1) **fuera de rango** en el Paso 1 (t, P, ρo, α) o en el Paso 7 (ρ60 convergido fuera de [ρ60,min, ρ60,max]); (2) **no convergencia** tras 15 iteraciones (la forma del error es libre; se puede devolver la última iteración "flagged"). Si al agotar las iteraciones ρ60 está anclado al límite, el error correcto es de rango (como muestra el ej. 7.2-17). | pp. 25, 57, 59, 60, 116 |
| **V-06 (tipos A/B/C/D)** | A crudo; B productos refinados (4 subgrupos: fuel oil, jet, transición, gasolina); C aplicaciones especiales = α60 de entrada (sin grupo); D lubricantes. En 6.1/6.2 se da "Commodity group (if α60 not input)" o "α60 (if commodity group not given)": son excluyentes. | pp. 14, 18-19, 39, 41, 55, 58 |
| **F-07 (ITS-90)** | La entrada es **una** temperatura, en °F o en °C. Se calcula t°C,68 = t°C,90 − Δt, y t°F,68 solo "if the input temperature was in °F". Coeficientes y escala (τ = t/630) verificados. | pp. 36-37 |
| **F-10 (cambio de grupo entre iteraciones)** | **Es lo que exige la norma**: "This sub-group switching is automatically performed as part of this iteration procedure"; Da también cambia. Los ejemplos 6.2-5, 6.2-6, 7.2-1, 7.2-6 y 7.2-7 lo muestran y el código los reproduce. Solo hace falta añadirlos como regresión y aplicar la nota de la p. 59 (no convergencia en frontera → resultado marcado). | pp. 55, 58, 59, 65-66, 104, 109-110 |
| **F-05 (α = 0)** | α = 0 está fuera del rango normativo (≥ 230×10⁻⁶ °F⁻¹). Hay que tratarlo como "dado" (`is not None`) y rechazarlo con un error de rango, no como "no proporcionado". | pp. 15, 40 |
| **Unidades de presión en 7.x** | Entrada P en **kPa (gauge) o bar (gauge)**, convertida con P_psi = P_kPa/6.894757 o P_bar/0.06894757. Salida Fp en **kPa⁻¹ o bar⁻¹** (Fp,psi/6.894757 o /0.06894757). P < 0 → 0. Límite 1500 psig (≈ 1.034×10⁴ kPa / 103.4 bar). Temperatura base solo 15 o 20 °C. Hoy el código toma la presión como psig: con 1235 kPa da CTPL 0.99831 frente a 0.98412 de la norma. | pp. 15, 30-31, 89-90, 101-102 |
| **Salidas de 7.1/7.2 (F-04, F-09)** | 7.1 → CTL, CPL, Fp (kPa⁻¹/bar⁻¹), CTPL (redondeado); opcionales ρ (alterna), VT, ρ60. 7.2 → ρT, CTL, CPL, Fp (kPa⁻¹/bar⁻¹), CTPL (redondeado); opcionales VT, ρ60. CTL = C*TL/CTL,60 y CPL = CPL del punto alterno/observado (ya correcto). | pp. 89-91, 101-103 |
| **Nº máximo de iteraciones** | 15. El texto del Paso 6 admite leerlo como 16 evaluaciones (m ≤ 15), pero el ejemplo de la p. 116 muestra m = 0..14 y "after 15 iterations", que coincide con el código. Mantener 15 y referenciar el mensaje a `_MAX_ITER`. | pp. 59, 60, 116 |
| **Tolerancia de convergencia** | \|ρo − ρ60(m)·CTPL(m)\| < 1×10⁻⁶ kg/m³ (estricto, sobre la densidad observada). El código cumple. | p. 58 |
| **DT y DP** | Δt = **t_o − 60** con la t_o observada **ITS-90** (no t*, no 60.0068749), y t_o también en DP. El código cumple. | p. 58 |

---

[⬅ Anterior: Conformidad con la norma](10_conformidad_norma.md) · [Índice](README.md) · [Siguiente: Anexo B — Tablas ➡](12_anexo_norma_tablas.md)
