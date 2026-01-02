# api_mpms/mpms_11_1/section_6_2.py

from typing import Optional, Tuple

from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate
from api_mpms.constants.iteration_coefficients import da_coefficient
from api_mpms.exceptions.validation import MPMSValidationError
from api_mpms.exceptions.convergence import MPMSConvergenceError
from api_mpms.validators.inputs import (
    validate_temperature_f,
    validate_pressure_psig,
)


_MAX_ITER = 15
_RHO_TOL = 1.0e-6


def correct_observed_to_base(
    *,
    rho_o: float,
    t_o: float,
    p_o: float,
    commodity_type: str,
    alpha_60: Optional[float] = None,
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        rho_60, CTL, Fp, CPL, CTPL
    """

    section_6_2 = False
    
    validate_temperature_f(t_o)
    p_o = validate_pressure_psig(p_o)

    commodity_type = commodity_type.lower()
    if commodity_type not in {"a", "b", "c","d"}:
        raise MPMSValidationError("commodity_type must be 'a', 'b', 'c', or 'd'")

    # Initial guess
    rho_60 = rho_o

    # Normative bounds
    bounds_60 = {
        "a": (610.6, 1163.5),
        "b": (610.6, 1163.5),
        "d": (800.9, 1163.5),
        "c": (-10000000, 1000000)
    }
    rho_min, rho_max = bounds_60[commodity_type]

    rho_60 = max(min(rho_60, rho_max), rho_min)

    alpha_iter = alpha_60

    for m in range(_MAX_ITER):
        
        CTL, Fp, CPL, CTPL, alpha_iter = correct_base_to_alternate(
            rho_60=rho_60,
            t_f=t_o,
            p_psig=p_o,
            commodity_group=commodity_type,
            alpha_60=alpha_60,
        )

        rho_calc = rho_60 * CTPL
        delta_rho_o = rho_o - rho_calc

        if abs(delta_rho_o) < _RHO_TOL:
            return rho_60, CTL, Fp, CPL, CTPL

        # --- Iterative correction ---
        Da = da_coefficient(
            commodity_type=commodity_type,
            rho_60=rho_60,
            alpha_given=alpha_60 is not None,
        )

        E_m = (rho_o / (CTL * CPL)) - rho_60

        delta_t = t_o - 60.0
        DT_m = Da * alpha_iter * delta_t * (1.0 + 1.6 * alpha_iter * delta_t)

        DP_m = -(
            2.0
            * CPL
            * p_o
            * Fp
            * (7.93920 + 0.02326 * t_o)
        ) / (rho_60**2)

        delta_rho_60 = E_m / (1.0 + DT_m + DP_m)

        # Enforce bounds
        rho_next = rho_60 + delta_rho_60
        rho_60 = max(min(rho_next, rho_max), rho_min)

    raise MPMSConvergenceError(
        f"API MPMS 11.1.6.2 did not converge within 15 iterations rho_o: {rho_o} - t_o: {t_o}"
    )
