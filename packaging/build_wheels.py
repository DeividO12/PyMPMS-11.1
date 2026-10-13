"""
Prepara y construye los wheels compilados (ofuscados) de pympms-11-1.

    python packaging/build_wheels.py --stage-only [--stage-dir DIR]
        Solo arma el staging (por defecto packaging/_stage/). Lo usa el
        workflow de release, que luego ejecuta cibuildwheel sobre esa carpeta.

    python packaging/build_wheels.py [--skip-tests]
        Build local para el intérprete actual: arma el staging en una carpeta
        temporal (fuera de OneDrive y con ruta corta), compila el wheel,
        verifica su contenido y corre las pruebas contra el wheel instalado en
        un entorno temporal. En Windows necesita Visual Studio Build Tools (se
        cargan con vcvars64.bat automáticamente).

El código fuente del repositorio no se modifica: todo ocurre en el staging
(packaging/_stage/ está ignorado en git). Ver packaging/README.md y
docs/decisiones (ADR-026 a ADR-033).
"""

import argparse
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGING = ROOT / "packaging"
DEFAULT_STAGE = PACKAGING / "_stage"
LOCAL_STAGE = Path(tempfile.gettempdir()) / "pympms_stage"
WHEELHOUSE = PACKAGING / "wheelhouse"

# Versiones fijadas (ADR-032): reproducibles y con soporte para Python 3.9.
BUILD_REQUIRES = ["setuptools==82.0.1", "Cython==3.3.0"]
PYTHON_BUILDS = "cp39-* cp310-* cp311-* cp312-* cp313-*"

IGNORE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", "*.pyd", "*.so", "*.c", "_version.py", "py.typed"
)


def get_version() -> str:
    """Versión del tag (setuptools-scm) o de la variable PYMPMS_VERSION."""
    if os.environ.get("PYMPMS_VERSION"):
        return os.environ["PYMPMS_VERSION"]
    from setuptools_scm import get_version as scm_version

    return scm_version(root=str(ROOT))


def _toml_list(values) -> str:
    return "[" + ", ".join(f'"{v}"' for v in values) + "]"


def stage_pyproject(version: str) -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf8"))["project"]
    authors = ", ".join(f'{{ name = "{a["name"]}" }}' for a in project["authors"])
    return f'''# Generado por packaging/build_wheels.py: no editar.
[build-system]
requires = {_toml_list(BUILD_REQUIRES)}
build-backend = "setuptools.build_meta"

[project]
name = "{project["name"]}"
version = "{version}"
description = "{project["description"]}"
readme = "README.md"
requires-python = "{project["requires-python"]}"
license = "LicenseRef-Proprietary"
license-files = ["LICENSE"]
authors = [{authors}]
classifiers = {_toml_list(project["classifiers"])}
dependencies = {_toml_list(project.get("dependencies", []))}

[tool.pytest.ini_options]
addopts = "-p no:cacheprovider --doctest-glob=*.md"
doctest_optionflags = ["ELLIPSIS", "NORMALIZE_WHITESPACE"]

[tool.cibuildwheel]
build = "{PYTHON_BUILDS}"
skip = "*-musllinux_*"
build-frontend = "build"
test-requires = ["pytest"]
# Se prueba el wheel instalado, nunca el código del staging.
test-command = [
    "python {{project}}/check_wheel.py installed",
    "pytest {{project}}/tests {{project}}/docs/api {{project}}/README.md",
]

[tool.cibuildwheel.linux]
archs = ["x86_64"]

[tool.cibuildwheel.windows]
archs = ["AMD64"]
'''


def _clear_readonly(func, path, _exc_info) -> None:
    """OneDrive marca carpetas como de solo lectura y copytree copia ese atributo."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _remove_tree(path: Path) -> None:
    """rmtree que quita el atributo de solo lectura y reintenta si un proceso retiene archivos."""
    for attempt in range(10):
        try:
            if sys.version_info >= (3, 12):
                shutil.rmtree(path, onexc=_clear_readonly)
            else:
                shutil.rmtree(path, onerror=_clear_readonly)
            return
        except FileNotFoundError:
            return
        except PermissionError:
            if attempt == 9:
                raise
            time.sleep(1)


def make_stage(version: str, stage: Path) -> None:
    _remove_tree(stage)
    stage.mkdir(parents=True)
    shutil.copytree(ROOT / "src" / "api_mpms", stage / "src" / "api_mpms", ignore=IGNORE)
    (stage / "src" / "api_mpms" / "_version.py").write_text(
        f'__version__ = version = "{version}"\n', encoding="utf8"
    )
    # Pruebas y documentación con doctest: se ejecutan contra el wheel instalado.
    shutil.copytree(ROOT / "tests", stage / "tests", ignore=IGNORE)
    shutil.copytree(ROOT / "docs" / "api", stage / "docs" / "api")
    for name in ("README.md", "LICENSE"):
        shutil.copy2(ROOT / name, stage / name)
    shutil.copy2(PACKAGING / "stage_setup.py", stage / "setup.py")
    shutil.copy2(PACKAGING / "check_wheel.py", stage / "check_wheel.py")
    (stage / "pyproject.toml").write_text(stage_pyproject(version), encoding="utf8")
    print(f"Staging listo para pympms-11-1 {version}: {stage}")


def _msvc_env() -> dict:
    """Entorno de Visual Studio (vcvars64) para compilar en Windows."""
    env = dict(os.environ)
    if shutil.which("cl"):
        return env
    vswhere = (Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
               / "Microsoft Visual Studio" / "Installer" / "vswhere.exe")
    path = subprocess.run(
        [str(vswhere), "-latest", "-products", "*", "-requires",
         "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    vcvars = Path(path) / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
    out = subprocess.run(f'"{vcvars}" >nul && set', shell=True, capture_output=True, text=True, check=True)
    env.update(line.split("=", 1) for line in out.stdout.splitlines() if "=" in line)
    env["DISTUTILS_USE_SDK"] = "1"
    env["MSSdk"] = "1"
    return env


def build_local(version: str, stage: Path, run_tests: bool) -> Path:
    WHEELHOUSE.mkdir(exist_ok=True)
    env = _msvc_env() if sys.platform == "win32" else dict(os.environ)
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(WHEELHOUSE), str(stage)],
        env=env, check=True,
    )
    tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    wheel = max(WHEELHOUSE.glob(f"pympms_11_1-{version}-{tag}-*.whl"), key=os.path.getmtime)
    subprocess.run([sys.executable, str(PACKAGING / "check_wheel.py"), "contents", str(wheel),
                    "--version", version], check=True)
    if run_tests:
        _test_wheel(wheel, stage)
    return wheel


def _test_wheel(wheel: Path, stage: Path) -> None:
    # Ruta corta: Windows limita las rutas a 260 caracteres.
    venv = Path(tempfile.mkdtemp(prefix="pymw"))
    try:
        subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(venv)], check=True)
        py = venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run([sys.executable, "-m", "pip", "--python", str(py), "install", "-q",
                        str(wheel), "pytest"], check=True)
        subprocess.run([str(py), str(stage / "check_wheel.py"), "installed"], check=True, cwd=venv)
        subprocess.run([str(py), "-m", "pytest", "-q", str(stage / "tests"), str(stage / "docs" / "api"),
                        str(stage / "README.md"), "--rootdir", str(stage)], check=True, cwd=venv)
    finally:
        _remove_tree(venv)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--stage-only", action="store_true", help="solo preparar el staging")
    parser.add_argument("--skip-tests", action="store_true", help="no probar el wheel local")
    parser.add_argument("--stage-dir", type=Path, default=None,
                        help="carpeta del staging (por defecto packaging/_stage con --stage-only; "
                             "una carpeta temporal en el build local)")
    args = parser.parse_args()

    stage = (args.stage_dir or (DEFAULT_STAGE if args.stage_only else LOCAL_STAGE)).resolve()
    version = get_version()
    make_stage(version, stage)
    if not args.stage_only:
        wheel = build_local(version, stage, run_tests=not args.skip_tests)
        print(f"Wheel listo: {wheel}")


if __name__ == "__main__":
    main()
