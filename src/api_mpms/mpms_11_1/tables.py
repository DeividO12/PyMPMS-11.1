# api_mpms/mpms_11_1/tables.py

"""
Factores CTL en formato de tabla (API MPMS 11.1.8).

Cada función redondea sus entradas y su resultado según 11.1.5.4.
"""

from api_mpms.mpms_11_1.section_5_1 import (
    alpha_c_to_alpha_f,
    api_to_rho,
    celsius_to_fahrenheit,
    gamma_t_to_rho,
    rho_to_api,
    rho_to_gamma_t,
)
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate, ctl_from_alpha
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.mpms_11_1.section_7_1 import correct_observed_to_alternate_C
from api_mpms.mpms_11_1.section_7_2 import correct_observed_to_base_C

_CTL_DELTA = 0.00001


def _ctl_base_to_alternate(rho_60: float, t_f: float, commodity_type: str) -> float:
    ctl = correct_base_to_alternate(
        rho_60=rho_60, t_f=t_f, p_psig=0, commodity_type=commodity_type
    ).ctl
    return api_round(ctl, _CTL_DELTA)


def table_6x(*, api_base: float, t_f_obs: float, commodity_type: str) -> float:
    """Tablas 6A/6B/6D: CTL a partir de la gravedad API base (°API, °F)."""
    api_base = api_round(api_base, 0.1)
    t_f_obs = api_round(t_f_obs, 0.1)
    return _ctl_base_to_alternate(api_to_rho(api_base), t_f_obs, commodity_type)


def table_5x_6x(*, api_obs: float, t_f_obs: float, commodity_type: str) -> float:
    """Tablas 5x + 6x: CTL a partir de la gravedad API observada (°API, °F)."""
    api_obs = api_round(api_obs, 0.1)
    t_f_obs = api_round(t_f_obs, 0.1)

    rho_60 = correct_observed_to_base(
        rho_o=api_to_rho(api_obs), t_o=t_f_obs, p_o=0, commodity_type=commodity_type
    ).rho_60
    api_60 = api_round(rho_to_api(rho_60), 0.1)

    return _ctl_base_to_alternate(api_to_rho(api_60), t_f_obs, commodity_type)


def table_6c_24c(*, alpha_obs: float, t_f_obs: float) -> float:
    """Tablas 6C/24C: CTL a partir de alpha_60 (°F⁻¹) y temperatura (°F)."""
    t_f_obs = api_round(t_f_obs, 0.1)
    return api_round(ctl_from_alpha(alpha_60=alpha_obs, t_f=t_f_obs), _CTL_DELTA)


def table_24x(*, rel_base: float, t_f_obs: float, commodity_type: str) -> float:
    """Tablas 24A/24B/24D: CTL a partir de la densidad relativa base 60/60 °F."""
    rel_base = api_round(rel_base, 0.0001)
    t_f_obs = api_round(t_f_obs, 0.1)
    return _ctl_base_to_alternate(gamma_t_to_rho(rel_base), t_f_obs, commodity_type)


def table_23x_24x(*, rel_obs: float, t_f_obs: float, commodity_type: str) -> float:
    """Tablas 23x + 24x: CTL a partir de la densidad relativa observada."""
    rel_obs = api_round(rel_obs, 0.0001)
    t_f_obs = api_round(t_f_obs, 0.1)

    rho_60 = correct_observed_to_base(
        rho_o=gamma_t_to_rho(rel_obs), t_o=t_f_obs, p_o=0, commodity_type=commodity_type
    ).rho_60
    rel_60 = api_round(rho_to_gamma_t(rho_60), 0.0001)

    return _ctl_base_to_alternate(gamma_t_to_rho(rel_60), t_f_obs, commodity_type)


def _ctl_metric_from_alpha(alpha_c: float, t_c_obs: float, t_b: float) -> float:
    alpha_f = alpha_c_to_alpha_f(alpha_c)
    ctl = (
        ctl_from_alpha(alpha_60=alpha_f, t_f=celsius_to_fahrenheit(t_c_obs))
        / ctl_from_alpha(alpha_60=alpha_f, t_f=celsius_to_fahrenheit(t_b))
    )
    return api_round(ctl, _CTL_DELTA)


def _ctl_metric(den_base: float, t_c_obs: float, t_b: float, commodity_type: str) -> float:
    _, ctl, _, _, _ = correct_observed_to_alternate_C(
        rho_t=den_base, t_a_c=t_c_obs, p_a=0, t_b=t_b, commodity_type=commodity_type
    )
    return api_round(ctl, _CTL_DELTA)


def _ctl_metric_observed(den_obs: float, t_c_obs: float, t_b: float, commodity_type: str) -> float:
    rho_b = correct_observed_to_base_C(
        rho_o=den_obs, t_o_c=t_c_obs, p_o=0, t_b=t_b, commodity_type=commodity_type
    )[0]
    return _ctl_metric(api_round(rho_b, 0.1), t_c_obs, t_b, commodity_type)


def table_54x(*, den_base: float, t_c_obs: float, commodity_type: str) -> float:
    """Tablas 54A/54B/54D: CTL a partir de la densidad base a 15 °C (kg/m³, °C)."""
    return _ctl_metric(api_round(den_base, 0.1), api_round(t_c_obs, 0.05), 15.0, commodity_type)


def table_54c(*, alpha_obs: float, t_c_obs: float) -> float:
    """Tabla 54C: CTL a partir de alpha a 15 °C (°C⁻¹) y temperatura (°C)."""
    return _ctl_metric_from_alpha(alpha_obs, api_round(t_c_obs, 0.05), 15.0)


def table_53x_54x(*, den_obs: float, t_c_obs: float, commodity_type: str) -> float:
    """Tablas 53x + 54x: CTL a partir de la densidad observada (kg/m³, °C), base 15 °C."""
    return _ctl_metric_observed(
        api_round(den_obs, 0.1), api_round(t_c_obs, 0.05), 15.0, commodity_type
    )


def table_60x(*, den_base: float, t_c_obs: float, commodity_type: str) -> float:
    """Tablas 60A/60B/60D: CTL a partir de la densidad base a 20 °C (kg/m³, °C)."""
    return _ctl_metric(api_round(den_base, 0.1), api_round(t_c_obs, 0.05), 20.0, commodity_type)


def table_60c(*, alpha_obs: float, t_c_obs: float) -> float:
    """Tabla 60C: CTL a partir de alpha a 20 °C (°C⁻¹) y temperatura (°C)."""
    return _ctl_metric_from_alpha(alpha_obs, api_round(t_c_obs, 0.05), 20.0)


def table_59x_60x(*, den_obs: float, t_c_obs: float, commodity_type: str) -> float:
    """Tablas 59x + 60x: CTL a partir de la densidad observada (kg/m³, °C), base 20 °C."""
    return _ctl_metric_observed(
        api_round(den_obs, 0.1), api_round(t_c_obs, 0.05), 20.0, commodity_type
    )
