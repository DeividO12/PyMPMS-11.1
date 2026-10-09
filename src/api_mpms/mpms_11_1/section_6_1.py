# api_mpms/mpms_11_1/section_6_1.py

import math
from typing import NamedTuple, Optional

from api_mpms.constants.commodity_groups import CommodityGroup, resolve_commodity_group
from api_mpms.constants.commodity_types import CommodityType
from api_mpms.exceptions.validation import MPMSRangeError
from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.results import BaseToAlternateResult
from api_mpms.validators.inputs import (
    validate_alpha_60,
    validate_commodity_and_alpha,
    validate_density,
    validate_pressure_psig,
    validate_temperature_f,
)


DELTA_60 = 0.01374979547
T_BASE_IPTS68 = 60.0068749
CTPL_DELTA = 0.00001


class _Factors(NamedTuple):
    """Factores sin redondear de los pasos 3 a 9 (uso interno)."""

    rho: float
    ctl: float
    fp: float
    cpl: float
    ctpl: float
    alpha_60: float


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
) -> _Factors:
    """
    Pasos 3 a 9 de 11.1.6.1 sin validación ni redondeo.

    Recibe la temperatura ya convertida a IPTS-68 para que el procedimiento
    iterativo de 11.1.6.2 no repita la conversión en cada iteración
    (11.1.6.2 Paso 3: «Do not check the input values», «Do not round»).
    """
    # Step 3 – density shift to IPTS-68
    if group is None:
        assert alpha_60 is not None
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

        # Step 4 – alpha_60
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
        raise MPMSRangeError("Invalid CPL denominator")
    cpl = 1.0 / denom

    # Step 8 – CTPL; Step 9 – density at alternate conditions
    ctpl = ctl * cpl
    return _Factors(ctpl * rho_60, ctl, fp, cpl, ctpl, alpha_60)


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
        Densidad base (kg/m³). Para A/B/D debe estar dentro de los límites del
        tipo (610.6 o 800.9 a 1163.5 kg/m³); para C basta con que sea > 0.
    t_f : float
        Temperatura alterna (°F, ITS-90), de −58.0 a 302.0.
    p_psig : float
        Presión alterna (psig), hasta 1500. Los valores negativos se toman como 0.
    commodity_type : {"A", "B", "C", "D"}, optional
        Obligatorio si no se da ``alpha_60``.
    alpha_60 : float, optional
        Coeficiente de expansión térmica a 60 °F (°F⁻¹), 230e-6 a 930e-6, para
        aplicaciones especiales (tipo C). Excluyente con los tipos A, B y D.

    Raises
    ------
    MPMSRangeError
        Si alguna entrada está fuera de los límites del procedimiento (Paso 1).
    MPMSValidationError
        Si alguna entrada es inválida (tipo, NaN, combinación no permitida).
    """
    t_f = validate_temperature_f(t_f)
    p_psig = validate_pressure_psig(p_psig)
    rho_60 = validate_density(rho_60, "rho_60")
    ct, alpha_60 = validate_commodity_and_alpha(commodity_type, alpha_60)
    group = None if ct is CommodityType.SPECIAL_APPLICATIONS else resolve_commodity_group(rho_60, ct)

    # Step 2 – temperature shift
    t_ipts68 = its90_to_ipts68(t_f_90=t_f)
    f = _correct_core(rho_60, t_ipts68, p_psig, alpha_60, group)
    return BaseToAlternateResult(
        f.rho, f.ctl, f.fp, f.cpl, f.ctpl, api_round(f.ctpl, CTPL_DELTA), f.alpha_60
    )


def ctl_from_alpha(*, alpha_60: float, t_f: float) -> float:
    """
    CTL sin redondear de un líquido de tipo C a partir de alpha_60 (°F⁻¹).

    No requiere densidad: con alpha_60 dado, CTL solo depende de alpha_60 y de
    la temperatura (11.1.6.1 Paso 5). Es el cálculo de las tablas 6C, 24C, 54C
    y 60C, generadas a presión 0 (11.1.8.23, 11.1.8.24).
    """
    t_f = validate_temperature_f(t_f)
    alpha_60 = validate_alpha_60(alpha_60)
    return _ctl(alpha_60, its90_to_ipts68(t_f_90=t_f))
