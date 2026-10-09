# 12 · Anexo B — Verificación normativa de las tablas (11.1.8)

[⬅ Anterior: Anexo A — Núcleo](11_anexo_norma_nucleo.md) · [Índice](README.md)

> [!NOTE]
> Este anexo describe el código del commit auditado `4f1216d`, **antes** de las correcciones.
> El estado actual de cada punto está en [10 · Conformidad con la norma](10_conformidad_norma.md).
> Las páginas citadas son páginas del PDF de API MPMS 11.1 (2004).

## 📑 Contenido

- [Hallazgos](#hallazgos)
  - [NORM-T01 · El motor numérico reproduce todas las tablas de muestra de la norma: ✅ Conforme](#norm-t01)
  - [NORM-T02 · Conversiones de unidades (11.1.5.1): ✅ Conforme](#norm-t02)
  - [NORM-T03 · Presión, temperatura base y procedimiento invocado: ✅ Conforme](#norm-t03)
  - [NORM-T04 · Redondeo de entradas y salidas en las tablas A/B/D: ✅ Conforme](#norm-t04)
  - [NORM-T05 · Las tablas C no redondean el coeficiente alpha: ❌ No conforme (impacto bajo)](#norm-t05)
  - [NORM-T06 · No se valida el rango de alpha (tablas C): ❌ No conforme](#norm-t06)
  - [NORM-T07 · Tablas C invocadas con `rho_60=0` / `rho_t=0`: ⚠️ Dudoso (resultado correcto, implementación frágil)](#norm-t07)
  - [NORM-T08 · `generar_tabla_23a` convierte la temperatura en vez de la densidad relativa: ❌ No conforme (confirmado)](#norm-t08)
  - [NORM-T09 · Rangos del generador para 5A, 5B, 5D, 6A, 6B, 6D y temperatura: ✅ Conforme (con fragilidad)](#norm-t09)
  - [NORM-T10 · Funciones combinadas `table_5x_6x`, `table_23x_24x`, `table_53x_54x` y `table_59x_60x`: ❌ No conforme (no son tablas normativas y su resultado difiere del procedimiento normativo)](#norm-t10)
  - [NORM-T11 · `table_6x` y `table_24x` no rechazan densidades base fuera de rango: ❌ No conforme](#norm-t11)
  - [NORM-T12 · Tablas 54x/60x (11.1.7.1): rangos y procedimiento: ✅ Conforme](#norm-t12)
  - [NORM-T13 · Qué imprimir cuando el cálculo no es posible: ⚠️ Dudoso (la norma no lo prescribe para tablas)](#norm-t13)
  - [NORM-T14 · Cobertura del generador y de las funciones: ⚠️ Incompleto](#norm-t14)
  - [NORM-T15 · Erratas de la propia norma y cómo las interpreta el código: ⚠️ Informativo](#norm-t15)
  - [NORM-T16 · Formato de salida del generador: ⚠️ Menor](#norm-t16)
  - [NORM-T17 · Referencias normativas en los docstrings: ⚠️ Menor](#norm-t17)
- [Tabla resumen por función](#tabla-resumen-por-funci-n)

---


- **Código auditado:** commit `4f1216d`: `src/api_mpms/mpms_11_1/tables.py`, `src/api_mpms/Tables/generator_tables.py` y las secciones `section_5_1`, `5_4`, `6_1`, `6_2`, `7_1`, `7_2`. El árbol de trabajo no se revisó.
- **Norma:** `PDFs/API MPMS 11.1.pdf`. Las páginas se citan como **pág. PDF** (página impresa = PDF − 9; p. ej., la pág. PDF 141 es la impresa 132).
- **Método:**
  1. Se leyeron las instrucciones 11.1.8.1 a 11.1.8.24 (págs. PDF 139-192), 11.1.3.9 (pág. 28), 11.1.5.1 (págs. 30-31), 11.1.5.4 (págs. 37-39), 11.1.6.1/11.1.6.2 (págs. 39-60) y 11.1.7.1/11.1.7.2 (págs. 89-103).
  2. Se extrajeron las **28 tablas de muestra impresas** en la norma: 51 temperaturas × 7 columnas = **9 996 valores**.
  3. Esos valores se compararon con lo que calcula el código de `4f1216d` (scripts temporales de verificación, no versionados).

> **Resultado global:** el motor de cálculo (11.1.5.1, 11.1.5.4, 11.1.6.1, 11.1.6.2, 11.1.7.1 y 11.1.7.2) reproduce **los 9 996 valores impresos sin ninguna discrepancia** en las 28 tablas (5A/B/D, 6A/B/D, 23A/B/D, 24A/B/D, 53A/B/D, 54A/B/D, 59A/B/D, 60A/B/D, 6C, 24C, 54C, 60C). Las no conformidades están en la **capa de tablas**: generador, validaciones, redondeo de alpha y funciones combinadas. El núcleo matemático no presenta fallos.

---

<a id="hallazgos"></a>
## Hallazgos

<a id="norm-t01"></a>
### NORM-T01 · El motor numérico reproduce todas las tablas de muestra de la norma: ✅ Conforme
- **Norma:** 11.1.8.1 a 11.1.8.24, tablas de muestra en las págs. PDF 142, 144, 146, 148, 149, 151, 153, 155, 157, 159, 160, 162, 164, 166, 168, 170, 172, 174, 176, 178, 180, 182, 184, 186, 188, 189, 191 y 192.
- **Código:**
  - `table_6x`, `table_24x`, `table_54x`, `table_60x`, `table_6c_24c`, `table_54c` y `table_60c` se usaron directamente.
  - Para 5x, 23x, 53x y 59x se replicó el cuerpo del generador o se usó `correct_observed_to_base[_C]` + conversión + `api_round`.
- **Evidencia:** 28 tablas × 357 valores = 9 996 comparaciones con **0 discrepancias**. Los valores de prueba están en [`tests/data/norm_table_samples.json`](../../tests/data/norm_table_samples.json) (252 casos de las tablas de muestra + 2 casos de regresión).
- **Nota:** en el texto extraído de las tablas 6A/6B/6D (págs. 148-151) las etiquetas de temperatura aparecen desplazadas. La asignación correcta (120.0, 120.1, …, 125.0 en orden) se confirmó porque coincide valor a valor.

<a id="norm-t02"></a>
### NORM-T02 · Conversiones de unidades (11.1.5.1): ✅ Conforme
- **Norma (págs. 30-31):**
  - ρ = 141.5·999.016/(G+131.5)
  - γ60 = ρ/999.016
  - t°F = 1.8·t°C + 32
  - α60,°F = α60,°C/1.8
  - La densidad del agua a 60 °F es 999.016 kg/m³.
- **Código:** `section_5_1.py` (`API_to_rho`, `rho_to_API`, `gamma_t_to_rho`, `rho_to_gamma_t`, `celc_to_fahr`, `alphac_to_alphaf`) aplica estas mismas fórmulas.

<a id="norm-t03"></a>
### NORM-T03 · Presión, temperatura base y procedimiento invocado: ✅ Conforme
- **Norma:**
  - Tablas 5/6/23/24 a 0 psig; tablas 53/54/59/60 a 0 kPa (pág. 139).
  - Base de 60 °F, 15 °C (59 °F) o 20 °C (68 °F).
  - Procedimientos: 5x/23x → 11.1.6.2; 6x/24x/6C/24C → 11.1.6.1; 53x/59x → 11.1.7.2; 54x/60x/54C/60C → 11.1.7.1 (págs. 141-190).
- **Código:**
  - `table_6x` y `table_24x` → `correct_base_to_alternate` (11.1.6.1).
  - `table_54x` y `table_60x` → `correct_observed_to_alternate_C` con `t_b` = 15/20. Esta función hace 11.1.7.1: 11.1.6.2 a T_F, luego 11.1.6.1 a t_F, y CTL = C*TL/CTL,60 (pág. 90, pasos 2-4).
  - 53/59 (generador y funciones combinadas) → `correct_observed_to_base_C` (11.1.7.2: 11.1.6.2 a t_o y 11.1.6.1 a T_F; pág. 102, pasos 2-3).
  - En todas las funciones la presión es `0`.

<a id="norm-t04"></a>
### NORM-T04 · Redondeo de entradas y salidas en las tablas A/B/D: ✅ Conforme
- **Norma:**
  - 11.1.5.4, paso 1 (págs. 37-38), incrementos: °API 0.1; densidad relativa 0.0001; kg/m³ 0.1; °F 0.1; °C 0.05; CTL 0.00001.
  - 11.1.8, pág. 140: «These table representations … are to be generated with rounded input and be represented with rounded output».
- **Código (`tables.py`):**
  - `table_6x`, `table_5x_6x`: API a 0.1 y °F a 0.1.
  - `table_24x`, `table_23x_24x`: densidad relativa a 0.0001 y °F a 0.1.
  - `table_54x`, `table_60x`, `table_53x_54x`, `table_59x_60x`: kg/m³ a 0.1 y °C a 0.05.
  - CTL a 0.00001 en todas.
  - Generador: API60 a 0.1 y γ60 a 0.0001. ρ60 no se redondea antes de convertir (paso 6, pág. 141), como pide la norma.

<a id="norm-t05"></a>
### NORM-T05 · Las tablas C no redondean el coeficiente alpha: ❌ No conforme (impacto bajo)
- **Norma:**
  - 11.1.8.23, paso 2 (pág. 187): «Increment 60 °F thermal expansion coefficient by 0.1×10⁻⁶ °F⁻¹ … Ensure that the value remains rounded consistent with 11.1.5.4».
  - 11.1.8.24, paso 2 (pág. 190): incremento de 0.2×10⁻⁶ °C⁻¹.
  - 11.1.5.4, pág. 37: α en °F⁻¹ a 0.0000001; en °C⁻¹ a 0.0000002.
- **Código:** `tables.py:57-75` (`table_6c_24c`), `146-164` (`table_54c`) y `211-229` (`table_60c`). Redondean la temperatura pero **no** alpha.
- **Evidencia:** `table_6c_24c(alpha_obs=0.00047005, t_f_obs=300.0)` devuelve **0.88424**. Con alpha redondeado a 0.0004700 (regla del par) el resultado es **0.88425**.
- **Corrección:**
```python
alpha_obs = api_round(alpha_obs, 0.0000001)   # table_6c_24c (°F⁻¹)
alpa_obs  = api_round(alpa_obs, 0.0000002)    # table_54c / table_60c (°C⁻¹)
```

<a id="norm-t06"></a>
### NORM-T06 · No se valida el rango de alpha (tablas C): ❌ No conforme
- **Norma:**
  - 11.1.6.1, paso 1 (pág. 40): «230.0×10⁻⁶ °F⁻¹ < α60 < 930.0×10⁻⁶ °F⁻¹ (if α60 … is specified)». Si no se cumple: «Set an error condition … and exit» (pág. 41).
  - Rango de la tabla 6C/24C: 230.0 a 930.0×10⁻⁶ °F⁻¹ (pág. 187).
  - Rango de 54C/60C: 414.0 a 1674.0×10⁻⁶ °C⁻¹ (pág. 190), equivalente al anterior dividido entre 1.8.
- **Código:** `section_6_1.correct_base_to_alternate` (rama `alpha_60 is not None`) y `table_6c_24c`/`table_54c`/`table_60c` no validan.
- **Evidencia:**
  - `table_6c_24c(alpha_obs=0.001, t_f_obs=100)` devuelve 0.95955 en vez de un error.
  - `table_54c(alpa_obs=0.0, …)` lanza `MPMSValidationError: commodity_group must be A, B, or D` (mensaje engañoso, ligado a F-05).
- **Corrección:** al inicio de la rama alpha de `correct_base_to_alternate`:
```python
if not (230.0e-6 <= alpha_60 <= 930.0e-6):
    raise MPMSValidationError(f"alpha_60={alpha_60} °F⁻¹ fuera de 230e-6…930e-6 (11.1.6.1 paso 1)")
```
  En `section_7_1`/`7_2`, cambiar `if alpha_60_c` por `if alpha_60_c is not None`.

<a id="norm-t07"></a>
### NORM-T07 · Tablas C invocadas con `rho_60=0` / `rho_t=0`: ⚠️ Dudoso (resultado correcto, implementación frágil)
- **Norma:**
  - 11.1.8.23, paso 4 (pág. 187): CTL por 11.1.6.1 «specifying the special applications group C». Con α60 dado, el paso 3 usa ρ* = ρ60·exp(½α60Δ60(1+0.4α60Δ60)) y el paso 5 calcula CTL solo con α60 y t*. **CTL no depende de la densidad.**
  - 11.1.8.24, paso 4 (pág. 190): CTL por 11.1.7.1, es decir CTL(t)/CTL(T). Con α dado, CTL,60 tampoco depende de ρ.
- **Código:**
  - `table_6c_24c` (`tables.py:71`): `correct_base_to_alternate(rho_60=0, …, alpha_60=alpha_obs)`.
  - `table_54c`/`table_60c` (`tables.py:160, 225`): `correct_observed_to_alternate_C(rho_t=0, …)`.
- **Veredicto:**
  - Las tablas de muestra 6C, 24C, 54C y 60C (págs. 188, 189, 191 y 192) se reproducen al 100 %.
  - Pero el resultado depende de efectos laterales: los límites ficticios `"c": (-1e7, 1e6)` en `section_6_2.py:51`, la rama `rho_60 <= 0` de `section_6_1.py:81` y la convergencia trivial con δρ = 0 − 0.
  - Si se corrigen F-02/F-08 de la auditoría (validar ρ > 0 al inicio), **las tablas C dejarán de funcionar**.
- **Corrección:** calcular CTL desde alpha sin densidad ficticia:
```python
def ctl_from_alpha(alpha_f: float, t_f: float) -> float:
    """11.1.6.1 pasos 2 y 5 con α60 dado (CTL independiente de ρ60)."""
    validate_temperature_f(t_f)
    dt = its90_to_ipts68(t_f_90=t_f) - T_BASE_IPTS68
    return math.exp(-alpha_f * dt * (1.0 + 0.8 * alpha_f * (dt + DELTA_60)))

def table_6c_24c(*, alpha_obs, t_f_obs):
    a = api_round(alpha_obs, 0.0000001); t = api_round(t_f_obs, 0.1)
    _check_alpha_f(a)
    return api_round(ctl_from_alpha(a, t), 0.00001)

def table_54c(*, alpha_obs, t_c_obs, t_base_c=15):   # 60C: t_base_c=20
    a_c = api_round(alpha_obs, 0.0000002); t = api_round(t_c_obs, 0.05)
    a_f = alphac_to_alphaf(a_c); _check_alpha_f(a_f)
    ctl = ctl_from_alpha(a_f, celc_to_fahr(t)) / ctl_from_alpha(a_f, celc_to_fahr(t_base_c))
    return api_round(ctl, 0.00001)          # 11.1.7.1 paso 4: CTL = C*TL / CTL,60
```
  Además: renombrar el parámetro `alpa_obs` a `alpha_obs`.
  **Ya validado:** esta propuesta reproduce los 1 428 valores impresos de 6C, 24C, 54C y 60C (págs. 188-192) sin discrepancias. Los casos de prueba son `EX-6C-*`, `EX-24C-*`, `EX-54C-*` y `EX-60C-*` del JSON.

<a id="norm-t08"></a>
### NORM-T08 · `generar_tabla_23a` convierte la temperatura en vez de la densidad relativa: ❌ No conforme (confirmado)
- **Norma:** 11.1.8.6, paso 4 (pág. 152): «Convert density units from relative density to kg/m³ using procedure in 11.1.5.1».
- **Código:** `generator_tables.py:317`: `rho_o = gamma_t_to_rho(t_obs_raw)`.
- **Evidencia:**
  - Para γobs = 0.8270 y t = 90.0 °F la norma imprime **0.8393** (pág. 153). El generador calcula ρo = 89 911.44, no converge e imprime `-`.
  - De las 3 601 columnas solo 5 (t = 0.7 a 1.1 °F) producen un valor, y ese valor no depende de la fila (p. ej., 0.9795 en todas las filas a 1.0 °F; el correcto para 0.8270 a 1.0 °F es 0.8021).
  - El `except:` desnudo oculta el error (ver NORM-T13).
- **Segundo defecto (rango, paso 2):** `np.arange(0.4710, 1.199, 0.0001)` genera **7 281** valores (ceil(7280.000…)), así que añade la fila **1.1990**, fuera del rango normativo 0.4710–1.1989.
- **Corrección:**
```python
rel_range = [i / 10000 for i in range(4710, 11990)]      # 0.4710 … 1.1989 (7 280 filas)
...
rho_o = gamma_t_to_rho(rel_obs)                          # densidad relativa redondeada, no la temperatura
```

<a id="norm-t09"></a>
### NORM-T09 · Rangos del generador para 5A, 5B, 5D, 6A, 6B, 6D y temperatura: ✅ Conforme (con fragilidad)
| Tabla | Norma (pág. PDF) | Código | Resultado |
|---|---|---|---|
| 5A | −13.4 a 168.9 °API, Δ 0.1 (141) | `arange(-13.4,169,0.1)` → 1 824 valores, último 168.9 | ✅ |
| 5B | −14.2 a 168.9 °API (143) | `arange(-14.2,169,0.1)` → 1 832, último 168.9 | ✅ |
| 5D | −14.1 a 66.3 °API (145) | `arange(-14.1,66.4,0.1)` → 805, último 66.3 | ✅ |
| 6A/6B | −10.0 a 100.0 °API (147) | `arange(-10,100.1,0.1)` → 1 101, último 100.0 | ✅ |
| 6D | −10.0 a 45.0 °API (150) | `arange(-10,45.1,0.1)` → 551, último 45.0 | ✅ |
| Temperatura °F | −58.0 a 302.0, Δ 0.1 (141-158) | `arange(-58.0,302.1,0.1)` → 3 601, último 302.0 | ✅ |
| 23A | 0.4710 a 1.1989, Δ 0.0001 (152) | 7 281 valores, último 1.1990 | ❌ (NORM-T08) |

Los recuentos se obtuvieron emulando `numpy.arange`: n = ceil((stop−start)/step). Funciona hoy, pero depende del error de coma flotante (N-03). Se recomienda iterar sobre enteros, p. ej. `[i/10 for i in range(-134, 1690)]`.

<a id="norm-t10"></a>
### NORM-T10 · Funciones combinadas `table_5x_6x`, `table_23x_24x`, `table_53x_54x` y `table_59x_60x`: ❌ No conforme (no son tablas normativas y su resultado difiere del procedimiento normativo)
- **Norma:**
  - §11.1.8 (pág. 139) define cada tabla por separado. Las impares (5, 23, 53, 59) dan la **densidad base**; las pares (6, 24, 54, 60) dan **CTL contra densidad base**. **Ninguna** encadena «observada → base redondeada → CTL».
  - 11.1.3.9 (pág. 28): «When the tabular representations are calculated, the initial and final values are to be rounded for display, **but intermediate values are never to be rounded**».
  - El CTL a partir de una densidad observada es el resultado directo de 11.1.6.2, paso 7 (pág. 59: «set the value of CTPL to the last C(m)TPL value … Round this value») o de 11.1.7.2, paso 4 (pág. 102).
- **Código:**
  - `tables.py:31-55`: API60 se redondea a 0.1 y luego entra en 11.1.6.1.
  - `99-123`: γ60 se redondea a 0.0001.
  - `166-188` y `231-253`: ρ15/ρ20 se redondea a 0.1 y luego se aplica 11.1.7.1.
  - Además, el docstring dice «API MPMS 11.1.6.2».
- **Evidencia:** comparación con el CTL directo de 11.1.6.2 / 11.1.7.2, redondeado a 1e-5.

| Función | Casos | Coinciden | Peor diferencia |
|---|---|---|---|
| `table_5x_6x` | 1 855 | 40 % | **23e-5** (API 76.6, 248.2 °F, B: 0.87934 frente a 0.87911) |
| `table_23x_24x` | 1 330 | 80 % | 5e-5 |
| `table_53x_54x` | 1 482 | 80 % | 6e-5 |
| `table_59x_60x` | 1 482 | 80 % | 5e-5 |

- **Respuesta a la pregunta 3:** la cadena «observada → base → CTL» solo reproduce la **consulta manual de dos tablas impresas** (práctica histórica). La norma 11.1 de 2004 no la define y prohíbe redondear el valor intermedio en el cálculo algorítmico.
- **Corrección (recomendada):** devolver el CTL del propio procedimiento de corrección observada → base:
```python
def table_5x_6x(*, api_obs, t_f_obs, commodity_type):
    api_obs = api_round(api_obs, 0.1); t = api_round(t_f_obs, 0.1)
    _, CTL, _, _, _ = correct_observed_to_base(rho_o=API_to_rho(api_obs), t_o=t, p_o=0,
                                               commodity_type=commodity_type)   # 11.1.6.2 paso 7
    return api_round(CTL, 0.00001)

def table_53x_54x(*, den_obs, t_c_obs, commodity_type):      # 59x_60x: t_b=20
    den_obs = api_round(den_obs, 0.1); t = api_round(t_c_obs, 0.05)
    _, _, CTL, _, _, _ = correct_observed_to_base_C(rho_o=den_obs, t_o_c=t, p_o=0, t_b=15,
                                                    commodity_type=commodity_type)  # 11.1.7.2 paso 4
    return api_round(CTL, 0.00001)
```
  Para `table_23x_24x` se aplica lo mismo con `gamma_t_to_rho`. Si se quiere conservar la emulación manual, debe renombrarse (p. ej. `lookup_5x_then_6x`) y documentarse como **no** normativa.
- **Supuesto implícito:** las funciones usan la misma temperatura para la densidad observada y para el volumen. Conviene documentarlo.

<a id="norm-t11"></a>
### NORM-T11 · `table_6x` y `table_24x` no rechazan densidades base fuera de rango: ❌ No conforme
- **Norma:** 11.1.6.1, paso 1 (págs. 40-41): ρ60,min ≤ ρ60 ≤ ρ60,max. A/B: 610.6 a 1163.5 kg/m³; D: 800.9 a 1163.5. Si no se cumple: «Set an error condition … and exit procedure». Rangos de tabla: 6A/6B −10 a 100 °API (pág. 147); 6D −10 a 45 (pág. 150); 24A/24B 0.6113 a 1.1646 (pág. 158); 24D 0.8017 a 1.1646 (pág. 161).
- **Código:** `section_6_1.py:57-60` → `resolve_commodity_group` (`constants/commodity_groups.py`). Si la densidad no está en ningún subgrupo, devuelve **el más cercano** en lugar de dar error.
- **Evidencia:**
  - `table_6x(api_base=100.5, t_f_obs=100, 'A')` devuelve 0.96287.
  - `table_6x(api_base=-10.5, …)` devuelve 0.98997.
  - `table_6x(api_base=46, …, 'D')` devuelve 0.98239.
  - Los bordes exactos (−10.0, 100.0, 45.0, 0.6113, 0.8017 y 1.1646, a −58, 60 y 302 °F) sí calculan bien.
- **Corrección:** en `correct_base_to_alternate`, cuando `alpha_60 is None` (y no dentro de la iteración de 6.2, cuyo paso 3 dice «Do not check the input values»):
```python
LIM = {"a": (610.6, 1163.5), "b": (610.6, 1163.5), "d": (800.9, 1163.5)}
lo, hi = LIM[commodity_group.lower()]
if check_range and not (lo <= rho_60 <= hi):
    raise MPMSValidationError(f"rho_60={rho_60} fuera de [{lo}, {hi}] (11.1.6.1 paso 1)")
```
  Usar `check_range=False` en las llamadas internas desde `section_6_2`.

<a id="norm-t12"></a>
### NORM-T12 · Tablas 54x/60x (11.1.7.1): rangos y procedimiento: ✅ Conforme
- **Norma:** 54A 611.2 a 1163.7; 54B 611.2 a 1163.8; 54D 801.3 a 1163.8 kg/m³ (págs. 169, 171, 173). 60A 606.2 a 1161.1; 60B 606.2 a 1160.6; 60D 798.2 a 1160.7 (págs. 181, 183, 185). Temperatura de −50.00 a 150.00 °C con Δ 0.05.
- **Evidencia:**
  - Los extremos de cada rango calculan bien a −50, 15, 20 y 150 °C.
  - Justo fuera del rango (611.1 a 15 °C; 1163.8 en A; 606.1 y 1161.2 a 20 °C) se lanza una excepción, porque 11.1.6.2 no encuentra un ρ60 válido. Esto es consistente con 11.1.7.1, paso 2 (pág. 90): «If this procedure returns with an error condition … exit». El tipo de error se trata en NORM-T13.

<a id="norm-t13"></a>
### NORM-T13 · Qué imprimir cuando el cálculo no es posible: ⚠️ Dudoso (la norma no lo prescribe para tablas)
- **Norma:**
  - Los procedimientos dicen «Set an error condition (**such as setting all output values to zero**) and exit»: 11.1.6.1 paso 1 (pág. 41); 11.1.6.2 pasos 1, 6 y 7 (págs. 57 y 59); 11.1.7.1/11.1.7.2 paso 2 (págs. 90 y 102).
  - §11.1.8 **no** indica cómo representar esas celdas en la tabla impresa, y las tablas de muestra solo contienen celdas válidas.
  - Para el grupo B existe una excepción (pág. 59): si no converge cerca de un límite de subgrupo, «the density from the last iteration may be used … and the result should be flagged».
- **Código:**
  - `generar_tabla_5a`, `5b`, `6b`, `6d` y `23a` usan `except:` desnudo e imprimen `'-'`.
  - `generar_tabla_6a` imprime la excepción y escribe `'-'`.
  - `generar_tabla_5d` solo captura `MPMSConvergenceError`.
  - Una celda fuera de rango se reporta como `MPMSConvergenceError` y no como error de rango. Ejemplos: 5A con API 168.9 a −58 °F, o con −13.4 a 302 °F.
  - El `except:` desnudo hizo invisible el defecto de NORM-T08.
- **Corrección recomendada:**
  - Celda **vacía** (o `'-'` documentado) para cualquier condición de error. **Nunca 0**: un CTL o una densidad de 0 se puede confundir con un dato.
  - Capturar solo `(MPMSValidationError, MPMSConvergenceError)`.
  - Validar el rango de ρo (11.1.6.2 paso 1: A 470.5 a 1201.8; B 470.4 a 1209.5; D 714.3 a 1208.3 kg/m³) y el de ρ60 tras converger (paso 7), para separar «fuera de rango» de «no converge».
  - Opcional: aplicar la nota del grupo B, usando la última iteración con una marca.
  - En un barrido de 133 900 celdas de 5B (API 30 a 56, todas las temperaturas) no hubo ninguna falta de convergencia dentro del rango.

<a id="norm-t14"></a>
### NORM-T14 · Cobertura del generador y de las funciones: ⚠️ Incompleto
- **Norma:** §11.1.8 define 28 tablas de temperatura más las dos de compresibilidad, 11.2.1 y 11.2.1M (11.1.8.25/26, págs. 193-195).
- **Código:** `generator_tables.py` solo genera 5A, 5B, 5D, 6A, 6B, 6D y 23A. Faltan:

| Tabla | Rango normativo (pág. PDF) | Procedimiento |
|---|---|---|
| 23B | γ 0.4709 a 1.2065 (154) | 11.1.6.2, B |
| 23D | γ 0.7151 a 1.2053 (156) | 11.1.6.2, D |
| 24A/24B | γ60 0.6113 a 1.1646 (158) | 11.1.6.1 |
| 24D | γ60 0.8017 a 1.1646 (161) | 11.1.6.1, D |
| 53A / 59A | 470.6 a 1197.7 kg/m³ (163 / 175) | 11.1.7.2 |
| 53B / 59B | 470.5 a 1205.4 (165 / 177) | 11.1.7.2 |
| 53D / 59D | 714.5 a 1204.1 (167 / 179) | 11.1.7.2 |
| 54A/B/D, 60A/B/D | ver NORM-T12 | 11.1.7.1 |
| 6C/24C | α 230.0 a 930.0e-6 °F⁻¹, Δ 0.1e-6, −58 a 302 °F (187) | 11.1.6.1, C |
| 54C/60C | α 414.0 a 1674.0e-6 °C⁻¹, Δ 0.2e-6, −50 a 150 °C (190) | 11.1.7.1, C |
| 11.2.1 / 11.2.1M | (193 / 195) | Fp |

  En `tables.py` tampoco hay funciones puntuales para las tablas impares, que devuelven la densidad base:
  - 5x (API60)
  - 23x (γ60)
  - 53x (ρ15)
  - 59x (ρ20)

  Hoy esas salidas solo existen dentro de las funciones combinadas o en el generador. Se sugiere añadir `table_5x`, `table_23x`, `table_53x` y `table_59x`, con redondeo final de 0.1 °API, 0.0001 y 0.1 kg/m³.

<a id="norm-t15"></a>
### NORM-T15 · Erratas de la propia norma y cómo las interpreta el código: ⚠️ Informativo
- **59A/59B/59D (págs. 175, 177 y 179):** el texto de entradas y salidas copia el de la tabla 60 («Base density … Output: CTL … procedure in 11.1.7.2»). Sin embargo, el título y la tabla de muestra (pág. 176: «Corresponding Density at 20 °C») muestran que la salida es la **densidad base a 20 °C** por 11.1.7.2. El código usa esta interpretación correcta.
- **54C/60C, paso 3 (pág. 190):** dice «0.05 °F», pero el rango está en °C (−50.00 a 150.00 °C). El código usa 0.05 °C, que es lo correcto.
- **23D, paso 5 (pág. 156):** dice «"AD"»; **24D, paso 5 (pág. 161):** dice «"A" or "BD"». Debe leerse «D». El código usa D.
- **24D, paso 2:** el rango empieza en 0.8017, equivalente a ρ60 = 800.9 kg/m³. Es coherente.

<a id="norm-t16"></a>
### NORM-T16 · Formato de salida del generador: ⚠️ Menor
- **Norma:**
  - Las tablas de muestra (p. ej., pág. 142) ponen la **temperatura en filas** y la densidad o API en columnas.
  - Las tablas impares llevan el encabezado «If hydrometer used to determine density, apply glass correction before entering table» (pág. 140: las tablas no incluyen corrección de hidrómetro).
- **Código:** el generador pone la densidad en filas y la temperatura en columnas, y no incluye la nota del hidrómetro. Los valores no cambian, pero el formato no es el histórico. Se recomienda trasponer y añadir la nota en el CSV.

<a id="norm-t17"></a>
### NORM-T17 · Referencias normativas en los docstrings: ⚠️ Menor
- **Código:** todas las funciones `table_*` citan «API MPMS 11.1.6.2» y declaran `Tuple[...]`, pero devuelven un `float` (ver F-04).
- **Corrección:** citar la sección correcta en cada función:
  - `table_6x`: 11.1.8.4/11.1.8.5 + 11.1.6.1
  - `table_24x`: 11.1.8.9/11.1.8.10
  - `table_54x`: 11.1.8.14-16 + 11.1.7.1
  - `table_60x`: 11.1.8.20-22
  - `table_6c_24c`: 11.1.8.23
  - `table_54c`/`table_60c`: 11.1.8.24

---

<a id="tabla-resumen-por-funci-n"></a>
## Tabla resumen por función

| Función | Tabla(s) normativa(s) | Entradas y redondeo | Procedimiento | Redondeo de salida | Rangos y errores | Veredicto |
|---|---|:---:|:---:|:---:|:---:|:---:|
| `table_6x` | 6A, 6B, 6D (11.1.8.4-5) | ✅ | ✅ 11.1.6.1 | ✅ CTL 1e-5 | ❌ no rechaza API fuera de rango (T11) | ⚠️ conforme dentro de rango |
| `table_5x_6x` | ninguna (5x+6x encadenadas) | ✅ | ❌ redondea API60 intermedio (T10) | ✅ | ⚠️ (T13) | ❌ |
| `table_6c_24c` | 6C, 24C (11.1.8.23) | ❌ alpha sin redondear (T05) | ⚠️ `rho_60=0` (T07) | ✅ | ❌ sin validar alpha (T06) | ❌ (impacto bajo) |
| `table_24x` | 24A, 24B, 24D (11.1.8.9-10) | ✅ | ✅ 11.1.6.1 | ✅ | ❌ (T11) | ⚠️ conforme dentro de rango |
| `table_23x_24x` | ninguna (23x+24x) | ✅ | ❌ redondea γ60 intermedio (T10) | ✅ | ⚠️ | ❌ |
| `table_54x` | 54A, 54B, 54D (11.1.8.14-16) | ✅ | ✅ 11.1.7.1 (T=15 °C) | ✅ | ✅ error fuera de rango (tipo, T13) | ✅ |
| `table_54c` | 54C (11.1.8.24) | ❌ alpha (T05) | ⚠️ `rho_t=0` (T07) | ✅ | ❌ (T06); alpha=0 da error engañoso | ❌ (impacto bajo) |
| `table_53x_54x` | ninguna (53x+54x) | ✅ | ❌ redondea ρ15 intermedio (T10) | ✅ | ⚠️ | ❌ |
| `table_60x` | 60A, 60B, 60D (11.1.8.20-22) | ✅ | ✅ 11.1.7.1 (T=20 °C) | ✅ | ✅ (T12) | ✅ |
| `table_60c` | 60C (11.1.8.24) | ❌ alpha (T05) | ⚠️ `rho_t=0` (T07) | ✅ | ❌ (T06) | ❌ (impacto bajo) |
| `table_59x_60x` | ninguna (59x+60x) | ✅ | ❌ redondea ρ20 intermedio (T10) | ✅ | ⚠️ | ❌ |
| `generar_tabla_5a` | 5A (11.1.8.1) | ✅ | ✅ 11.1.6.2 «A» | ✅ API60 0.1 | ✅ rango; ⚠️ `except:` (T13) | ✅ |
| `generar_tabla_5b` | 5B (11.1.8.2) | ✅ | ✅ «B» | ✅ | ✅ / ⚠️ | ✅ |
| `generar_tabla_5d` | 5D (11.1.8.3) | ✅ | ✅ «D» | ✅ | ✅ / ⚠️ solo captura convergencia | ✅ |
| `generar_tabla_6a` | 6A (11.1.8.4) | ✅ | ✅ 11.1.6.1 | ✅ | ✅ / ⚠️ `print(e)` | ✅ |
| `generar_tabla_6b` | 6B (11.1.8.4) | ✅ | ✅ | ✅ | ✅ / ⚠️ | ✅ |
| `generar_tabla_6d` | 6D (11.1.8.5) | ✅ | ✅ | ✅ | ✅ / ⚠️ | ✅ |
| `generar_tabla_23a` | 23A (11.1.8.6) | ❌ usa la temperatura como densidad (T08) | ❌ (resultado inválido) | ✅ γ60 0.0001 | ❌ fila extra 1.1990 | ❌ crítico |
| (sin generador) | 23B, 23D, 24x, 53x, 54x, 59x, 60x, C, 11.2.1(M) | — | — | — | — | ⚠️ cobertura (T14) |

**Archivo de pruebas:** [`tests/data/norm_table_samples.json`](../../tests/data/norm_table_samples.json) contiene 252 valores de las tablas de muestra (3 temperaturas × 3 columnas × 28 tablas, todos reproducidos por el motor de `4f1216d`). Incluye además `EX-23A-BUG` (regresión de T08) y `EX-6C-ROUND` (redondeo de alpha, T05; el valor esperado es calculado, no impreso en la norma). La comparación completa de 9 996 valores se hizo con scripts temporales no versionados; la suite conserva la muestra de 254 casos.

---

[⬅ Anterior: Anexo A — Núcleo](11_anexo_norma_nucleo.md) · [Índice](README.md)
