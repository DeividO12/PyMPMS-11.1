# api_mpms/validators/inputs.py

import math
import numbers
from typing import Optional, Union

from api_mpms.constants.commodity_types import CommodityType
from api_mpms.constants.physical import P_MAX_PSIG, T_MAX_F, T_MIN_F
from api_mpms.exceptions.validation import MPMSValidationError


_COMMODITY_VALUES = frozenset(ct.value for ct in CommodityType)


def _as_finite_float(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise MPMSValidationError(f"{name} must be a number, got {value!r}")
    value = float(value)
    if not math.isfinite(value):
        raise MPMSValidationError(f"{name} must be finite, got {value!r}")
    return value


def validate_temperature_f(t: float) -> float:
    t = _as_finite_float(t, "Temperature")
    if not (T_MIN_F <= t <= T_MAX_F):
        raise MPMSValidationError(
            f"Temperature {t} °F out of range ({T_MIN_F:g} to {T_MAX_F:g})"
        )
    return t


def validate_pressure_psig(p: float) -> float:
    """Valida la presión manométrica; los valores negativos se toman como 0 psig."""
    p = _as_finite_float(p, "Pressure")
    if p > P_MAX_PSIG:
        raise MPMSValidationError(
            f"Pressure {p} psig out of range (0–{P_MAX_PSIG:g})"
        )
    return max(p, 0.0)


def validate_alpha_60(alpha_60: float) -> float:
    alpha_60 = _as_finite_float(alpha_60, "alpha_60")
    if alpha_60 <= 0:
        raise MPMSValidationError(f"alpha_60 must be > 0, got {alpha_60}")
    return alpha_60


def validate_density(rho: float, name: str = "Density") -> float:
    rho = _as_finite_float(rho, name)
    if rho <= 0:
        raise MPMSValidationError(f"{name} must be > 0 kg/m³, got {rho}")
    return rho


def validate_commodity_type(
    commodity_type: Union[str, CommodityType, None],
    alpha_60: Optional[float] = None,
) -> CommodityType:
    """
    Normaliza el tipo de producto (A, B, C, D; sin distinguir mayúsculas).

    El tipo C (aplicaciones especiales) requiere alpha_60.
    """
    if isinstance(commodity_type, CommodityType):
        ct = commodity_type
    elif isinstance(commodity_type, str) and commodity_type.strip().lower() in _COMMODITY_VALUES:
        ct = CommodityType(commodity_type.strip().lower())
    else:
        raise MPMSValidationError(
            f"commodity_type must be 'A', 'B', 'C' or 'D', got {commodity_type!r}"
        )

    if ct is CommodityType.SPECIAL_APPLICATIONS and alpha_60 is None:
        raise MPMSValidationError("commodity_type 'C' requires alpha_60")
    return ct
