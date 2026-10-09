# api_mpms/mpms_11_1/section_6_1.py

import math
from typing import Optional

from api_mpms.constants.commodity_groups import CommodityGroup, resolve_commodity_group
from api_mpms.exceptions.validation import MPMSValidationError
from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68
from api_mpms.results import BaseToAlternateResult
from api_mpms.validators.inputs import (
    validate_alpha_60,
    validate_commodity_type,
    validate_density,
    validate_pressure_psig,
    validate_temperature_f,
)


DELTA_60 = 0.01374979547
T_BASE_IPTS68 = 60.0068749


def _ctl(alpha_60: float, t_ipts68: float) -> float:
    """Step 5 – CTL."""
    delta_t = t_ipts68 - T_BASE_IPTS68
    ctl_exp = -alpha_60 * delta_t * (
        1.0 + 0.8 * alpha_60 * (delta_t + DELTA_60)
    )
    return math.exp(ctl_exp)


def _correct_core(
    rho_60: float,
    t_ipts68: float,
    p_psig: float,
    alpha_60: Optional[float],
    group: Optional[CommodityGroup],
) -> BaseToAlternateResult:
    """
    Pasos 3 a 8 de 11.1.6.1 sin validación.

    Recibe la temperatura ya convertida a IPTS-68 para que el procedimiento
    iterativo de 11.1.6.2 no repita la conversión en cada iteración.
    """
    # Step 3 – density shift to IPTS-68
    if group is None:
        exponent = 0.5 * alpha_60 * DELTA_60 * (1.0 + 0.4 * alpha_60 * DELTA_60)
        rho_68 = rho_60 * math.exp(exponent)
    else:
        K0, K1, K2 = group.K0, group.K1, group.K2

        A = (DELTA_60 / 2.0) * ((K0 / rho_60**2) + (K1 / rho_60) + K2)
        B = (2.0 * K0 + K1 * rho_60) / (K0 + (K1 + K2 * rho_60) * rho_60)

        exp_term = math.exp(A * (1.0 + 0.8 * A)) - 1.0
        rho_68 = rho_60 * (
            1.0 + exp_term / (1.0 + A * (1.0 + 1.6 * A) * B)
        )

        alpha_60 = ((K0 / rho_68) + K1) / rho_68 + K2

    # Step 5 – CTL
    ctl = _ctl(alpha_60, t_ipts68)

    # Step 6 – Fp
    fp = math.exp(
        -1.9947
        + 0.00013427 * t_ipts68
        + (793920.0 + 2326.0 * t_ipts68) / rho_68**2
    )

    # Step 7 – CPL
    denom = 1.0 - 1.0e-5 * fp * p_psig
    if denom <= 0:
        raise MPMSValidationError("Invalid CPL denominator")
    cpl = 1.0 / denom

    ctpl = ctl * cpl
    return BaseToAlternateResult(ctpl * rho_60, ctl, fp, cpl, ctpl, alpha_60)


def correct_base_to_alternate(
    *,
    rho_60: float,
    t_f: float,
    p_psig: float,
    commodity_type: Optional[str] = None,
    alpha_60: Optional[float] = None,
) -> BaseToAlternateResult:
    """
    API MPMS 11.1.6.1

    Corrige volumen y densidad desde condiciones base (60 °F, 0 psig) a una
    temperatura y presión alternas.

    Parameters
    ----------
    rho_60 : float
        Densidad base (kg/m³), > 0.
    t_f : float
        Temperatura alterna (°F, ITS-90).
    p_psig : float
        Presión alterna (psig). Los valores negativos se toman como 0.
    commodity_type : {"A", "B", "D", "C"}, optional
        Obligatorio si no se da ``alpha_60``.
    alpha_60 : float, optional
        Coeficiente de expansión térmica a 60 °F (°F⁻¹) para aplicaciones
        especiales (tipo C). Si se da, prevalece sobre ``commodity_type``.

    Raises
    ------
    MPMSValidationError
        Si alguna entrada es inválida o está fuera de rango.
    """
    t_f = validate_temperature_f(t_f)
    p_psig = validate_pressure_psig(p_psig)
    rho_60 = validate_density(rho_60, "rho_60")

    if alpha_60 is not None:
        alpha_60 = validate_alpha_60(alpha_60)
        group = None
    else:
        ct = validate_commodity_type(commodity_type)
        group = resolve_commodity_group(rho_60, ct)

    # Step 2 – temperature shift
    t_ipts68 = its90_to_ipts68(t_f_90=t_f)
    return _correct_core(rho_60, t_ipts68, p_psig, alpha_60, group)


def ctl_from_alpha(*, alpha_60: float, t_f: float) -> float:
    """
    CTL de un líquido de aplicación especial (tipo C) a partir de alpha_60.

    No requiere densidad: CTL solo depende de alpha_60 y de la temperatura
    (tablas 6C, 24C, 54C y 60C).
    """
    t_f = validate_temperature_f(t_f)
    alpha_60 = validate_alpha_60(alpha_60)
    return _ctl(alpha_60, its90_to_ipts68(t_f_90=t_f))
