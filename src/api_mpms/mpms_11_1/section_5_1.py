# api_mpms/mpms_11_1/section_5_1.py

"""
API MPMS 11.1.5.1 – Conversión de unidades de temperatura, presión, factor de
expansión térmica y densidad.

Los valores de densidad relativa y gravedad API están en vacío.

    t_C      Temperatura (°C)
    API      Gravedad API (°API)
    rho      Densidad (kg/m³)
    gamma_t  Densidad relativa respecto al agua a 60 °F
"""

from api_mpms.constants.physical import WATER_DENSITY_KGM3
from api_mpms.exceptions.validation import MPMSValidationError


def rho_to_api(rho: float) -> float:
    if rho <= 0:
        raise MPMSValidationError(f"Density must be > 0 kg/m³, got {rho}")
    return (141.5 / (rho / WATER_DENSITY_KGM3)) - 131.5


def api_to_rho(api: float) -> float:
    if api <= -131.5:
        raise MPMSValidationError(f"API gravity must be > -131.5, got {api}")
    return (141.5 * WATER_DENSITY_KGM3) / (api + 131.5)


def gamma_t_to_rho(gamma_t: float) -> float:
    if gamma_t <= 0:
        raise MPMSValidationError(f"Relative density must be > 0, got {gamma_t}")
    return gamma_t * WATER_DENSITY_KGM3


def rho_to_gamma_t(rho: float) -> float:
    if rho <= 0:
        raise MPMSValidationError(f"Density must be > 0 kg/m³, got {rho}")
    return rho / WATER_DENSITY_KGM3


def celsius_to_fahrenheit(t_c: float) -> float:
    return (1.8 * t_c) + 32


def alpha_c_to_alpha_f(alpha_c: float) -> float:
    """Coeficiente de expansión térmica de °C⁻¹ a °F⁻¹."""
    return alpha_c / 1.8
