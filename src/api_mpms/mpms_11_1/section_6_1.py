# api_mpms/mpms_11_1/section_6_1.py

import math
from typing import Optional, Tuple

from api_mpms.constants.commodity_groups import (
    COMMODITY_GROUPS,
    resolve_commodity_group,
)
from api_mpms.exceptions.validation import MPMSValidationError
from api_mpms.validators.inputs import (
    validate_temperature_f,
    validate_pressure_psig,
)

from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68


DELTA_60 = 0.01374979547
T_BASE_IPTS68 = 60.0068749


def correct_base_to_alternate(
    rho_60: float,
    t_f: float,
    p_psig: float,
    *,
    alpha_60: Optional[float] = None,
    commodity_group: Optional[str] = None,
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.1
    Correct volume and density from base (60°F, 0 psig)
    to alternate temperature and pressure.

    Returns:
        rho, CTL, Fp, CPL, CTPL, alpha_60
    """

    validate_temperature_f(t_f)
    p_psig = validate_pressure_psig(p_psig)

    # Step 2 – temperature shift
    t_ipts68 = its90_to_ipts68(t_f_90=t_f)

    # Step 3 – density shift to IPTS-68
    if alpha_60 is not None:
        exponent = 0.5 * alpha_60 * DELTA_60 * (1.0 + 0.4 * alpha_60 * DELTA_60)
        rho_68 = rho_60 * math.exp(exponent)

    else:
        if not commodity_group:
            raise MPMSValidationError(
                "commodity_group (A, B, D) required when alpha_60 is not provided"
            )

        group = resolve_commodity_group(
            rho=rho_60,
            commodity_type=commodity_group,
        )
        
        K0, K1, K2 = group.K0, group.K1, group.K2

        A = (DELTA_60 / 2.0) * ((K0 / rho_60**2) + (K1 / rho_60) + K2)
        B = (2.0 * K0 + K1 * rho_60) / (K0 + (K1 + K2 * rho_60) * rho_60)

        exp_term = math.exp(A * (1.0 + 0.8 * A)) - 1.0
        rho_68 = rho_60 * (
            1.0 + exp_term / (1.0 + A * (1.0 + 1.6 * A) * B)
        )

        alpha_60 = ((K0 / rho_68) + K1) / rho_68 + K2

    # Step 5 – CTL
    delta_t = t_ipts68 - T_BASE_IPTS68
    ctl_exp = -alpha_60 * delta_t * (
        1.0 + 0.8 * alpha_60 * (delta_t + DELTA_60)
    )
    CTL = math.exp(ctl_exp)

    if rho_60 <= 0:
        fp = 0.0
        CPL = 1.0
    else:
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

        CPL = 1.0 / denom

    CTPL = CTL * CPL
    rho = CTPL * rho_60

    return rho, CTL, fp, CPL, CTPL, alpha_60
