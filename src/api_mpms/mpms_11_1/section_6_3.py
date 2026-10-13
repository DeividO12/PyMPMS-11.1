# api_mpms/mpms_11_1/section_6_3.py

from typing import Optional

from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.results import ObservedToAlternateResult


def correct_observed_to_alternate(
    *,
    rho_o: float,
    t_o: float,
    p_o: float,
    t_f: float,
    p_psig: float,
    commodity_type: Optional[str] = None,
    alpha_60: Optional[float] = None,
) -> ObservedToAlternateResult:
    """
    API MPMS 11.1.6.3

    Corrige desde condiciones observadas (t_o °F, p_o psig) a condiciones
    alternas (t_f °F, p_psig psig) pasando por las condiciones base:

    1. 11.1.6.2 con las condiciones observadas → ρ60 y factores observados.
    2. 11.1.6.1 desde ρ60 a las condiciones alternas → factores alternos.

    Volúmenes: V60 = Vo · observed.ctpl_rounded y V = V60 / alternate.ctpl_rounded.
    """
    observed = correct_observed_to_base(
        rho_o=rho_o, t_o=t_o, p_o=p_o, commodity_type=commodity_type, alpha_60=alpha_60
    )
    alternate = correct_base_to_alternate(
        rho_60=observed.rho_60, t_f=t_f, p_psig=p_psig,
        commodity_type=commodity_type, alpha_60=alpha_60,
    )
    return ObservedToAlternateResult(observed, alternate)
