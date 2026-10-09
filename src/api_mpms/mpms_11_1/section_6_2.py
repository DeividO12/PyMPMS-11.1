# api_mpms/mpms_11_1/section_6_2.py

import math
from typing import Optional

from api_mpms.constants.commodity_groups import (
    COMMODITY_TYPE_BOUNDS,
    OBSERVED_DENSITY_BOUNDS,
    resolve_commodity_group,
)
from api_mpms.constants.commodity_types import CommodityType
from api_mpms.constants.physical import T_BASE_F
from api_mpms.exceptions.convergence import MPMSConvergenceError
from api_mpms.exceptions.validation import MPMSRangeError
from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_1 import CTPL_DELTA, _correct_core
from api_mpms.results import ObservedToBaseResult
from api_mpms.validators.inputs import (
    validate_commodity_and_alpha,
    validate_density,
    validate_pressure_psig,
    validate_temperature_f,
)


# 15 evaluaciones de CTPL (m = 0 … 14), como el ejemplo 11.1.7.2-17 (pág. 116)
_MAX_ITER = 15
# |ρo − ρ60(m)·CTPL(m)| < 1e-6 kg/m³ (Paso 4)
_RHO_TOL = 1.0e-6


def _result(rho_60, f, iterations) -> ObservedToBaseResult:
    return ObservedToBaseResult(
        rho_60, f.ctl, f.fp, f.cpl, f.ctpl, api_round(f.ctpl, CTPL_DELTA), iterations
    )


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
        Densidad observada (kg/m³). Límites para A: 470.5–1201.8,
        B: 470.4–1209.5, D: 714.3–1208.3 (Paso 1).
    t_o : float
        Temperatura observada (°F, ITS-90), de −58.0 a 302.0.
    p_o : float
        Presión observada (psig), hasta 1500. Los valores negativos se toman como 0.
    commodity_type : {"A", "B", "C", "D"}, optional
        Obligatorio si no se da ``alpha_60``.
    alpha_60 : float, optional
        Coeficiente de expansión térmica a 60 °F (°F⁻¹) para el tipo C.

    Raises
    ------
    MPMSRangeError
        Entrada fuera de límites (Paso 1) o densidad base fuera de los límites
        del procedimiento (Paso 7).
    MPMSValidationError
        Entrada inválida.
    MPMSConvergenceError
        Sin convergencia en ``_MAX_ITER`` iteraciones. ``last_result`` contiene
        la última iteración, que la nota del Paso 6 permite usar marcada.
    """
    # Step 1 – check input values
    t_o = validate_temperature_f(t_o)
    p_o = validate_pressure_psig(p_o)
    rho_o = validate_density(rho_o, "rho_o")
    ct, alpha_60 = validate_commodity_and_alpha(commodity_type, alpha_60)

    if ct is CommodityType.SPECIAL_APPLICATIONS:
        rho_min, rho_max = 0.0, math.inf
    else:
        lo, hi = OBSERVED_DENSITY_BOUNDS[ct]
        if not (lo <= rho_o <= hi):
            raise MPMSRangeError(
                f"rho_o {rho_o} kg/m³ out of range for commodity type "
                f"{ct.value.upper()} ({lo} to {hi})"
            )
        rho_min, rho_max = COMMODITY_TYPE_BOUNDS[ct]

    # Step 2 – temperature shift (invariante durante la iteración)
    t_ipts68 = its90_to_ipts68(t_f_90=t_o)

    delta_t = t_o - T_BASE_F
    dp_factor = 7.93920 + 0.02326 * t_o

    # Initial guess
    rho_60 = max(min(rho_o, rho_max), rho_min)
    clamped = False

    for m in range(_MAX_ITER):
        # Step 3 – CTPL(m); el subgrupo (tipo B) se re-evalúa en cada iteración
        group = None if alpha_60 is not None else resolve_commodity_group(rho_60, ct)
        f = _correct_core(rho_60, t_ipts68, p_o, alpha_60, group)
        rho_eval = rho_60

        # Step 4 – convergence test
        if abs(rho_o - f.rho) < _RHO_TOL:
            return _result(rho_60, f, m)

        # Step 5 – Newton correction
        Da = 0.0 if group is None else group.Da

        E_m = (rho_o / (f.ctl * f.cpl)) - rho_60

        DT_m = Da * f.alpha_60 * delta_t * (1.0 + 1.6 * f.alpha_60 * delta_t)

        DP_m = -(
            2.0
            * f.cpl
            * p_o
            * f.fp
            * dp_factor
        ) / (rho_60**2)

        delta_rho_60 = E_m / (1.0 + DT_m + DP_m)

        # Enforce bounds
        rho_next = rho_60 + delta_rho_60
        rho_60 = max(min(rho_next, rho_max), rho_min)
        clamped = rho_60 != rho_next

    if clamped:
        # Step 7 – la densidad base buscada queda fuera de los límites
        raise MPMSRangeError(
            f"rho_60 out of the limits of the procedure for commodity type "
            f"{ct.value.upper()} ({rho_min} to {rho_max}): rho_o={rho_o}, t_o={t_o}, p_o={p_o}"
        )
    raise MPMSConvergenceError(
        f"API MPMS 11.1.6.2 did not converge within {_MAX_ITER} iterations "
        f"(rho_o={rho_o}, t_o={t_o}, p_o={p_o}, commodity_type={ct.value.upper()}, "
        f"alpha_60={alpha_60})",
        last_result=_result(rho_eval, f, _MAX_ITER - 1),
    )
