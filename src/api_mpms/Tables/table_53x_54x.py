from typing import Tuple
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_7_2 import correct_observed_to_base_C
from api_mpms.mpms_11_1.section_7_1 import correct_observed_to_alternate_C

def table_53x_54x(
    *,
    den_obs: float,
    t_c_obs: float,
    commodity_type: str
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        CTL
    """
    
    rho, _, _, _, _, _ = correct_observed_to_base_C(rho_o=den_obs, t_o_c=t_c_obs, p_o=0,t_b=15, commodity_type=commodity_type)
    rho = api_round(rho, 0.1)

    _, CTL, _, _, _ = correct_observed_to_alternate_C(rho_t=rho, t_a_c=t_c_obs, p_a=0, t_b=15,commodity_type=commodity_type)

    CTL = api_round(CTL, 0.00001)
    
    return CTL