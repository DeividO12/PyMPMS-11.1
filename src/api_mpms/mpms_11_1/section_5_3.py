# api_mpms/mpms_11_1/section_5_3.py

from typing import Optional
from api_mpms.exceptions.validation import MPMSValidationError


# API MPMS 11.1 – Table 5.3
_A_COEFFICIENTS = (
    -0.148759,
    -0.267408,
    1.080760,
    1.269056,
    -4.089591,
    -1.871251,
    7.438081,
    -3.536296,
)

def its90_to_ipts68(
    *,
    t_f_90: Optional[float] = None,
    t_c_90: Optional[float] = None,
) -> float:
    """
    API MPMS 11.1.5.3

    Convert temperature from ITS-90 to IPTS-68.

    Parameters
    ----------
    t_f_90 : float, optional
        Temperature in °F (ITS-90 basis). Mutually exclusive with ``t_c_90``.
    t_c_90 : float, optional
        Temperature in °C (ITS-90 basis). Mutually exclusive with ``t_f_90``.
    Returns
    -------
    float
        Temperature converted to IPTS-68, in the same unit as the input
        (°F if ``t_f_90`` was given, °C if ``t_c_90`` was given).
    """

    if (t_f_90 is None) == (t_c_90 is None):
        raise MPMSValidationError(
            "Exactly one of t_f_90 or t_c_90 must be provided"
        )

    # Convert input to Celsius if needed
    input_fahrenheit = t_f_90 is not None
    if t_f_90 is not None:
        t_c = (t_f_90 - 32.0) / 1.8
    else:
        assert t_c_90 is not None
        t_c = t_c_90

    # Step 1 – scaled temperature
    tau = t_c / 630.0

    # Step 2 – polynomial evaluation (Horner method)
    delta_t = _A_COEFFICIENTS[-1]
    for coeff in reversed(_A_COEFFICIENTS[:-1]):
        delta_t = coeff + delta_t * tau

    delta_t *= tau

    # Step 3 – corrected temperature
    t_c_68 = t_c - delta_t

    if input_fahrenheit:
        return 1.8 * t_c_68 + 32.0

    return t_c_68
