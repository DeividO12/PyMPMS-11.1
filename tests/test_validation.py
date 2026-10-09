"""Casos borde de validación (auditoría 2026-10-09: F-02, F-05..F-08, V-01, V-03, V-04, V-06, V-07)."""

import math

import pytest

from api_mpms.constants.commodity_types import CommodityType
from api_mpms.exceptions.validation import MPMSValidationError
from api_mpms.mpms_11_1.section_5_1 import api_to_rho, gamma_t_to_rho, rho_to_api, rho_to_gamma_t
from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate, ctl_from_alpha
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.validators.inputs import (
    validate_commodity_type,
    validate_pressure_psig,
    validate_temperature_f,
)

NOT_FINITE = [math.nan, math.inf, -math.inf]


@pytest.mark.parametrize("rho", [0, -800, *NOT_FINITE, None, "850"])
def test_base_to_alternate_rejects_invalid_density(rho):
    with pytest.raises(MPMSValidationError):
        correct_base_to_alternate(rho_60=rho, t_f=60, p_psig=0, commodity_type="A")


@pytest.mark.parametrize("rho", [0, -5, *NOT_FINITE])
def test_observed_to_base_rejects_invalid_density(rho):
    with pytest.raises(MPMSValidationError):
        correct_observed_to_base(rho_o=rho, t_o=60, p_o=0, commodity_type="A")


@pytest.mark.parametrize("p", [*NOT_FINITE, None, 1500.1])
def test_invalid_pressure(p):
    with pytest.raises(MPMSValidationError):
        validate_pressure_psig(p)


def test_negative_pressure_is_zero():
    assert validate_pressure_psig(-7.3) == 0.0


@pytest.mark.parametrize("t", [*NOT_FINITE, None, -58.1, 302.1])
def test_invalid_temperature(t):
    with pytest.raises(MPMSValidationError):
        validate_temperature_f(t)


@pytest.mark.parametrize("alpha", [0.0, -0.001, *NOT_FINITE])
def test_invalid_alpha(alpha):
    with pytest.raises(MPMSValidationError):
        correct_base_to_alternate(rho_60=800, t_f=100, p_psig=0, alpha_60=alpha)


@pytest.mark.parametrize("ct", [None, 1, "E", "", "AB"])
def test_invalid_commodity_type(ct):
    with pytest.raises(MPMSValidationError):
        correct_base_to_alternate(rho_60=800, t_f=60, p_psig=0, commodity_type=ct)


def test_type_c_requires_alpha():
    with pytest.raises(MPMSValidationError, match="requires alpha_60"):
        correct_observed_to_base(rho_o=800, t_o=60, p_o=0, commodity_type="C")


@pytest.mark.parametrize("ct", ["a", "A", " b ", CommodityType.LUBRICATING_OILS])
def test_commodity_type_normalization(ct):
    assert isinstance(validate_commodity_type(ct), CommodityType)


def test_its90_requires_exactly_one_temperature():
    with pytest.raises(MPMSValidationError):
        its90_to_ipts68(t_f_90=212, t_c_90=0)
    with pytest.raises(MPMSValidationError):
        its90_to_ipts68()


@pytest.mark.parametrize("func,value", [
    (rho_to_api, 0), (rho_to_gamma_t, -1), (api_to_rho, -131.5), (gamma_t_to_rho, 0),
])
def test_unit_conversion_domain(func, value):
    with pytest.raises(MPMSValidationError):
        func(value)


def test_results_are_named():
    res = correct_base_to_alternate(rho_60=850, t_f=100, p_psig=100, commodity_type="A")
    assert res.ctpl == pytest.approx(res.ctl * res.cpl)
    assert len(res) == 6
    obs = correct_observed_to_base(rho_o=res.rho, t_o=100, p_o=100, commodity_type="A")
    assert obs.rho_60 == pytest.approx(850, abs=1e-5)


def test_ctl_from_alpha_matches_full_procedure():
    full = correct_base_to_alternate(rho_60=853.7, t_f=84.5, p_psig=0, alpha_60=0.00057634)
    assert ctl_from_alpha(alpha_60=0.00057634, t_f=84.5) == full.ctl
