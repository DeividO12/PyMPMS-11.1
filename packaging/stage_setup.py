"""
setup.py del staging de compilación (lo copia build_wheels.py a packaging/_stage/setup.py).

Compila con Cython todos los módulos de api_mpms excepto los __init__.py y
excluye del wheel el .py de cada módulo compilado. Ver docs/decisiones ADR-026.
"""

import sys
from pathlib import Path

from Cython.Build import cythonize
from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

SRC = Path("src")
SOURCES = sorted(p for p in (SRC / "api_mpms").rglob("*.py") if p.name != "__init__.py")
# Nombre de módulo de cada fuente compilada: src/api_mpms/x/y.py -> api_mpms.x.y
COMPILED = {".".join(p.relative_to(SRC).with_suffix("").parts) for p in SOURCES}

COMPILER_DIRECTIVES = {
    "language_level": 3,
    # Sin esto Cython convierte las anotaciones en comprobaciones de tipo en C y
    # un dato inválido lanza TypeError en lugar de MPMSValidationError.
    "annotation_typing": False,
}

if sys.platform == "win32":
    # MSVC: /fp:precise (por defecto) no contrae operaciones; no emite símbolos en el .pyd.
    COMPILE_ARGS, LINK_ARGS = [], []
else:
    # -ffp-contract=off: sin FMA, resultados idénticos a CPython bit a bit.
    # -g0 y -s: sin información de depuración ni tabla de símbolos en el .so.
    COMPILE_ARGS, LINK_ARGS = ["-g0", "-ffp-contract=off"], ["-s"]


class BuildPyWithoutCompiledSources(build_py):
    """No copia al wheel el .py de los módulos que se compilan."""

    def find_package_modules(self, package, package_dir):
        modules = super().find_package_modules(package, package_dir)
        return [m for m in modules if f"{m[0]}.{m[1]}" not in COMPILED]


extensions = cythonize(
    [str(p) for p in SOURCES],
    compiler_directives=COMPILER_DIRECTIVES,
    quiet=True,
)
for ext in extensions:
    ext.extra_compile_args += COMPILE_ARGS
    ext.extra_link_args += LINK_ARGS

setup(
    package_dir={"": "src"},
    packages=find_packages("src"),
    ext_modules=extensions,
    cmdclass={"build_py": BuildPyWithoutCompiledSources},
    # Los .c que genera Cython son el código fuente traducido (legible): nunca al wheel.
    include_package_data=False,
    exclude_package_data={"": ["*.c", "*.pyx", "*.pxd", "*.pyi", "py.typed"]},
)
