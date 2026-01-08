from typing import Tuple
from api_mpms.mpms_11_1.section_5_1 import gamma_t_to_rho, rho_to_gamma_t
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate

def table_24x(
    *,
    rel_base: float,
    t_f_obs: float,
    commodity_type: str
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        CTL
    """
    rho_base = gamma_t_to_rho(rel_base)
    
    _, CTL, _, _, _, _ = correct_base_to_alternate(rho_60=rho_base, t_f=t_f_obs,p_psig=0,commodity_group=commodity_type)
    
    CTL = api_round(CTL, 0.00001)
    
    return CTL