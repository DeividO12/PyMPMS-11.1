# api_mpms/mpms_11_1/section_7_1.py

from typing import Optional, Tuple
from api_mpms.mpms_11_1.section_5_1 import celc_to_fahr
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate

def correct_observed_to_alternate_C(
    *,
    rho_t: float,
    t_a: float,
    p_a: float,
    t_b: Optional[int] = 20,
    commodity_type: str = None,
    alpha_60: Optional[float] = None,
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        rho_60, CTL, Fp_psi, CPL, CTPL
    """
    
    t_b_F = celc_to_fahr(t_b)
    
    rho_60, CTL_60, _, _, _ = correct_observed_to_base(rho_o=rho_t, t_o=t_b_F, p_o=0,commodity_type=commodity_type, alpha_60=alpha_60)
    CTL_a, fp_a, CPL_a, CTPL_a, alpha_60_a = correct_base_to_alternate(rho_60=rho_60, t_f=t_a, p_psig=p_a, commodity_group=commodity_type, alpha_60=alpha_60)
    
    CTL = CTL_a / CTL_60
    Fp_psi = fp_a
    CPL = CPL_a
    CTPL = CTL * CPL
    
    return rho_60, CTL, Fp_psi, CPL, CTPL