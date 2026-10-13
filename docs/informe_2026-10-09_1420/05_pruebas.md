# 05 · Pruebas

[⬅ Anterior: Estructura y empaquetado](04_estructura_empaquetado.md) · [Índice](README.md) · [Siguiente: Rendimiento ➡](06_rendimiento.md)

## 📑 Contenido

| ID | Severidad | Título | Cierre |
|---|---|---|:---:|
| [T-01](#t-01) | 🟠 Alto | Los tests no son pruebas automatizadas | ✅ 100 % |
| [T-02](#t-02) | 🟡 Medio | Módulos sin ninguna cobertura | ✅ 100 % |
| [T-03](#t-03) | 🔵 Bajo | Sin configuración de pytest ni integración continua | ✅ 100 % |
| [Propuesta](#propuesta-de-suite-de-pruebas) | — | Suite de pruebas sugerida |

---

<a id="t-01"></a>
## T-01 · Los tests no son pruebas automatizadas — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟠 Alto | [`tests/test_6_1.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/tests/test_6_1.py), [`tests/test_6_2.py`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/src/api_mpms/tests/test_6_2.py) | ✅ |

### Descripción

Los dos archivos son *scripts* que imprimen resultados con `print(...)` a nivel de módulo:

- **No hay funciones `test_*`** → `pytest` recolecta **0 pruebas** (y ejecuta los `print` durante la recolección).
- **No hay `assert`** → nada falla aunque el resultado cambie.
- Los valores esperados están en *docstrings* sueltos; la comparación debe hacerse a ojo.
- `pytest` ni siquiera está instalado en el entorno (`No module named pytest`).

### Evidencia: los valores sí coinciden hoy

Al comparar programáticamente la salida actual con los valores esperados escritos en los docstrings, **todos** los ejemplos coinciden con error < 5e-13:

| Ejemplo | Magnitud comparada | Obtenido | Esperado | Error abs. |
|---|---|---|---|---|
| 6.1 Ej. 1 | CTL | 1.0330115919579348 | 1.033011591958 | 6.5e-14 |
| 6.1 Ej. 2 | CTPL | 0.9441117266030916 | 0.944111726603 | 9.2e-14 |
| 6.1 Ej. 3 | CTPL | 1.0048580689904953 | 1.004858068990 | 5.0e-13 |
| 6.2 Ej. 1 | ρ₆₀ | 832.0485161842337 | 832.048516184234 | 3.4e-13 |
| 6.2 Ej. 2 | ρ₆₀ | 663.4450628524019 | 663.445062852402 | 1.1e-13 |
| 6.2 Ej. 5 | ρ₆₀ | 787.5079225939165 | 787.507922593917 | 4.6e-13 |
| 6.2 Ej. 6 | ρ₆₀ | 770.3497942520598 | 770.349794252060 | 1.1e-13 |
| 6.2 Ej. 7 | ρ₆₀ | 863.4030986136481 | 863.403098613648 | 1.1e-13 |

> [!IMPORTANT]
> El trabajo de reunir los casos de referencia **ya está hecho**; solo falta convertirlos en `assert`. Es la mejora de mayor retorno de todo el informe: sin ella, ninguna de las correcciones propuestas puede aplicarse con seguridad.


<!-- res:T-01 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `6b68257`, `5b0e53a` | 493 pruebas en verde. |

Los ejemplos se convirtieron en pruebas `pytest` con `assert` y se ampliaron con **105 ejemplos resueltos** de la norma (incluidos los casos de error) y **253 valores** de tablas de muestra.

---

<a id="t-02"></a>
## T-02 · Módulos sin ninguna cobertura — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🟡 Medio | `tests/` | — |

| Módulo | Casos nominales | Casos borde / errores |
|---|:---:|:---:|
| `section_5_1` (conversiones) | ❌ | ❌ |
| `section_5_3` (ITS-90 → IPTS-68) | ❌ | ❌ |
| `section_5_4` (`api_round`) | ❌ | ❌ |
| `section_6_1` | ⚠️ 3 ejemplos sin assert | ❌ |
| `section_6_2` | ⚠️ 5 ejemplos sin assert | ❌ |
| `section_7_1`, `section_7_2` | ❌ | ❌ |
| `tables.py` / `Tables/` | ❌ | ❌ |
| `validators/inputs.py` | ❌ | ❌ |
| `constants/*` | ❌ | ❌ |

Varios de los bugs de este informe ([N-01](03_precision_numerica.md#n-01), [F-01](01_errores_funcionales.md#f-01), [F-02](01_errores_funcionales.md#f-02), [F-05](01_errores_funcionales.md#f-05), [E-01](04_estructura_empaquetado.md#e-01)) habrían sido detectados por una prueba sencilla.


<!-- res:T-02 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `7809937` | `pytest --cov=api_mpms`. |

Cobertura medida con `pytest-cov`: **99 %** (467 sentencias, 1 sin cubrir: rama defensiva de valores no `float` no finitos).

---

<a id="t-03"></a>
## T-03 · Sin configuración de pytest ni integración continua — ✅ 100 %

| Severidad | Ubicación | Verificado |
|---|---|:---:|
| 🔵 Bajo | [`pyproject.toml`](https://github.com/DeividO12/PyMPMS-11.1/blob/4f1216d/pyproject.toml) | — |

No hay sección `[tool.pytest.ini_options]`, ni configuración de cobertura, ni *workflow* de CI. Recomendación mínima:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
```

Y un *workflow* de GitHub Actions que ejecute `pytest` en **Linux** (lo que además detectaría [E-02](04_estructura_empaquetado.md#e-02)).


<!-- res:T-03 -->
### ✅ Resolución — 100 %

| Cierre | Commits | Verificación |
|:---:|---|---|
| **100 %** | `6b68257`, `fa840c5` | Ejecución local de ruff, mypy y pytest; compatibilidad con 3.9.13 comprobada. |

`[tool.pytest.ini_options]` y `[tool.ruff]` en `pyproject.toml`; workflow `.github/workflows/tests.yml` (Ubuntu, Python 3.9 y 3.12) con ruff, mypy y pytest.

---

<a id="propuesta-de-suite-de-pruebas"></a>
## Propuesta de suite de pruebas

### Pruebas de referencia (a partir de los ejemplos existentes)

```python
# tests/test_section_6_2.py
import pytest
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base

CASES = [
    # rho_o,        t_o,    p_o,   tipo, alpha,       rho_60_esperado
    (823.7,         80.3,   -5,    "A",  None,        832.048516184234),
    (722.60825312, -57.95,  113.5, "A",  None,        663.445062852402),
    (803.141,       25.3,   267,   "B",  None,        787.507922593917),
    (731.4795152,   139,    100,   "B",  None,        770.349794252060),
    (853.7,         84.5,   573,   "C",  0.00057634,  863.403098613648),
]

@pytest.mark.parametrize("rho_o,t_o,p_o,ct,alpha,expected", CASES)
def test_reference_examples(rho_o, t_o, p_o, ct, alpha, expected):
    rho_60, *_ = correct_observed_to_base(
        rho_o=rho_o, t_o=t_o, p_o=p_o, commodity_type=ct, alpha_60=alpha
    )
    assert rho_60 == pytest.approx(expected, abs=1e-9)
```

### Pruebas de casos borde (deben fallar hoy y pasar tras las correcciones)

```python
# tests/test_section_5_4.py
import pytest
from api_mpms.mpms_11_1.section_5_4 import api_round

@pytest.mark.parametrize("x,delta,expected", [
    (0.15, 0.1, 0.2), (0.25, 0.1, 0.2),
    (611.15, 0.1, 611.2),          # N-01
    (205.075, 0.05, 205.1),        # N-01
    (0.800055, 0.00001, 0.80006),  # N-01
    (0.75, 0.25, 0.75),            # N-02
    (12.5, 2.5, 12.5),             # N-02
])
def test_api_round_ties(x, delta, expected):
    assert api_round(x, delta) == expected

@pytest.mark.parametrize("x,delta", [(float("nan"), 0.1), (1.0, 0), (1.0, -0.1)])
def test_api_round_invalid(x, delta):
    with pytest.raises(MPMSValidationError):
        api_round(x, delta)
```

```python
# tests/test_validation.py
@pytest.mark.parametrize("rho", [0, -800, float("nan"), float("inf")])
def test_invalid_density_rejected(rho):                       # V-01, F-02
    with pytest.raises(MPMSValidationError):
        correct_base_to_alternate(rho, 60, 0, commodity_group="A")

def test_pressure_nan_rejected():                              # V-03
    with pytest.raises(MPMSValidationError):
        validate_pressure_psig(float("nan"))

def test_commodity_none_rejected():                            # F-06
    with pytest.raises(MPMSValidationError):
        correct_observed_to_base(rho_o=800, t_o=60, p_o=0, commodity_type=None)

def test_alpha_zero_not_ignored():                             # F-05
    ...
```

### Pruebas de propiedades (recomendado)

Con `hypothesis` se puede verificar la **reversibilidad** 6.1 ↔ 6.2 en todo el dominio:

```python
@given(rho_60=st.floats(620, 1150), t=st.floats(-58, 302), p=st.floats(0, 1500))
def test_roundtrip(rho_60, t, p):
    rho_o, *_ = correct_base_to_alternate(rho_60, t, p, commodity_group="A")
    back, *_ = correct_observed_to_base(rho_o=rho_o, t_o=t, p_o=p, commodity_type="A")
    assert back == pytest.approx(rho_60, abs=1e-5)
```

> [!NOTE]
> Esta propiedad se verificó con 5 000 muestras aleatorias para el tipo A: 0 fallos y error máximo de 1.13e-6 kg/m³. Hoy pasaría, por lo que sirve como red de seguridad para futuras refactorizaciones.

---

[⬅ Anterior: Estructura y empaquetado](04_estructura_empaquetado.md) · [Índice](README.md) · [Siguiente: Rendimiento ➡](06_rendimiento.md)
