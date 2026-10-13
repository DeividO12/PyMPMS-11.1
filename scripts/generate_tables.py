"""
Genera las tablas de corrección de API MPMS 11.1 §11.1.8 en formato CSV.

Formato (como las tablas de muestra de la norma): temperatura en filas y
densidad/API/densidad relativa/alpha en columnas. Las celdas que la norma no
permite calcular (fuera de rango o sin convergencia) quedan vacías.

Uso:
    python scripts/generate_tables.py 5A 6B 54C --out-dir tablas --workers 8
    python scripts/generate_tables.py --list

Requiere los extras opcionales: pip install -e ".[tables]"
"""

import argparse
import logging
import math
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence

import pandas as pd

from api_mpms.exceptions.convergence import MPMSConvergenceError
from api_mpms.exceptions.validation import MPMSValidationError
from api_mpms.mpms_11_1 import tables

logger = logging.getLogger("generate_tables")

_CALC_ERRORS = (MPMSConvergenceError, MPMSValidationError)

_HYDROMETER_NOTE = (
    "If hydrometer used to determine density, apply glass correction before entering table"
)


@dataclass(frozen=True)
class Grid:
    """Rango inclusivo start..stop con paso fijo, generado con enteros (sin acumular error)."""

    start: float
    stop: float
    step: float
    decimals: int

    def values(self) -> List[float]:
        n = round((self.stop - self.start) / self.step)
        return [round(self.start + k * self.step, self.decimals) for k in range(n + 1)]


TEMP_F = Grid(-58.0, 302.0, 0.1, 1)
TEMP_C = Grid(-50.0, 150.0, 0.05, 2)


@dataclass(frozen=True)
class TableSpec:
    name: str
    function: str           # nombre de la función en api_mpms.mpms_11_1.tables
    column_param: str       # parámetro que recorre las columnas
    columns: Grid
    temp_param: str
    temps: Grid
    fixed: Dict[str, str] = field(default_factory=dict)
    observed_input: bool = False  # tablas impares: llevan la nota del hidrómetro


def _specs() -> Dict[str, TableSpec]:
    s: List[TableSpec] = []
    for ct, lo in (("A", -13.4), ("B", -14.2)):
        s.append(TableSpec(f"5{ct}", "table_5x", "api_obs", Grid(lo, 168.9, 0.1, 1),
                           "t_f_obs", TEMP_F, {"commodity_type": ct}, True))
    s.append(TableSpec("5D", "table_5x", "api_obs", Grid(-14.1, 66.3, 0.1, 1),
                       "t_f_obs", TEMP_F, {"commodity_type": "D"}, True))
    for ct, hi in (("A", 100.0), ("B", 100.0), ("D", 45.0)):
        s.append(TableSpec(f"6{ct}", "table_6x", "api_base", Grid(-10.0, hi, 0.1, 1),
                           "t_f_obs", TEMP_F, {"commodity_type": ct}))
    for ct, lo, hi in (("A", 0.4710, 1.1989), ("B", 0.4709, 1.2065), ("D", 0.7151, 1.2053)):
        s.append(TableSpec(f"23{ct}", "table_23x", "rel_obs", Grid(lo, hi, 0.0001, 4),
                           "t_f_obs", TEMP_F, {"commodity_type": ct}, True))
    for ct, lo in (("A", 0.6113), ("B", 0.6113), ("D", 0.8017)):
        s.append(TableSpec(f"24{ct}", "table_24x", "rel_base", Grid(lo, 1.1646, 0.0001, 4),
                           "t_f_obs", TEMP_F, {"commodity_type": ct}))
    for prefix, func in (("53", "table_53x"), ("59", "table_59x")):
        for ct, lo, hi in (("A", 470.6, 1197.7), ("B", 470.5, 1205.4), ("D", 714.5, 1204.1)):
            s.append(TableSpec(f"{prefix}{ct}", func, "den_obs", Grid(lo, hi, 0.1, 1),
                               "t_c_obs", TEMP_C, {"commodity_type": ct}, True))
    for ct, lo, hi in (("A", 611.2, 1163.7), ("B", 611.2, 1163.8), ("D", 801.3, 1163.8)):
        s.append(TableSpec(f"54{ct}", "table_54x", "den_base", Grid(lo, hi, 0.1, 1),
                           "t_c_obs", TEMP_C, {"commodity_type": ct}))
    for ct, lo, hi in (("A", 606.2, 1161.1), ("B", 606.2, 1160.6), ("D", 798.2, 1160.7)):
        s.append(TableSpec(f"60{ct}", "table_60x", "den_base", Grid(lo, hi, 0.1, 1),
                           "t_c_obs", TEMP_C, {"commodity_type": ct}))
    alpha_f = Grid(230.0e-6, 930.0e-6, 0.1e-6, 7)
    alpha_c = Grid(414.0e-6, 1674.0e-6, 0.2e-6, 7)
    s.append(TableSpec("6C", "table_6c_24c", "alpha_obs", alpha_f, "t_f_obs", TEMP_F))
    s.append(TableSpec("24C", "table_6c_24c", "alpha_obs", alpha_f, "t_f_obs", TEMP_F))
    s.append(TableSpec("54C", "table_54c", "alpha_obs", alpha_c, "t_c_obs", TEMP_C))
    s.append(TableSpec("60C", "table_60c", "alpha_obs", alpha_c, "t_c_obs", TEMP_C))
    return {spec.name: spec for spec in s}


SPECS = _specs()


def _compute_column(spec: TableSpec, column_value: float, temps: Sequence[float]) -> List[float]:
    func = getattr(tables, spec.function)
    out = []
    for t in temps:
        try:
            out.append(func(**{spec.column_param: column_value, spec.temp_param: t}, **spec.fixed))
        except _CALC_ERRORS:
            out.append(math.nan)
    return out


def generate_table(spec: TableSpec, out_dir: Path, workers: int = 1) -> Path:
    """Calcula la tabla completa y la escribe en ``out_dir/Tabla_<nombre>.csv``."""
    columns = spec.columns.values()
    temps = spec.temps.values()
    logger.info("Tabla %s: %d columnas × %d temperaturas", spec.name, len(columns), len(temps))

    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            data = list(pool.map(_compute_column, [spec] * len(columns), columns,
                                 [temps] * len(columns), chunksize=16))
    else:
        data = [_compute_column(spec, c, temps) for c in columns]

    df = pd.DataFrame(dict(zip(columns, data)), index=pd.Index(temps, name=spec.temp_param))
    df.columns.name = spec.column_param

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"Tabla_{spec.name}.csv"
    with path.open("w", encoding="utf8", newline="") as fh:
        if spec.observed_input:
            fh.write(f"# {_HYDROMETER_NOTE}\n")
        df.to_csv(fh, na_rep="")
    logger.info("Tabla %s escrita en %s", spec.name, path)
    return path


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("tables", nargs="*", help="Tablas a generar (p. ej. 5A 6B 54C)")
    parser.add_argument("--out-dir", type=Path, default=Path("tablas"))
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--list", action="store_true", help="Lista las tablas disponibles")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    if args.list or not args.tables:
        for spec in SPECS.values():
            n_cols, n_temps = len(spec.columns.values()), len(spec.temps.values())
            print(f"{spec.name:>4}  {spec.function}  {n_cols} x {n_temps}")
        return
    unknown = [t for t in args.tables if t.upper() not in SPECS]
    if unknown:
        parser.error(f"Tablas desconocidas: {', '.join(unknown)}")
    for name in args.tables:
        generate_table(SPECS[name.upper()], args.out_dir, args.workers)


if __name__ == "__main__":
    main()
