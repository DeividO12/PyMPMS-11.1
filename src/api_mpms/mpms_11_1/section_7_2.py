# api_mpms/mpms_11_1/section_7_2.py

from typing import Optional, Tuple
from api_mpms.mpms_11_1.section_5_1 import alpha_c_to_alpha_f, celsius_to_fahrenheit
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate

def correct_observed_to_base_C(
    *,
    rho_o: float,
    t_o_c: float,
    p_o: float,
    t_b: float = 20.0,
    commodity_type: Optional[str] = None,
    alpha_60_c: Optional[float] = None,
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        rho, rho_60, CTL, Fp_psi, CPL, CTPL
    """
    
    t_b_F = celsius_to_fahrenheit(t_b)
    t_o_f = celsius_to_fahrenheit(t_o_c)
    alpha_60_f = alpha_c_to_alpha_f(alpha_60_c) if alpha_60_c is not None else None
    
    rho_60, CTL_o, Fp_o, CPL_o, CTPL_o = correct_observed_to_base(rho_o=rho_o, t_o=t_o_f, p_o=p_o,commodity_type=commodity_type, alpha_60=alpha_60_f)
    rho, CTL_60, fp_60, CPL_60, CTPL_60, alpha_60 = correct_base_to_alternate(rho_60=rho_60, t_f=t_b_F, p_psig=0, commodity_type=commodity_type, alpha_60=alpha_60_f)
    
    CTL = CTL_o / CTL_60
    Fp_psi = Fp_o
    CPL = CPL_o
    CTPL = CTL * CPL
    
    return rho, rho_60, CTL, Fp_psi, CPL, CTPL