# api_mpms/mpms_11_1/section_5_1.py

"""
API MPMS 11.1.5.1 – Conversión de unidades de temperatura, presión, factor de
expansión térmica y densidad.

Los valores de densidad relativa y gravedad API están en vacío.

    t_C      Temperatura (°C)
    API      Gravedad API (°API)
    rho      Densidad (kg/m³)
    gamma_t  Densidad relativa respecto al agua a 60 °F
    P        Presión manométrica (psig, kPa o bar)
    Fp       Factor de compresibilidad escalado (psi⁻¹, kPa⁻¹ o bar⁻¹)

Las constantes de conversión se usan con todos sus dígitos (11.1.3).
"""

from api_mpms.constants.physical import KPA_PER_PSI, BAR_PER_PSI, WATER_DENSITY_KGM3
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


def alpha_f_to_alpha_c(alpha_f: float) -> float:
    """Coeficiente de expansión térmica de °F⁻¹ a °C⁻¹."""
    return 1.8 * alpha_f


_KPA = "kpa"
_BAR = "bar"


def _pressure_factor(unit: str) -> float:
    unit_key = unit.strip().lower() if isinstance(unit, str) else unit
    if unit_key == _KPA:
        return KPA_PER_PSI
    if unit_key == _BAR:
        return BAR_PER_PSI
    raise MPMSValidationError(f"pressure_unit must be 'kPa' or 'bar', got {unit!r}")


def pressure_to_psig(p: float, unit: str) -> float:
    """Presión manométrica en kPa o bar → psig (P_psi = P_kPa / 6.894757 = P_bar / 0.06894757)."""
    return p / _pressure_factor(unit)


def fp_from_psi(fp_psi: float, unit: str) -> float:
    """Fp en psi⁻¹ → kPa⁻¹ o bar⁻¹ (Fp_kPa = Fp_psi / 6.894757; Fp_bar = Fp_psi / 0.06894757)."""
    return fp_psi / _pressure_factor(unit)
