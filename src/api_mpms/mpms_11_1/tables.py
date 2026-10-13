# api_mpms/mpms_11_1/tables.py

"""
Valores en formato de tabla (API MPMS 11.1.8).

Las tablas se generan con entradas redondeadas y salida redondeada
(11.1.5.4, 11.1.8); los valores intermedios nunca se redondean (11.1.3.9).
Todas se calculan a presión 0.
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
from api_mpms.mpms_11_1.section_7_1 import correct_metric_base_to_alternate
from api_mpms.mpms_11_1.section_7_2 import correct_metric_observed_to_base

# Incrementos de redondeo de 11.1.5.4
_API_DELTA = 0.1
_REL_DELTA = 0.0001
_RHO_DELTA = 0.1
_T_F_DELTA = 0.1
_T_C_DELTA = 0.05
_CTL_DELTA = 0.00001
_ALPHA_F_DELTA = 0.0000001  # °F⁻¹
_ALPHA_C_DELTA = 0.0000002  # °C⁻¹


# --- Tablas de densidad base a partir de la densidad observada (5, 23, 53, 59) ---


def table_5x(*, api_obs: float, t_f_obs: float, commodity_type: str) -> float:
    """Tablas 5A/5B/5D (11.1.8.1-3): gravedad API a 60 °F a partir de la API observada."""
    rho_60 = correct_observed_to_base(
        rho_o=api_to_rho(api_round(api_obs, _API_DELTA)),
        t_o=api_round(t_f_obs, _T_F_DELTA),
        p_o=0,
        commodity_type=commodity_type,
    ).rho_60
    return api_round(rho_to_api(rho_60), _API_DELTA)


def table_23x(*, rel_obs: float, t_f_obs: float, commodity_type: str) -> float:
    """Tablas 23A/23B/23D (11.1.8.6-8): densidad relativa 60/60 °F a partir de la observada."""
    rho_60 = correct_observed_to_base(
        rho_o=gamma_t_to_rho(api_round(rel_obs, _REL_DELTA)),
        t_o=api_round(t_f_obs, _T_F_DELTA),
        p_o=0,
        commodity_type=commodity_type,
    ).rho_60
    return api_round(rho_to_gamma_t(rho_60), _REL_DELTA)


def _metric_base_density(den_obs: float, t_c_obs: float, t_base_c: float, commodity_type: str) -> float:
    rho_base = correct_metric_observed_to_base(
        rho_o=api_round(den_obs, _RHO_DELTA),
        t_o_c=api_round(t_c_obs, _T_C_DELTA),
        p_o=0,
        pressure_unit="kPa",
        t_base_c=t_base_c,
        commodity_type=commodity_type,
    ).rho_base
    return api_round(rho_base, _RHO_DELTA)


def table_53x(*, den_obs: float, t_c_obs: float, commodity_type: str) -> float:
    """Tablas 53A/53B/53D (11.1.8.11-13): densidad a 15 °C a partir de la observada (kg/m³, °C)."""
    return _metric_base_density(den_obs, t_c_obs, 15.0, commodity_type)


def table_59x(*, den_obs: float, t_c_obs: float, commodity_type: str) -> float:
    """Tablas 59A/59B/59D (11.1.8.17-19): densidad a 20 °C a partir de la observada (kg/m³, °C)."""
    return _metric_base_density(den_obs, t_c_obs, 20.0, commodity_type)


# --- Tablas de CTL a partir de la densidad base (6, 24, 54, 60) ---


def _ctl_base_to_alternate(rho_60: float, t_f: float, commodity_type: str) -> float:
    ctl = correct_base_to_alternate(
        rho_60=rho_60, t_f=t_f, p_psig=0, commodity_type=commodity_type
    ).ctl
    return api_round(ctl, _CTL_DELTA)


def table_6x(*, api_base: float, t_f_obs: float, commodity_type: str) -> float:
    """Tablas 6A/6B/6D (11.1.8.4-5): CTL a partir de la gravedad API base (°API, °F)."""
    api_base = api_round(api_base, _API_DELTA)
    t_f_obs = api_round(t_f_obs, _T_F_DELTA)
    return _ctl_base_to_alternate(api_to_rho(api_base), t_f_obs, commodity_type)


def table_24x(*, rel_base: float, t_f_obs: float, commodity_type: str) -> float:
    """Tablas 24A/24B/24D (11.1.8.9-10): CTL a partir de la densidad relativa base 60/60 °F."""
    rel_base = api_round(rel_base, _REL_DELTA)
    t_f_obs = api_round(t_f_obs, _T_F_DELTA)
    return _ctl_base_to_alternate(gamma_t_to_rho(rel_base), t_f_obs, commodity_type)


def _ctl_metric(den_base: float, t_c_obs: float, t_base_c: float, commodity_type: str) -> float:
    ctl = correct_metric_base_to_alternate(
        rho_base=api_round(den_base, _RHO_DELTA),
        t_base_c=t_base_c,
        t_c=api_round(t_c_obs, _T_C_DELTA),
        p=0,
        pressure_unit="kPa",
        commodity_type=commodity_type,
    ).ctl
    return api_round(ctl, _CTL_DELTA)


def table_54x(*, den_base: float, t_c_obs: float, commodity_type: str) -> float:
    """Tablas 54A/54B/54D (11.1.8.14-16): CTL a partir de la densidad a 15 °C (kg/m³, °C)."""
    return _ctl_metric(den_base, t_c_obs, 15.0, commodity_type)


def table_60x(*, den_base: float, t_c_obs: float, commodity_type: str) -> float:
    """Tablas 60A/60B/60D (11.1.8.20-22): CTL a partir de la densidad a 20 °C (kg/m³, °C)."""
    return _ctl_metric(den_base, t_c_obs, 20.0, commodity_type)


# --- Tablas C: CTL a partir de alpha (sin densidad) ---


def table_6c_24c(*, alpha_obs: float, t_f_obs: float) -> float:
    """Tablas 6C/24C (11.1.8.23): CTL a partir de alpha_60 (°F⁻¹) y temperatura (°F)."""
    alpha_obs = api_round(alpha_obs, _ALPHA_F_DELTA)
    t_f_obs = api_round(t_f_obs, _T_F_DELTA)
    return api_round(ctl_from_alpha(alpha_60=alpha_obs, t_f=t_f_obs), _CTL_DELTA)


def _ctl_metric_from_alpha(alpha_c: float, t_c_obs: float, t_base_c: float) -> float:
    """11.1.7.1 con alpha dado: CTL = CTL(t) / CTL(T_base)."""
    alpha_f = alpha_c_to_alpha_f(api_round(alpha_c, _ALPHA_C_DELTA))
    t_c_obs = api_round(t_c_obs, _T_C_DELTA)
    ctl = (
        ctl_from_alpha(alpha_60=alpha_f, t_f=celsius_to_fahrenheit(t_c_obs))
        / ctl_from_alpha(alpha_60=alpha_f, t_f=celsius_to_fahrenheit(t_base_c))
    )
    return api_round(ctl, _CTL_DELTA)


def table_54c(*, alpha_obs: float, t_c_obs: float) -> float:
    """Tabla 54C (11.1.8.24): CTL a partir de alpha (°C⁻¹) y temperatura (°C), base 15 °C."""
    return _ctl_metric_from_alpha(alpha_obs, t_c_obs, 15.0)


def table_60c(*, alpha_obs: float, t_c_obs: float) -> float:
    """Tabla 60C (11.1.8.24): CTL a partir de alpha (°C⁻¹) y temperatura (°C), base 20 °C."""
    return _ctl_metric_from_alpha(alpha_obs, t_c_obs, 20.0)


# --- CTL a partir de la densidad observada (procedimiento normativo directo) ---
#
# Sustituyen a las antiguas table_5x_6x, table_23x_24x, table_53x_54x y
# table_59x_60x, que encadenaban dos tablas redondeando la densidad base
# intermedia (no permitido por 11.1.3.9). El CTL es el de 11.1.6.2 Paso 7 o
# 11.1.7.2 Paso 4, con entradas y salida redondeadas como en las tablas.


def ctl_from_observed_api(*, api_obs: float, t_f_obs: float, commodity_type: str) -> float:
    """CTL (60 °F) a partir de la gravedad API observada, por 11.1.6.2."""
    ctl = correct_observed_to_base(
        rho_o=api_to_rho(api_round(api_obs, _API_DELTA)),
        t_o=api_round(t_f_obs, _T_F_DELTA),
        p_o=0,
        commodity_type=commodity_type,
    ).ctl
    return api_round(ctl, _CTL_DELTA)


def ctl_from_observed_relative_density(*, rel_obs: float, t_f_obs: float, commodity_type: str) -> float:
    """CTL (60 °F) a partir de la densidad relativa observada, por 11.1.6.2."""
    ctl = correct_observed_to_base(
        rho_o=gamma_t_to_rho(api_round(rel_obs, _REL_DELTA)),
        t_o=api_round(t_f_obs, _T_F_DELTA),
        p_o=0,
        commodity_type=commodity_type,
    ).ctl
    return api_round(ctl, _CTL_DELTA)


def _ctl_from_observed_metric(den_obs: float, t_c_obs: float, t_base_c: float, commodity_type: str) -> float:
    ctl = correct_metric_observed_to_base(
        rho_o=api_round(den_obs, _RHO_DELTA),
        t_o_c=api_round(t_c_obs, _T_C_DELTA),
        p_o=0,
        pressure_unit="kPa",
        t_base_c=t_base_c,
        commodity_type=commodity_type,
    ).ctl
    return api_round(ctl, _CTL_DELTA)


def ctl_from_observed_density_15c(*, den_obs: float, t_c_obs: float, commodity_type: str) -> float:
    """CTL (base 15 °C) a partir de la densidad observada (kg/m³, °C), por 11.1.7.2."""
    return _ctl_from_observed_metric(den_obs, t_c_obs, 15.0, commodity_type)


def ctl_from_observed_density_20c(*, den_obs: float, t_c_obs: float, commodity_type: str) -> float:
    """CTL (base 20 °C) a partir de la densidad observada (kg/m³, °C), por 11.1.7.2."""
    return _ctl_from_observed_metric(den_obs, t_c_obs, 20.0, commodity_type)
