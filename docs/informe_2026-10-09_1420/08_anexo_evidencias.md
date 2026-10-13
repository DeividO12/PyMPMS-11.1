# 08 · Anexo de evidencias

[⬅ Anterior: Calidad y mantenibilidad](07_calidad_mantenibilidad.md) · [Índice](README.md) · [Siguiente: Plan de acción ➡](09_plan_de_accion.md)

> [!NOTE]
> Estas evidencias corresponden al código auditado (`4f1216d`). Con la versión `1.0.0` los mismos casos lanzan `MPMSValidationError` / `MPMSRangeError` o dan el resultado correcto, como documenta la sección **Resolución** de cada hallazgo.

Scripts usados para verificar los hallazgos y la salida obtenida. Todos se ejecutaron desde la raíz del repositorio con `python -I` y `src` añadido a `sys.path`, sin modificar el código de la librería.

## 📑 Contenido

1. [Entorno](#a-entorno)
2. [Casos borde (validación y errores)](#a-casos-borde)
3. [Redondeo `api_round` vs `Decimal`](#a-redondeo)
4. [Barrido de convergencia](#a-convergencia)
5. [Divergencia entre implementaciones de tablas](#a-divergencia)
6. [Importación del generador](#a-generador)
7. [Ejemplos de referencia y propiedad de ida y vuelta](#a-referencia)
8. [Tiempos](#a-tiempos)

---

<a id="a-entorno"></a>
## A.1 Entorno

| Elemento | Valor |
|---|---|
| Python | 3.12.10 |
| SO | Windows 11 Pro 10.0.26200 |
| Rama / commit | `dev_deivid` / `4f1216d` |
| `numpy`, `pandas`, `pytest` | **No instalados** |
| `git config core.ignorecase` | `true` |
| Directorio en git | `src/api_mpms/Tables/` |
| Directorio en disco | `src/api_mpms/tables/` |

---

<a id="a-casos-borde"></a>
## A.2 Casos borde

<details>
<summary><b>Script</b> (clic para expandir)</summary>

```python
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate as b2a
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base as o2b
from api_mpms.mpms_11_1.section_7_1 import correct_observed_to_alternate_C
from api_mpms.mpms_11_1.section_7_2 import correct_observed_to_base_C
from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68
from api_mpms.validators.inputs import validate_pressure_psig

def tryit(label, f):
    try: print(label, "->", repr(f()))
    except Exception as e: print(label, "-> EXC", type(e).__name__, e)

tryit("pressure nan", lambda: validate_pressure_psig(float('nan')))
tryit("pressure None", lambda: validate_pressure_psig(None))
tryit("b2a rho=0 A", lambda: b2a(0, 60, 0, commodity_group='A'))
tryit("b2a rho=-800 A", lambda: b2a(-800, 60, 0, commodity_group='A'))
tryit("b2a rho=5000 A", lambda: b2a(5000, 60, 0, commodity_group='A'))
tryit("b2a rho=nan A", lambda: b2a(float('nan'), 60, 0, commodity_group='A'))
tryit("b2a alpha, rho=0, p=1000", lambda: b2a(0, 100, 1000, alpha_60=0.0005))
tryit("b2a group 'C' sin alpha", lambda: b2a(800, 60, 0, commodity_group='C'))
tryit("b2a alpha=1.0", lambda: b2a(800, 300, 0, alpha_60=1.0))
tryit("b2a alpha negativo", lambda: b2a(800, 100, 0, alpha_60=-0.001))
tryit("b2a group int", lambda: b2a(800, 60, 0, commodity_group=1))
tryit("o2b type None", lambda: o2b(rho_o=800, t_o=60, p_o=0, commodity_type=None))
tryit("o2b type c sin alpha", lambda: o2b(rho_o=800, t_o=60, p_o=0, commodity_type='c'))
tryit("o2b rho_o=nan", lambda: o2b(rho_o=float('nan'), t_o=60, p_o=0, commodity_type='a'))
tryit("o2b rho_o=-5", lambda: o2b(rho_o=-5, t_o=60, p_o=0, commodity_type='a'))
tryit("o2b p nan", lambda: o2b(rho_o=800, t_o=60, p_o=float('nan'), commodity_type='a'))
tryit("o2b C rho=0 p=500", lambda: o2b(rho_o=0, t_o=100, p_o=500, commodity_type='c', alpha_60=0.0005))
tryit("o2b C rho=1e-3 p=500", lambda: o2b(rho_o=1e-3, t_o=100, p_o=500, commodity_type='c', alpha_60=0.0005))
tryit("7_1 alpha_c=0.0", lambda: correct_observed_to_alternate_C(rho_t=0, t_a_c=30, p_a=0, commodity_type='C', alpha_60_c=0.0))
tryit("7_1 commodity None", lambda: correct_observed_to_alternate_C(rho_t=850, t_a_c=30, p_a=0))
tryit("7_2 len", lambda: len(correct_observed_to_base_C(rho_o=850, t_o_c=30, p_o=0, commodity_type='A')))
tryit("5_3 ambas", lambda: its90_to_ipts68(t_f_90=212, t_c_90=0))
tryit("5_3 out None", lambda: its90_to_ipts68(t_f_90=212, out_fahrenheit=None))
```
</details>

**Salida:**

```text
pressure nan -> nan
pressure None -> EXC TypeError '<' not supported between instances of 'NoneType' and 'int'
b2a rho=0 A -> EXC ZeroDivisionError float division by zero
b2a rho=-800 A -> (-800.0000000009654, 1.0000000000012068, 0.0, 1.0, 1.0000000000012068, 0.0005329581256723363)
b2a rho=5000 A -> (5000.000000000155, 1.0000000000000309, 0.14237326487831112, 1.0, 1.0000000000000309, 1.3643825440420518e-05)
b2a rho=nan A -> (nan, nan, nan, nan, nan, nan)
b2a alpha, rho=0, p=1000 -> (0.0, 0.9798796586333338, 0.0, 1.0, 0.9798796586333338, 0.0005)
b2a group 'C' sin alpha -> EXC MPMSValidationError commodity_group must be A, B, or D
b2a alpha=1.0 -> (0.0, 0.0, 1.4114600051803052, 1.0, 0.0, 1.0)
b2a alpha negativo -> (831.5912937632614, 1.0394891172040768, 0.6857459319611954, 1.0, 1.0394891172040768, -0.001)
b2a group int -> EXC AttributeError 'int' object has no attribute 'lower'
o2b type None -> EXC AttributeError 'NoneType' object has no attribute 'lower'
o2b type c sin alpha -> EXC MPMSValidationError commodity_group must be A, B, or D
o2b rho_o=nan -> EXC MPMSConvergenceError API MPMS 11.1.6.2 did not converge within 15 iterations rho_o: nan - t_o: 60
o2b rho_o=-5 -> EXC MPMSConvergenceError API MPMS 11.1.6.2 did not converge within 15 iterations rho_o: -5 - t_o: 60
o2b p nan -> EXC MPMSConvergenceError API MPMS 11.1.6.2 did not converge within 15 iterations rho_o: 800 - t_o: 60
o2b C rho=0 p=500 -> (0, 0.9798796586333338, 0.0, 1.0, 0.9798796586333338)
o2b C rho=1e-3 p=500 -> EXC OverflowError math range error
7_1 alpha_c=0.0 -> EXC MPMSValidationError commodity_group must be A, B, or D
7_1 commodity None -> EXC AttributeError 'NoneType' object has no attribute 'lower'
7_2 len -> 6
5_3 ambas -> 32.0
5_3 out None -> 100.02564667518497
```

| Hallazgos respaldados |
|---|
| [F-02](01_errores_funcionales.md#f-02), [F-05](01_errores_funcionales.md#f-05), [F-06](01_errores_funcionales.md#f-06), [F-07](01_errores_funcionales.md#f-07), [F-08](01_errores_funcionales.md#f-08), [V-01](02_validacion_y_errores.md#v-01), [V-03](02_validacion_y_errores.md#v-03), [V-04](02_validacion_y_errores.md#v-04), [V-05](02_validacion_y_errores.md#v-05), [V-06](02_validacion_y_errores.md#v-06) |

---

<a id="a-redondeo"></a>
## A.3 Redondeo `api_round` vs `Decimal`

<details>
<summary><b>Script</b></summary>

```python
from decimal import Decimal
from api_mpms.mpms_11_1.section_5_4 import api_round

def check(values, delta, tol):
    bad = []
    for s in values:
        r = api_round(float(s), delta)
        q = (Decimal(s) / Decimal(str(delta))).quantize(Decimal('1'), rounding='ROUND_HALF_EVEN') * Decimal(str(delta))
        if abs(r - float(q)) > tol:
            bad.append((s, r, float(q)))
    return bad

# Empates exactos en decimal
rho_ties  = [f'{i/10 + 0.05:.2f}'        for i in range(6106, 11635)]   # 610.65 … 1163.45
ctl_ties  = [f'{i/100000 + 0.000005:.6f}' for i in range(80000, 110000)] # 0.800005 … 1.099995
tc_ties   = [f'{i/20 + 0.025:.3f}'        for i in range(-1200, 6100)]   # °C, δ = 0.05
all_ties  = [f'{i/10 + 0.05:.2f}'         for i in range(20000)]         # 0.05 … 1999.95

for name, vals, d, tol in [('rho', rho_ties, 0.1, 1e-9), ('CTL', ctl_ties, 0.00001, 1e-12),
                           ('t_C', tc_ties, 0.05, 1e-9), ('0-2000', all_ties, 0.1, 1e-9)]:
    bad = check(vals, d, tol)
    print(name, len(vals), len(bad), bad[:3])

print(api_round(0.75, 0.25), api_round(12.5, 2.5), api_round(-0.01, 0.1))
```
</details>

**Salida:**

```text
rho     5529   901  [('611.15', 611.1, 611.2), ('611.55', 611.5, 611.6), ('612.15', 612.1, 612.2)]
CTL    30000  7874  [('0.800055', 0.80005, 0.80006), ('0.800075', 0.80007, 0.80008), ('0.800155', 0.80015, 0.80016)]
t_C     7300   298  [('205.075', 205.05, 205.1), ('205.575', 205.55, 205.6), ('206.075', 206.05, 206.1)]
0-2000 20000  2512  [('410.15', 410.1, 410.2), ('411.15', 411.1, 411.2), ('412.15', 412.1, 412.2)]
0.8 12.0 -0.0
```

| Hallazgos respaldados |
|---|
| [N-01](03_precision_numerica.md#n-01), [N-02](03_precision_numerica.md#n-02) |

---

<a id="a-convergencia"></a>
## A.4 Barrido de convergencia

<details>
<summary><b>Script</b></summary>

```python
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base as o2b

for ct in 'abd':
    n = f = 0; failing_rho = set()
    for i in range(233):                    # 600 … 1180 kg/m³, paso 2.5
        rho = 600 + i * 2.5
        for j in range(91):                 # -58 … 302 °F, paso 4
            t = -58 + j * 4; n += 1
            try:
                o2b(rho_o=rho, t_o=t, p_o=0, commodity_type=ct)
            except Exception:
                f += 1; failing_rho.add(rho)
    print(ct, n, f, min(failing_rho), max(failing_rho))

# Zona de transición del tipo B (740-840 kg/m³, paso 0.25)
...
```
</details>

**Salida:**

```text
tipo  casos  fallos  ρ mín. con fallo  ρ máx. con fallo  fallos en zona media
a     21203  1916    600.0             1180.0            1092.5–1097.5
b     21203  2108    600.0             1180.0            1075.0–1097.5
d     21203  8077    600.0             1180.0            1080.0–1097.5
b zona transición (740–840 kg/m³)  14800 casos  0 fallos
```

Todos los fallos son `MPMSConvergenceError` en combinaciones cuyo `rho_60` cae fuera de los límites del tipo.

| Hallazgos respaldados |
|---|
| [V-05](02_validacion_y_errores.md#v-05), [F-10](01_errores_funcionales.md#f-10) |

---

<a id="a-divergencia"></a>
## A.5 Divergencia entre implementaciones de tablas

```python
from api_mpms.mpms_11_1.tables import table_6x as a, table_53x_54x as a2
from api_mpms.tables.table_6x import table_6x as b
from api_mpms.tables.table_53x_54x import table_53x_54x as b2

print(a(api_base=30.04, t_f_obs=80.04, commodity_type='A'),  b(api_base=30.04, t_f_obs=80.04, commodity_type='A'))
print(a(api_base=35.06, t_f_obs=150.06, commodity_type='B'), b(api_base=35.06, t_f_obs=150.06, commodity_type='B'))
print(a2(den_obs=850.06, t_c_obs=40.03, commodity_type='A'), b2(den_obs=850.06, t_c_obs=40.03, commodity_type='A'))
```

```text
0.99107 0.99105
0.95783 0.95787
0.97945 0.97947
```

| Hallazgos respaldados |
|---|
| [E-01](04_estructura_empaquetado.md#e-01) |

---

<a id="a-generador"></a>
## A.6 Importación del generador

```text
$ python -I -c "import sys; sys.path.insert(0,'src'); import api_mpms.tables.generator_tables"
ModuleNotFoundError: No module named 'exceptions'

$ python -I -c "import sys; sys.path.insert(0,'src/api_mpms'); import tables.generator_tables"
ModuleNotFoundError: No module named 'api_mpms'

$ python -I -c "import numpy"
ModuleNotFoundError: No module named 'numpy'
```

| Hallazgos respaldados |
|---|
| [F-03](01_errores_funcionales.md#f-03), [E-03](04_estructura_empaquetado.md#e-03) |

---

<a id="a-referencia"></a>
## A.7 Ejemplos de referencia y propiedad de ida y vuelta

Comparación programática con los valores esperados de los docstrings de `tests/` — ver tabla en [T-01](05_pruebas.md#t-01). Todos coinciden con error < 5e-13.

Propiedad 6.1 → 6.2 (tipo A, 5 000 muestras aleatorias, `random.seed(1)`, ρ₆₀ ∈ [620, 1150], t ∈ [−58, 302], p ∈ [0, 1500]):

```text
fallos: 0   error máximo |ρ₆₀_recuperada − ρ₆₀|: 1.134e-06 kg/m³
```

---

<a id="a-tiempos"></a>
## A.8 Tiempos

```text
correct_observed_to_base   ≈ 20.7 µs/llamada   (20 000 repeticiones)
correct_base_to_alternate  ≈  5.5 µs/llamada
api_round actual           ≈  1.4 µs/llamada  (100 000 repeticiones)
api_round con Decimal      ≈  3.9 µs/llamada
Estimación tabla 5A (1 824 × 3 601 celdas, solo 6.2): ≈ 2.3 min
```

| Hallazgos respaldados |
|---|
| [P-01](06_rendimiento.md#p-01), [P-03](06_rendimiento.md#p-03) |

---

[⬅ Anterior: Calidad y mantenibilidad](07_calidad_mantenibilidad.md) · [Índice](README.md) · [Siguiente: Plan de acción ➡](09_plan_de_accion.md)
