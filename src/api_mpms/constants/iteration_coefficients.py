# api_mpms/constants/iteration_coefficients.py

def da_coefficient(
    *,
    commodity_type: str,
    rho_60: float,
    alpha_given: bool,
) -> float:
    """
    API MPMS 11.1.6.2 – Table Da
    """

    if alpha_given:
        # Special applications (C)
        return 0.0

    commodity_type = commodity_type.lower()

    if commodity_type == "a":  # Crude Oil
        return 2.0

    if commodity_type == "d":  # Lubricating Oil
        return 1.0

    # Refined products (B)
    if 838.3127 <= rho_60 < 1163.5:
        return 1.3
    if 787.5195 <= rho_60 < 838.3127:
        return 2.0
    if 770.3520 <= rho_60 < 787.5195:
        return 8.5
    if 610.6 <= rho_60 < 770.3520:
        return 1.5

    # Special applications (C)
    return 0.0
