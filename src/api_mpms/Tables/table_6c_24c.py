from typing import Tuple
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate

def table_6c_24c(
    *,
    alpha_obs: float,
    t_f_obs: float,
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        CTL
    """
    commodity_type = 'C'
    
    _, CTL, _, _, _, _ = correct_base_to_alternate(rho_60=0, t_f=t_f_obs,p_psig=0,commodity_group=commodity_type, alpha_60=alpha_obs)

    CTL = api_round(CTL, 0.00001)
    
    return CTL