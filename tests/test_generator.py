"""Generador de tablas (scripts/generate_tables.py)."""

import importlib.util
from dataclasses import replace
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")

_spec = importlib.util.spec_from_file_location(
    "generate_tables", Path(__file__).parents[1] / "scripts" / "generate_tables.py"
)
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)


@pytest.mark.parametrize("name,n_cols,n_temps,first,last", [
    ("5A", 1824, 3601, -13.4, 168.9),
    ("6D", 551, 3601, -10.0, 45.0),
    ("23A", 7280, 3601, 0.4710, 1.1989),   # NORM-T08: sin la fila extra 1.1990
    ("54B", 5527, 4001, 611.2, 1163.8),
    ("6C", 7001, 3601, 230.0e-6, 930.0e-6),
    ("60C", 6301, 4001, 414.0e-6, 1674.0e-6),
])
def test_grids(name, n_cols, n_temps, first, last):
    spec = gen.SPECS[name]
    cols, temps = spec.columns.values(), spec.temps.values()
    assert (len(cols), len(temps)) == (n_cols, n_temps)
    assert cols[0] == pytest.approx(first, abs=1e-12) and cols[-1] == pytest.approx(last, abs=1e-12)
    assert len(set(cols)) == len(cols)


def test_generate_table_23a_sample(tmp_path):
    """F-01 / NORM-T08: 0.8270 a 90 °F → 0.8393 (pág. 153); las celdas no calculables quedan vacías."""
    spec = replace(
        gen.SPECS["23A"],
        columns=gen.Grid(0.8270, 0.8271, 0.0001, 4),
        temps=gen.Grid(89.9, 90.0, 0.1, 1),
    )
    path = gen.generate_table(spec, tmp_path)
    df = pd.read_csv(path, comment="#", index_col=0)
    assert df.loc[90.0, "0.827"] == pytest.approx(0.8393)

    out_of_range = replace(spec, columns=gen.Grid(1.3, 1.3, 0.0001, 4))
    df = pd.read_csv(gen.generate_table(out_of_range, tmp_path), comment="#", index_col=0)
    assert df.isna().all().all()
