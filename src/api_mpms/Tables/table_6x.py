from typing import Tuple
from api_mpms.mpms_11_1.section_5_1 import API_to_rho
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate

def table_6x(
    *,
    api_base: float,
    t_f_obs: float,
    commodity_type: str
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        CTL
    """
    
    rho_base = API_to_rho(api_base)
    
    _, CTL, _, _, _, _ = correct_base_to_alternate(rho_60=rho_base, t_f=t_f_obs,p_psig=0,commodity_group=commodity_type)
    CTL = api_round(CTL, 0.00001)
    
    return CTL