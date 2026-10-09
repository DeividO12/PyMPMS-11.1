"""Valores impresos en las tablas de muestra de API MPMS 11.1 §11.1.8 (págs. PDF 142-192)."""

import json
from pathlib import Path

import pytest

from api_mpms.exceptions.validation import MPMSValidationError
from api_mpms.mpms_11_1 import tables

SAMPLES = json.loads(
    (Path(__file__).parent / "data" / "norm_table_samples.json").read_text(encoding="utf8")
)


@pytest.mark.parametrize("case", SAMPLES, ids=[c["id"] for c in SAMPLES])
def test_standard_sample_tables(case):
    func = getattr(tables, case["function"])
    assert func(**case["kwargs"]) == pytest.approx(case["expected"], abs=1e-12)


@pytest.mark.parametrize("kwargs", [
    {"alpha_obs": 229.9e-6, "t_f_obs": 100},
    {"alpha_obs": 930.1e-6, "t_f_obs": 100},
])
def test_table_6c_alpha_out_of_range(kwargs):
    with pytest.raises(MPMSValidationError):
        tables.table_6c_24c(**kwargs)


@pytest.mark.parametrize("func", [tables.table_54c, tables.table_60c])
@pytest.mark.parametrize("alpha_c", [413.8e-6, 1674.2e-6])
def test_metric_c_alpha_out_of_range(func, alpha_c):
    with pytest.raises(MPMSValidationError):
        func(alpha_obs=alpha_c, t_c_obs=40)


@pytest.mark.parametrize("func", [tables.table_54c, tables.table_60c])
@pytest.mark.parametrize("alpha_c", [414.0e-6, 1674.0e-6])
def test_metric_c_alpha_range_edges(func, alpha_c):
    assert 0.5 < func(alpha_obs=alpha_c, t_c_obs=40) < 1.5


@pytest.mark.parametrize("kwargs", [
    {"api_base": 100.5, "t_f_obs": 100, "commodity_type": "A"},
    {"api_base": -10.5, "t_f_obs": 100, "commodity_type": "B"},
    {"api_base": 46.0, "t_f_obs": 100, "commodity_type": "D"},
])
def test_table_6x_rejects_base_density_out_of_range(kwargs):
    """NORM-T11: 11.1.6.1 paso 1 exige error fuera de los límites de densidad base."""
    with pytest.raises(MPMSValidationError):
        tables.table_6x(**kwargs)


@pytest.mark.parametrize("api,ct", [(-10.0, "A"), (100.0, "B"), (45.0, "D")])
def test_table_6x_range_edges(api, ct):
    assert 0.5 < tables.table_6x(api_base=api, t_f_obs=100, commodity_type=ct) < 1.5
