# Distribución compilada de PyMPMS-11.1

Cómo se construyen, verifican y publican las versiones **compiladas con Cython** (código no legible) de la librería. El código del repositorio es y sigue siendo Python puro; la compilación ocurre en una copia temporal (*staging*) y nunca se versiona nada generado.

Decisiones que respaldan este proceso: [ADR-025 a ADR-033](../docs/decisiones/05_versionado_y_distribucion.md).

## 📑 Contenido

1. [Resumen del flujo](#flujo)
2. [Archivos](#archivos)
3. [Configuración inicial (una sola vez)](#configuracion)
4. [Liberar una versión](#liberar)
5. [Instalar una versión publicada](#instalar)
6. [Build local](#local)
7. [Qué se verifica](#verificaciones)
8. [Problemas conocidos y recuperación](#problemas)

---

<a id="flujo"></a>
## 1. Resumen del flujo

```text
git tag -a vX.Y.Z  +  git push origin master vX.Y.Z          (repositorio personal)
        │
        ├─ mirror.yml ──► replica ramas y tags en sistemasSYZ/PyMPMS-11.1
        │
        └─ release.yml
             1. checks   : ruff + mypy + pytest
             2. wheels   : cibuildwheel en Windows y Linux, Python 3.9–3.13 (10 wheels)
                           cada wheel se instala y pasa las pruebas y los doctests
             3. publish  : en sistemasSYZ/PyMPMS-11.1
                           · GitHub Release vX.Y.Z con los 10 wheels
                           · rama dist/vX.Y.Z/ con los mismos wheels
                           · descarga de vuelta y comparación SHA-256
```

| Workflow | Se dispara con | Corre en |
|---|---|---|
| [`tests.yml`](../.github/workflows/tests.yml) | Cualquier push o PR | Solo el repositorio personal |
| [`mirror.yml`](../.github/workflows/mirror.yml) | Cualquier push o borrado de rama/tag | Solo el repositorio personal |
| [`release.yml`](../.github/workflows/release.yml) | Push de un tag `vX.Y.Z` (publica) o ejecución manual (solo compila) | Solo el repositorio personal |

---

<a id="archivos"></a>
## 2. Archivos

| Archivo | Función |
|---|---|
| `build_wheels.py` | Arma el staging (código, pruebas, docs con doctest, `setup.py`, `pyproject.toml` con la versión del tag). En modo local además compila, verifica y prueba el wheel del intérprete actual. |
| `stage_setup.py` | `setup.py` del staging: compila con Cython todo excepto los `__init__.py`, con `annotation_typing=False`, `-ffp-contract=off`, sin símbolos en Linux, y excluye del wheel los `.py` compilados y los `.c` |
| `check_wheel.py` | `contents`: ningún código fuente en el wheel y los 19 binarios presentes. `installed`: los módulos se cargan desde binarios. |
| `publish.py` | Publica en SYZ: Release, rama `dist` y comprobación SHA-256. Nunca reemplaza una versión ya publicada. |

Versiones fijadas ([ADR-032](../docs/decisiones/05_versionado_y_distribucion.md#adr-032)): Cython 3.3.0, setuptools 82.0.1 (la última compatible con Python 3.9), cibuildwheel 4.3.1. Se cambian solo de forma deliberada, verificando los 10 wheels.

---

<a id="configuracion"></a>
## 3. Configuración inicial (una sola vez)

Los workflows `mirror.yml` y `release.yml` corren en el repositorio personal y escriben en `sistemasSYZ/PyMPMS-11.1` con un token guardado como secreto **del repositorio personal**. En el repositorio de SYZ no se configura nada.

```text
DeividO12/PyMPMS-11.1 (Actions + secreto SYZ_RELEASE_TOKEN) ──escribe──► sistemasSYZ/PyMPMS-11.1
```

| Paso | Dónde | Enlace |
|---|---|---|
| Crear el token | Configuración de la **cuenta** `DeividO12` (no de un repositorio) | https://github.com/settings/tokens/new |
| Guardar el secreto | Repositorio **personal** `DeividO12/PyMPMS-11.1` | https://github.com/DeividO12/PyMPMS-11.1/settings/secrets/actions/new |

1. **Crear un token clásico** (*Tokens (classic)* › *Generate new token (classic)*):
   - *Note:* `PyMPMS-11.1 release → sistemasSYZ`.
   - *Scopes:* **`repo`** y **`workflow`**, nada más. `workflow` es obligatorio porque el espejo empuja commits que modifican `.github/workflows/`, y GitHub rechaza esos push sin ese alcance.
   - *Expiration:* la que permita la política de SYZ. **Anote la fecha**: al vencer, el espejo y las liberaciones fallan por autenticación hasta renovarlo (crear uno nuevo y reemplazar el secreto).
   - Si junto al token aparece **Configure SSO**, autorícelo para `sistemasSYZ`.
2. **Guardarlo como secreto** del repositorio personal con el nombre exacto `SYZ_RELEASE_TOKEN`.

> [!NOTE]
> **Por qué un token clásico y no uno de grano fino.** Verificado el 2026-10-13: la cuenta `DeividO12` es **colaborador externo** de `sistemasSYZ/PyMPMS-11.1` (permiso de escritura, no miembro de la organización), y GitHub no permite que un colaborador externo use un token de grano fino sobre repositorios privados de una organización. El token clásico con `repo` da acceso a todos los repositorios de la cuenta, por eso solo se guarda como secreto cifrado y con expiración. Si un administrador de `sistemasSYZ` hace a la cuenta miembro de la organización, conviene cambiarlo por uno de grano fino limitado a `PyMPMS-11.1` con *Contents: Read and write* y *Workflows: Read and write* (solo hay que reemplazar el secreto).

Configurado el 2026-10-13 (token clásico, secreto `SYZ_RELEASE_TOKEN` en `DeividO12/PyMPMS-11.1`).
3. **Probar el build sin publicar:** Actions › *release* › *Run workflow* (ejecución manual). Compila y prueba los 10 wheels y no publica nada.
4. **Retirar el push doble local** cuando `mirror.yml` funcione: deja de ser necesario ([ADR-005](../docs/decisiones/01_proceso_y_repositorio.md#adr-005)).

   ```bash
   git remote set-url --delete --push origin https://github.com/sistemasSYZ/PyMPMS-11.1.git
   ```

> [!WARNING]
> No use el token de la sesión de `gh` ni uno con acceso a toda la cuenta: el secreto solo necesita escribir en `sistemasSYZ/PyMPMS-11.1`.

---

<a id="liberar"></a>
## 4. Liberar una versión

```bash
git checkout master
git merge --no-ff dev_deivid                   # ADR-006
# actualizar CHANGELOG.md con la sección "## X.Y.Z — fecha" y hacer commit
git tag -a vX.Y.Z -m "vX.Y.Z — resumen"        # ADR-025: verificar antes que el tag no exista
git push origin master vX.Y.Z
```

Al terminar `release.yml` (unos 20-30 minutos), la versión está en:

- `https://github.com/sistemasSYZ/PyMPMS-11.1/releases/tag/vX.Y.Z`
- la rama `dist` de `sistemasSYZ/PyMPMS-11.1`, carpeta `vX.Y.Z/`

Las notas del Release salen de la sección `## X.Y.Z` del [CHANGELOG](../CHANGELOG.md).

Después de liberar, traiga `master` a la rama de trabajo para que contenga el commit etiquetado. Si no, `setuptools-scm` no ve el tag desde `dev_deivid` y las versiones de desarrollo salen como `0.1.devN` en lugar de `X.Y.(Z+1).devN`:

```bash
git checkout dev_deivid
git merge master            # avance rápido o merge sin conflictos: master solo agrega el commit de merge
git push origin dev_deivid
```

---

<a id="instalar"></a>
## 5. Instalar una versión publicada

El nombre del wheel indica la versión de Python (`cp39` … `cp313`) y la plataforma (`win_amd64` o `manylinux…x86_64`). Se necesita un token con **lectura** sobre `sistemasSYZ/PyMPMS-11.1`.

```bash
# Opción A — un solo comando (cualquier versión, desde la rama dist)
pip install "https://${GH_TOKEN}@raw.githubusercontent.com/sistemasSYZ/PyMPMS-11.1/dist/vX.Y.Z/pympms_11_1-X.Y.Z-cp312-cp312-win_amd64.whl"

# Opción B — con gh, desde el Release
gh release download vX.Y.Z --repo sistemasSYZ/PyMPMS-11.1 --pattern "*cp312*win_amd64.whl"
pip install ./pympms_11_1-X.Y.Z-cp312-cp312-win_amd64.whl
```

Para saber qué wheel le corresponde a un equipo:

```bash
python -c "import sys, sysconfig; print(f'cp{sys.version_info[0]}{sys.version_info[1]}', sysconfig.get_platform())"
```

---

<a id="local"></a>
## 6. Build local

Para probar la compilación antes de crear un tag. Compila **solo** el wheel del intérprete actual.

```bash
pip install -e ".[dev,release]"
python packaging/build_wheels.py              # staging en una carpeta temporal + wheel + pruebas
python packaging/build_wheels.py --skip-tests
```

- En Windows necesita **Visual Studio Build Tools** con el componente de C++; el script carga `vcvars64.bat` solo.
- El wheel queda en `packaging/wheelhouse/` (ignorado en git).
- La versión sale de `setuptools-scm`. Entre tags es de desarrollo (`1.0.1.devN+g…`); se puede forzar con `PYMPMS_VERSION=X.Y.Z`.

Resultado de referencia (2026-10-13, Windows, Python 3.12): wheel de 447 KB, los 19 módulos compilados, **508 pruebas pasan** contra el wheel instalado y 1 se omite (el generador de tablas, porque el wheel no lleva pandas).

Build de prueba en CI (2026-10-13, ejecución `38451574663`): los **10 wheels** (Python 3.9–3.13 × Windows/Linux) pasaron cada uno las 508 pruebas cargando los módulos desde binarios. Tamaños: Windows 406–440 KB, Linux 474–489 KB (sin símbolos), ~4.5 MB por versión. Duración: ~4.5 min.

---

<a id="verificaciones"></a>
## 7. Qué se verifica

| Verificación | Dónde | Detecta |
|---|---|---|
| Ningún `.py` (salvo `__init__.py`), `.c`, `.pyx`, `.pdb`, `.pyi` ni `py.typed` en el wheel | `check_wheel.py contents` (build local, `publish.py`) | Código fuente filtrado. Así se detectó que setuptools empaquetaba los `.c` generados por Cython. |
| Los 19 módulos presentes como binario, sin binarios inesperados | ídem | Un módulo nuevo sin compilar o una lista desactualizada |
| Los módulos se cargan desde binarios | `check_wheel.py installed` (cada wheel en cibuildwheel) | Un `.py` que tapa al binario |
| Pruebas, ejemplos de la norma y doctests de `docs/api` y del README | `pytest` contra el wheel instalado (cada wheel) | Diferencias de comportamiento del código compilado |
| 10 wheels, de la versión del tag | `publish.py` | Una plataforma o versión de Python faltante |
| Lo publicado es byte a byte lo verificado | `publish.py` (descarga desde la rama `dist`) | Publicación corrupta o incompleta |

---

<a id="problemas"></a>
## 8. Problemas conocidos y recuperación

| Situación | Causa | Qué hacer |
|---|---|---|
| `PermissionError: Acceso denegado` al borrar el staging | OneDrive marca carpetas como de solo lectura y `copytree` copia el atributo | Ya resuelto en `build_wheels.py` (quita el atributo y reintenta). El build local usa una carpeta temporal fuera de OneDrive. |
| `Unable to find a compatible Visual Studio installation` | setuptools no detecta Visual Studio por sí solo | `build_wheels.py` carga `vcvars64.bat`; verifique que esté instalado el componente *MSVC v143 C++ x64/x86 build tools* |
| El texto de un `TypeError` difiere entre CPython y el binario | Cython redacta distinto algunos mensajes nativos de Python | Los doctests comparan con `...`; el integrador debe decidir por el tipo de la excepción ([ADR-019](../docs/decisiones/03_api_publica.md#adr-019)) |
| `mirror.yml` falla con «Falta el secreto SYZ_RELEASE_TOKEN» | No se configuró el token | [Configuración inicial](#configuracion) |
| `mirror.yml` o `publish.py` fallan con `Repository not found` al hacer push a SYZ | Si el paso «Diagnóstico del token» muestra usuario, alcances y HTTP 200 correctos: `actions/checkout` dejó la cabecera del `GITHUB_TOKEN` del repo personal, que git envía a todo github.com y anula el token de SYZ (ocurrió el 2026-10-13) | `persist-credentials: false` en el checkout (ya aplicado). Si el diagnóstico muestra otro usuario, alcances sin `repo`/`workflow`, HTTP 404 o `x-github-sso`, el problema es el token: [Configuración inicial](#configuracion) |
| El token venció | Expiración del token clásico | Crear uno nuevo con los mismos alcances y reemplazar el secreto `SYZ_RELEASE_TOKEN` |
| `publish.py` falla porque el Release ya existe | La versión ya estaba publicada (no se reemplaza a propósito) | Publique una versión nueva (`vX.Y.Z+1`). Si el Release quedó a medias por un error, bórrelo a mano en SYZ y vuelva a ejecutar el job *publish* desde Actions. |
| `publish.py` falla porque `dist/vX.Y.Z` ya existe | Ídem | Ídem. Para retirar una carpeta publicada por error, haga un commit que la borre en la rama `dist` de SYZ. |
| Una versión nueva de Python (por ejemplo 3.14) | Los binarios dependen de la versión de Python | Agregar `cp314-*` en `PYTHON_BUILDS` (`build_wheels.py`), actualizar el número esperado en `publish.py` y registrar la decisión |
