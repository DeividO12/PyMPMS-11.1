"""Funciones auxiliares, rutas de error poco frecuentes y CTL desde densidad observada."""

import pytest

from api_mpms.constants.commodity_groups import COMMODITY_GROUPS
from api_mpms.exceptions.convergence import MPMSConvergenceError
from api_mpms.exceptions.validation import MPMSRangeError, MPMSValidationError
from api_mpms.mpms_11_1 import section_6_2, tables
from api_mpms.mpms_11_1.section_5_1 import (
    alpha_c_to_alpha_f,
    alpha_f_to_alpha_c,
    api_to_rho,
    fp_from_psi,
    pressure_to_psig,
)
from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_1 import _correct_core
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.mpms_11_1.section_7_2 import correct_metric_observed_to_base
from api_mpms.validators.inputs import validate_density


def test_its90_celsius_input_returns_celsius():
    t_f = its90_to_ipts68(t_f_90=212.0)
    t_c = its90_to_ipts68(t_c_90=100.0)
    assert t_c == pytest.approx((t_f - 32.0) / 1.8, abs=1e-12)


def test_alpha_conversions_roundtrip():
    assert alpha_f_to_alpha_c(alpha_c_to_alpha_f(900e-6)) == pytest.approx(900e-6, rel=1e-15)


def test_pressure_and_fp_conversions():
    assert pressure_to_psig(6.894757, "kPa") == pytest.approx(1.0)
    assert pressure_to_psig(0.06894757, " BAR ") == pytest.approx(1.0)
    assert fp_from_psi(6.894757, "kPa") == pytest.approx(1.0)


def test_api_round_rejects_non_numeric_delta():
    with pytest.raises(MPMSValidationError):
        api_round(1.0, "0.1")


def test_density_accepts_numeric_types():
    assert validate_density(850) == 850.0


def test_cpl_denominator_guard():
    with pytest.raises(MPMSRangeError):
        _correct_core(850.0, 60.0, 1.0e7, None, COMMODITY_GROUPS[1])


def test_non_convergence_keeps_last_result(monkeypatch):
    monkeypatch.setattr(section_6_2, "_MAX_ITER", 1)
    with pytest.raises(MPMSConvergenceError) as exc:
        correct_observed_to_base(rho_o=850.0, t_o=150.0, p_o=500.0, commodity_type="A")
    last = exc.value.last_result
    assert last.iterations == 0 and last.rho_60 == 850.0


@pytest.mark.parametrize("api_obs,t,ct", [(30.0, 100.0, "A"), (45.0, 20.0, "B"), (25.0, 200.0, "D")])
def test_ctl_from_observed_api_is_direct_procedure(api_obs, t, ct):
    """NORM-T10: el CTL sale directamente de 11.1.6.2, sin redondear la densidad base."""
    expected = correct_observed_to_base(rho_o=api_to_rho(api_obs), t_o=t, p_o=0, commodity_type=ct)
    assert tables.ctl_from_observed_api(api_obs=api_obs, t_f_obs=t, commodity_type=ct) == expected.ctpl_rounded


def test_ctl_from_observed_relative_density():
    expected = correct_observed_to_base(rho_o=0.8270 * 999.016, t_o=90.0, p_o=0, commodity_type="A")
    got = tables.ctl_from_observed_relative_density(rel_obs=0.8270, t_f_obs=90.0, commodity_type="A")
    assert got == expected.ctpl_rounded


@pytest.mark.parametrize("func,t_base", [
    (tables.ctl_from_observed_density_15c, 15),
    (tables.ctl_from_observed_density_20c, 20),
])
def test_ctl_from_observed_metric_density(func, t_base):
    expected = correct_metric_observed_to_base(
        rho_o=827.0, t_o_c=35.0, p_o=0, pressure_unit="kPa", t_base_c=t_base, commodity_type="A"
    )
    assert func(den_obs=827.0, t_c_obs=35.0, commodity_type="A") == expected.ctpl_rounded
