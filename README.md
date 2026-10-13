# PyMPMS-11.1

Implementación en Python de **API MPMS Capítulo 11.1 (2004)**: factores de corrección de volumen por temperatura y presión (CTL, CPL, CTPL) para crudos, productos refinados, lubricantes y aplicaciones especiales.

La librería reproduce los ejemplos resueltos de la norma (11.1.5 a 11.1.7) y los valores de sus tablas de muestra (11.1.8). Ambos forman parte de la suite de pruebas automáticas.

## 📑 Contenido

- [Características](#caracteristicas)
- [Requisitos e instalación](#instalacion)
- [Ejemplo rápido](#ejemplo)
- [Documentación](#documentacion)
- [Alcance](#alcance)
- [Desarrollo](#desarrollo)
- [Aviso y licencia](#licencia)

---

<a id="caracteristicas"></a>
## Características

- Corrección de condiciones observadas a base y de base a condiciones alternas, en el sistema **°F/psig (60 °F)** y en el **métrico (15 °C / 20 °C, kPa o bar)**.
- Tipos de producto **A** (crudos), **B** (productos refinados), **C** (aplicaciones especiales con α60) y **D** (lubricantes).
- Valores de las **28 tablas de temperatura** de 11.1.8 (5, 6, 23, 24, 53, 54, 59, 60 A/B/D y 6C, 24C, 54C, 60C) y un generador de tablas completas en CSV.
- Conversión de unidades (°API, densidad relativa, °C, kPa, bar, α, Fp) y redondeo según 11.1.5.4.
- Validación de límites según la norma: nunca extrapola. Excepciones específicas para datos fuera de rango, datos inválidos y falta de convergencia.
- Sin dependencias externas.

---

<a id="instalacion"></a>
## Requisitos e instalación

| Requisito | Detalle |
|---|---|
| Python | 3.9 a 3.13 |
| Plataforma | Windows x64 o Linux x64 (wheels compilados) |
| Dependencias | Ninguna |

La librería es de uso interno y no está publicada en PyPI.

Las versiones se publican **compiladas** (wheels, sin código fuente) en el repositorio de SYZ, en dos lugares con los mismos archivos: los [Releases](https://github.com/sistemasSYZ/PyMPMS-11.1/releases) y la rama [`dist`](https://github.com/sistemasSYZ/PyMPMS-11.1/tree/dist) (una carpeta por versión). Se instala el wheel que corresponde a la versión de Python y a la plataforma del equipo:

| Plataforma | Python | Archivo |
|---|---|---|
| Windows x64 | 3.9 – 3.13 | `pympms_11_1-<versión>-cpXY-cpXY-win_amd64.whl` |
| Linux x64 (glibc ≥ 2.17) | 3.9 – 3.13 | `pympms_11_1-<versión>-cpXY-cpXY-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl` |

`cpXY` es la versión de Python (`cp39` … `cp313`). Para averiguarla en el equipo de destino:

```bash
python -c "import sys, sysconfig; print(f'cp{sys.version_info[0]}{sys.version_info[1]}', sysconfig.get_platform())"
```

**Opción A — un solo comando**, desde la rama `dist` (ejemplo: v1.1.0, Python 3.12, Windows):

```bash
pip install "https://${GH_TOKEN}@raw.githubusercontent.com/sistemasSYZ/PyMPMS-11.1/dist/v1.1.0/pympms_11_1-1.1.0-cp312-cp312-win_amd64.whl"
```

**Opción B — con [`gh`](https://cli.github.com/)**, desde el Release:

```bash
gh release download v1.1.0 --repo sistemasSYZ/PyMPMS-11.1 --pattern "*cp312*win_amd64.whl"
pip install ./pympms_11_1-1.1.0-cp312-cp312-win_amd64.whl
```

En un `requirements.txt` (pip expande `${GH_TOKEN}` desde el entorno):

```text
pympms-11-1 @ https://${GH_TOKEN}@raw.githubusercontent.com/sistemasSYZ/PyMPMS-11.1/dist/v1.1.0/pympms_11_1-1.1.0-cp312-cp312-win_amd64.whl
```

> [!NOTE]
> El repositorio es privado: `GH_TOKEN` debe ser un token con **lectura** sobre `sistemasSYZ/PyMPMS-11.1`. Fije siempre la versión en la URL. La instalación desde el código fuente es solo para desarrollo ([README › Desarrollo](https://github.com/sistemasSYZ/PyMPMS-11.1#desarrollo)).

La distribución se llama `pympms-11-1`; el paquete se importa como `api_mpms`.

---

<a id="ejemplo"></a>
## Ejemplo rápido

Crudo con densidad observada de 823.7 kg/m³ a 80.3 °F y −5 psig, corregido a 60 °F (norma 11.1.6.2, ejemplo 1):

```python
>>> from api_mpms import correct_observed_to_base
>>> res = correct_observed_to_base(rho_o=823.7, t_o=80.3, p_o=-5, commodity_type="A")
>>> res.ctpl_rounded            # factor de corrección de volumen
0.98997
>>> round(res.rho_60, 6)        # densidad a 60 °F, kg/m³
832.048516

```

Mismo cálculo en el sistema métrico, con presión en kPa (norma 11.1.7.2, ejemplo 1):

```python
>>> from api_mpms import correct_metric_observed_to_base
>>> res = correct_metric_observed_to_base(
...     rho_o=721.1, t_o_c=82.35, p_o=10005, pressure_unit="kPa", t_base_c=15, commodity_type="B",
... )
>>> res.ctpl_rounded, round(res.rho_base, 6)
(0.93547, 770.84278)

```

---

<a id="documentacion"></a>
## Documentación

| Documento | Para quién |
|---|---|
| 📘 [**Documentación API**](docs/api/README.md) | **Integradores**: funciones, parámetros, resultados, errores, límites y guías por caso de uso, con ejemplos de la norma |
| [Guías por caso de uso](docs/api/02_guias.md) | Recetas por producto y sistema de unidades |
| [Errores](docs/api/08_errores.md) | Excepciones y cómo manejarlas |
| [CHANGELOG](CHANGELOG.md) | Cambios entre versiones (incluidos los incompatibles) |
| [Registro de decisiones](docs/decisiones/README.md) | Mantenedores: por qué el proyecto es como es (norma, API, versionado, distribución) |
| [Informe de auditoría 2026-10-09](docs/informe_2026-10-09_1420/README.md) | Mantenedores: auditoría de código y verificación contra la norma |

---

<a id="alcance"></a>
## Alcance

| Sección de la norma | Contenido | En la librería |
|---|---|---|
| 11.1.5.1 | Conversión de unidades | `api_mpms.conversions` |
| 11.1.5.3 | ITS-90 → IPTS-68 | Interno (y `conversions.its90_to_ipts68`) |
| 11.1.5.4 | Redondeo | `conversions.api_round` |
| 11.1.6.1 · 11.1.6.2 · 11.1.6.3 | Correcciones con base 60 °F | `correct_base_to_alternate`, `correct_observed_to_base`, `correct_observed_to_alternate` |
| 11.1.7.1 · 11.1.7.2 | Correcciones con base 15 °C / 20 °C | `correct_metric_base_to_alternate`, `correct_metric_observed_to_base` |
| 11.1.8 | Tablas | `api_mpms.tables` y `scripts/generate_tables.py` |

**No implementado:** 11.1.5.2 (α60 a partir de mediciones) y las tablas de compresibilidad 11.2.1 / 11.2.1M.

---

<a id="desarrollo"></a>
## Desarrollo

### Repositorios y versiones

| Repositorio | Uso |
|---|---|
| [`DeividO12/PyMPMS-11.1`](https://github.com/DeividO12/PyMPMS-11.1) | Repositorio de trabajo (`origin`) |
| [`sistemasSYZ/PyMPMS-11.1`](https://github.com/sistemasSYZ/PyMPMS-11.1) | Espejo de la organización: **desde aquí se instala** |

Cada `git push origin` publica en los dos repositorios. Para configurarlo en un clon nuevo:

```bash
git remote set-url --add --push origin https://github.com/DeividO12/PyMPMS-11.1.git
git remote set-url --add --push origin https://github.com/sistemasSYZ/PyMPMS-11.1.git
git remote -v        # deben aparecer dos líneas (push) para origin
```

La versión se deriva del tag de git (setuptools-scm). Para publicar una versión:

```bash
git tag -a v1.1.0 -m "v1.1.0 — resumen"
git push origin master v1.1.0      # llega a ambos repositorios
```

### Instalar desde el código fuente (solo desarrollo)

```bash
pip install -e ".[dev]"            # desde una copia del repositorio: pytest, pytest-cov, ruff, mypy
pip install -e ".[dev,tables]"     # + generador de tablas (numpy, pandas)
pip install "pympms-11-1 @ git+https://github.com/sistemasSYZ/PyMPMS-11.1.git@v1.1.0"   # código fuente de un tag
```

> [!WARNING]
> Estas formas instalan el **código fuente**. En los equipos de destino se instalan los wheels compilados ([Requisitos e instalación](#instalacion)), según [ADR-033](docs/decisiones/05_versionado_y_distribucion.md#adr-033).

### Versiones compiladas

Las versiones que se instalan en los equipos se publican compiladas con Cython (wheels para Python 3.9–3.13, Windows y Linux) mediante GitHub Actions al subir un tag. Proceso, configuración y recuperación: [`packaging/README.md`](packaging/README.md).

### Pruebas y calidad

```bash
pytest                              # pruebas, ejemplos de la norma y ejemplos de la documentación
pytest --cov=api_mpms               # con cobertura
ruff check src tests scripts
mypy src
```

Los bloques `>>>` de este README y de [`docs/api`](docs/api/README.md) se ejecutan como pruebas, así que la documentación no puede quedar desactualizada respecto al código.

```text
src/api_mpms/
├── __init__.py          # API pública: correcciones, resultados, excepciones
├── conversions.py       # API pública: conversiones y redondeo
├── tables.py            # API pública: valores de tabla
├── results.py           # tipos de resultado
├── constants/ exceptions/ validators/ mpms_11_1/   # implementación interna
scripts/generate_tables.py
tests/                   # pruebas y datos de la norma
docs/api/                # documentación para integradores
```

---

<a id="licencia"></a>
## Aviso y licencia

Esta librería es una implementación independiente de API MPMS 11.1. **No está afiliada ni avalada por el American Petroleum Institute (API).** El usuario es responsable de validar los resultados frente a la norma oficial y los requisitos regulatorios antes de usarlos en operación.

Software propietario — © 2026 SYZ Colombia SAS. Ver [LICENSE](LICENSE).
