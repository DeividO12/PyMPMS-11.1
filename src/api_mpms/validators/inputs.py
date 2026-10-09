# api_mpms/validators/inputs.py

import math
import numbers
from typing import Optional, Tuple, Union

from api_mpms.constants.commodity_types import CommodityType
from api_mpms.constants.physical import (
    ALPHA_60_MAX_F,
    ALPHA_60_MIN_F,
    METRIC_BASE_TEMPERATURES_C,
    P_MAX_PSIG,
    T_MAX_F,
    T_MIN_F,
)
from api_mpms.exceptions.validation import MPMSRangeError, MPMSValidationError


_COMMODITY_VALUES = frozenset(ct.value for ct in CommodityType)


def _as_finite_float(value, name: str) -> float:
    if type(value) is float:  # camino rápido: caso más común
        if not math.isfinite(value):
            raise MPMSValidationError(f"{name} must be finite, got {value!r}")
        return value
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise MPMSValidationError(f"{name} must be a number, got {value!r}")
    value = float(value)
    if not math.isfinite(value):
        raise MPMSValidationError(f"{name} must be finite, got {value!r}")
    return value


def validate_temperature_f(t: float) -> float:
    t = _as_finite_float(t, "Temperature")
    if not (T_MIN_F <= t <= T_MAX_F):
        raise MPMSRangeError(
            f"Temperature {t} °F out of range ({T_MIN_F:g} to {T_MAX_F:g})"
        )
    return t


def validate_pressure(p: float) -> float:
    """Presión numérica y finita (cualquier unidad); los límites se comprueban en psig."""
    return _as_finite_float(p, "Pressure")


def validate_metric_base_temperature(t_base_c: float) -> float:
    """Temperatura base métrica: solo 15 °C o 20 °C (11.1.3.1)."""
    t_base_c = _as_finite_float(t_base_c, "t_base_c")
    if t_base_c not in METRIC_BASE_TEMPERATURES_C:
        raise MPMSValidationError(f"t_base_c must be 15 or 20 °C, got {t_base_c}")
    return t_base_c


def validate_pressure_psig(p: float) -> float:
    """Valida la presión manométrica; los valores negativos se toman como 0 psig."""
    p = _as_finite_float(p, "Pressure")
    if p > P_MAX_PSIG:
        raise MPMSRangeError(
            f"Pressure {p} psig out of range (0–{P_MAX_PSIG:g})"
        )
    return max(p, 0.0)


# Holgura relativa para que los bordes en °C⁻¹ (414e-6, 1674e-6) sigan dentro tras dividir por 1.8
_ALPHA_REL_TOL = 1e-12


def validate_alpha_60(alpha_60: float) -> float:
    """Valida alpha_60 (°F⁻¹) contra los límites de 11.1.6.1 paso 1."""
    alpha_60 = _as_finite_float(alpha_60, "alpha_60")
    if not (
        ALPHA_60_MIN_F * (1 - _ALPHA_REL_TOL) <= alpha_60 <= ALPHA_60_MAX_F * (1 + _ALPHA_REL_TOL)
    ):
        raise MPMSRangeError(
            f"alpha_60 {alpha_60} °F⁻¹ out of range ({ALPHA_60_MIN_F:g} to {ALPHA_60_MAX_F:g})"
        )
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


def validate_commodity_and_alpha(
    commodity_type: Union[str, CommodityType, None],
    alpha_60: Optional[float],
) -> Tuple[CommodityType, Optional[float]]:
    """
    Tipo de producto y alpha_60 (°F⁻¹) de 11.1.6.1/11.1.6.2.

    La norma pide el grupo de producto *o* alpha_60, no ambos (págs. 39 y 55):
    con alpha_60 el tipo es C (y puede omitirse); con A, B o D no se admite alpha_60.
    """
    if alpha_60 is None:
        return validate_commodity_type(commodity_type), None
    alpha_60 = validate_alpha_60(alpha_60)
    if commodity_type is not None:
        ct = validate_commodity_type(commodity_type, alpha_60)
        if ct is not CommodityType.SPECIAL_APPLICATIONS:
            raise MPMSValidationError(
                "alpha_60 is only allowed for commodity type 'C' (special applications), "
                f"got commodity_type={commodity_type!r}"
            )
    return CommodityType.SPECIAL_APPLICATIONS, alpha_60
