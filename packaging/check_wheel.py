"""
Verificaciones de los wheels compilados (ver packaging/README.md).

    python check_wheel.py contents WHEEL... [--version X.Y.Z] [--expect N]
        Contenido de cada wheel: ningún código fuente (.py salvo __init__.py,
        .c, .pyx, .pdb, .pyi) y un binario por cada módulo compilable.

    python check_wheel.py installed
        Con el wheel ya instalado: los módulos se cargan desde binarios, no desde .py.
"""

import argparse
import sys
import zipfile
from pathlib import PurePosixPath

FORBIDDEN_SUFFIXES = {".c", ".pyx", ".pxd", ".pdb", ".pyi"}
FORBIDDEN_NAMES = {"py.typed"}
BINARY_SUFFIXES = (".pyd", ".so")

# Módulos que deben llegar compilados (todo api_mpms excepto los __init__.py).
REQUIRED_COMPILED = [
    "api_mpms/_version",
    "api_mpms/conversions",
    "api_mpms/results",
    "api_mpms/tables",
    "api_mpms/constants/commodity_groups",
    "api_mpms/constants/commodity_types",
    "api_mpms/constants/physical",
    "api_mpms/exceptions/convergence",
    "api_mpms/exceptions/validation",
    "api_mpms/mpms_11_1/section_5_1",
    "api_mpms/mpms_11_1/section_5_3",
    "api_mpms/mpms_11_1/section_5_4",
    "api_mpms/mpms_11_1/section_6_1",
    "api_mpms/mpms_11_1/section_6_2",
    "api_mpms/mpms_11_1/section_6_3",
    "api_mpms/mpms_11_1/section_7_1",
    "api_mpms/mpms_11_1/section_7_2",
    "api_mpms/mpms_11_1/tables",
    "api_mpms/validators/inputs",
]


def check_contents(wheel: str, version: str = "") -> list:
    errors = []
    name = PurePosixPath(wheel).name
    if version and f"-{version}-" not in name:
        errors.append(f"{name}: la versión del archivo no es {version}")
    with zipfile.ZipFile(wheel) as zf:
        files = [PurePosixPath(n) for n in zf.namelist() if not n.endswith("/")]
    package_files = [f for f in files if f.parts[0] == "api_mpms"]
    for f in package_files:
        if f.suffix == ".py" and f.name != "__init__.py":
            errors.append(f"{name}: contiene código fuente {f}")
        if f.suffix in FORBIDDEN_SUFFIXES or f.name in FORBIDDEN_NAMES:
            errors.append(f"{name}: contiene {f}")
    binaries = {str(f).split(".")[0] for f in package_files if f.name.endswith(BINARY_SUFFIXES)}
    for module in REQUIRED_COMPILED:
        if module not in binaries:
            errors.append(f"{name}: falta el binario de {module}")
    extra = binaries - set(REQUIRED_COMPILED)
    if extra:
        errors.append(f"{name}: binarios no esperados (actualizar REQUIRED_COMPILED): {sorted(extra)}")
    return errors


def check_installed() -> list:
    import importlib

    errors = []
    for module in REQUIRED_COMPILED:
        mod = importlib.import_module(module.replace("/", "."))
        if not mod.__file__.endswith(BINARY_SUFFIXES):
            errors.append(f"{module} se cargó desde {mod.__file__}, no desde un binario")
    import api_mpms

    print(f"api_mpms {api_mpms.__version__} cargado desde binarios: {api_mpms.__file__}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("contents")
    c.add_argument("wheels", nargs="+")
    c.add_argument("--version", default="")
    c.add_argument("--expect", type=int, default=0, help="número exacto de wheels esperado")
    sub.add_parser("installed")
    args = parser.parse_args()

    if args.cmd == "installed":
        errors = check_installed()
    else:
        errors = []
        if args.expect and len(args.wheels) != args.expect:
            errors.append(f"se esperaban {args.expect} wheels y hay {len(args.wheels)}")
        for wheel in args.wheels:
            errors += check_contents(wheel, args.version)
        if not errors:
            print(f"{len(args.wheels)} wheel(s) verificados: sin código fuente y con los "
                  f"{len(REQUIRED_COMPILED)} módulos compilados")

    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
