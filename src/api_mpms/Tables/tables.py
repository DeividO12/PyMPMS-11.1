from typing import Tuple
from api_mpms.mpms_11_1.section_5_1 import API_to_rho, rho_to_API, gamma_t_to_rho, rho_to_gamma_t
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.mpms_11_1.section_7_1 import correct_observed_to_alternate_C
from api_mpms.mpms_11_1.section_7_2 import correct_observed_to_base_C

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

def table_5x_6x(
    *,
    api_obs: float,
    t_f_obs: float,
    commodity_type: str
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        CTL
    """
    rho_obs = API_to_rho(api_obs)
    
    rho_60, _, _, _, _ = correct_observed_to_base(rho_o=rho_obs, t_o=t_f_obs, p_o=0, commodity_type=commodity_type)
    
    api_60 = api_round(rho_to_API(rho_60), 0.1)
    
    _, CTL, _, _, _, _ = correct_base_to_alternate(rho_60=API_to_rho(api_60), t_f=t_f_obs,p_psig=0,commodity_group=commodity_type)

    CTL = api_round(CTL, 0.00001)
    
    return CTL

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

def table_23x_24x(
    *,
    rel_obs: float,
    t_f_obs: float,
    commodity_type: str
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        CTL
    """
    rho_obs = gamma_t_to_rho(rel_obs)
    
    rho_60, _, _, _, _ = correct_observed_to_base(rho_o=rho_obs, t_o=t_f_obs, p_o=0, commodity_type=commodity_type)
    
    rel_60 = api_round(rho_to_gamma_t(rho_60), 0.0001)
    
    _, CTL, _, _, _, _ = correct_base_to_alternate(rho_60=gamma_t_to_rho(rel_60), t_f=t_f_obs,p_psig=0,commodity_group=commodity_type)

    CTL = api_round(CTL, 0.00001)
    
    return CTL

def table_54x(
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

    _, CTL, _, _, _ = correct_observed_to_alternate_C(rho_t=den_base, t_a_c=t_c_obs, p_a=0, t_b=15,commodity_type=commodity_type)

    CTL = api_round(CTL, 0.00001)
    
    return CTL

def table_54c(
    *,
    alpa_obs: float,
    t_c_obs: float,
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        CTL
    """
    commodity_type = 'C'

    _, CTL, _, _, _ = correct_observed_to_alternate_C(rho_t=0, t_a_c=t_c_obs, p_a=0, t_b=15,commodity_type=commodity_type, alpha_60_c=alpa_obs)

    CTL = api_round(CTL, 0.00001)
    
    return CTL

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

def table_60c(
    *,
    alpa_obs: float,
    t_c_obs: float,
) -> Tuple[float, float, float, float, float]:
    """
    API MPMS 11.1.6.2

    Returns:
        CTL
    """
    commodity_type = 'C'

    _, CTL, _, _, _ = correct_observed_to_alternate_C(rho_t=0, t_a_c=t_c_obs, p_a=0, t_b=20,commodity_type=commodity_type, alpha_60_c=alpa_obs)

    CTL = api_round(CTL, 0.00001)
    
    return CTL

def table_59x_60x(
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
    
    rho, _, _, _, _, _ = correct_observed_to_base_C(rho_o=den_obs, t_o_c=t_c_obs, p_o=0,t_b=20, commodity_type=commodity_type)
    rho = api_round(rho, 0.1)

    _, CTL, _, _, _ = correct_observed_to_alternate_C(rho_t=rho, t_a_c=t_c_obs, p_a=0, t_b=20,commodity_type=commodity_type)

    CTL = api_round(CTL, 0.00001)
    
    return CTL