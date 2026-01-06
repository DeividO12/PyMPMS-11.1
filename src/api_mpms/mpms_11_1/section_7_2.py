# api_mpms/mpms_11_1/section_7_1.py

from typing import Optional, Tuple
from api_mpms.mpms_11_1.section_5_1 import celc_to_fahr
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate

def correct_observed_to_base_C(
    *,
    rho_o: float,
    t_o: float,
    p_o: float,
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
    
    rho_60, CTL_o, Fp_o, CPL_o, CTPL_o = correct_observed_to_base(rho_o=rho_o, t_o=t_o, p_o=p_o,commodity_type=commodity_type, alpha_60=alpha_60)
    CTL_60, fp_60, CPL_60, CTPL_60, alpha_60 = correct_base_to_alternate(rho_60=rho_60, t_f=t_b_F, p_psig=0, commodity_group=commodity_type, alpha_60=alpha_60)
    
    CTL = CTL_o / CTL_60
    Fp_psi = Fp_o
    CPL = CPL_o
    CTPL = CTL * CPL
    
    return rho_60, CTL, Fp_psi, CPL, CTPL

print(correct_observed_to_base_C(rho_o=853.7, t_o=84.524, p_o=57.2899088394, t_b=15,commodity_type='C', alpha_60=0.0005763))