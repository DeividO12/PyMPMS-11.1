# api_mpms/mpms_11_1/section_6_2.py

import math
from typing import Optional

from api_mpms.constants.commodity_groups import COMMODITY_TYPE_BOUNDS, resolve_commodity_group
from api_mpms.constants.physical import T_BASE_F
from api_mpms.exceptions.convergence import MPMSConvergenceError
from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68
from api_mpms.mpms_11_1.section_6_1 import _correct_core
from api_mpms.results import ObservedToBaseResult
from api_mpms.validators.inputs import (
    validate_alpha_60,
    validate_commodity_type,
    validate_density,
    validate_pressure_psig,
    validate_temperature_f,
)


_MAX_ITER = 15
_RHO_TOL = 1.0e-6


def correct_observed_to_base(
    *,
    rho_o: float,
    t_o: float,
    p_o: float,
    commodity_type: Optional[str] = None,
    alpha_60: Optional[float] = None,
) -> ObservedToBaseResult:
    """
    API MPMS 11.1.6.2

    Corrige volumen y densidad desde condiciones observadas a condiciones
    base (60 °F, 0 psig) mediante el procedimiento iterativo.

    Parameters
    ----------
    rho_o : float
        Densidad observada (kg/m³), > 0.
    t_o : float
        Temperatura observada (°F, ITS-90).
    p_o : float
        Presión observada (psig). Los valores negativos se toman como 0.
    commodity_type : {"A", "B", "C", "D"}, optional
        Obligatorio si no se da ``alpha_60``; el tipo C requiere ``alpha_60``.
    alpha_60 : float, optional
        Coeficiente de expansión térmica a 60 °F (°F⁻¹).

    Raises
    ------
    MPMSValidationError
        Si alguna entrada es inválida o está fuera de rango.
    MPMSConvergenceError
        Si la iteración no converge en ``_MAX_ITER`` iteraciones.
    """
    t_o = validate_temperature_f(t_o)
    p_o = validate_pressure_psig(p_o)
    rho_o = validate_density(rho_o, "rho_o")

    if alpha_60 is not None:
        alpha_60 = validate_alpha_60(alpha_60)
    ct = None
    if commodity_type is not None or alpha_60 is None:
        ct = validate_commodity_type(commodity_type, alpha_60)

    # Normative bounds
    rho_min, rho_max = COMMODITY_TYPE_BOUNDS.get(ct, (-math.inf, math.inf))

    # Step 2 – temperature shift (invariante durante la iteración)
    t_ipts68 = its90_to_ipts68(t_f_90=t_o)

    delta_t = t_o - T_BASE_F
    dp_factor = 7.93920 + 0.02326 * t_o

    # Initial guess
    rho_60 = max(min(rho_o, rho_max), rho_min)

    for _ in range(_MAX_ITER):
        group = None if alpha_60 is not None else resolve_commodity_group(rho_60, ct)
        rho, ctl, fp, cpl, ctpl, alpha_iter = _correct_core(
            rho_60, t_ipts68, p_o, alpha_60, group
        )

        delta_rho_o = rho_o - rho

        if abs(delta_rho_o) < _RHO_TOL:
            return ObservedToBaseResult(rho_60, ctl, fp, cpl, ctpl)

        # --- Iterative correction ---
        Da = 0.0 if group is None else group.Da

        E_m = (rho_o / (ctl * cpl)) - rho_60

        DT_m = Da * alpha_iter * delta_t * (1.0 + 1.6 * alpha_iter * delta_t)

        DP_m = -(
            2.0
            * cpl
            * p_o
            * fp
            * dp_factor
        ) / (rho_60**2)

        delta_rho_60 = E_m / (1.0 + DT_m + DP_m)

        # Enforce bounds
        rho_next = rho_60 + delta_rho_60
        rho_60 = max(min(rho_next, rho_max), rho_min)

    raise MPMSConvergenceError(
        f"API MPMS 11.1.6.2 did not converge within {_MAX_ITER} iterations "
        f"(rho_o={rho_o}, t_o={t_o}, p_o={p_o}, commodity_type={ct and ct.value}, "
        f"alpha_60={alpha_60})"
    )
