from typing import Tuple
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_7_1 import correct_observed_to_alternate_C

def table_60x(
    *,
    den_base: float,
    t_c_obs: float,
    commodity_type: str
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        CTL
    """

    _, CTL, _, _, _ = correct_observed_to_alternate_C(rho_t=den_base, t_a_c=t_c_obs, p_a=0, t_b=20,commodity_type=commodity_type)

    CTL = api_round(CTL, 0.00001)
    
    return CTL