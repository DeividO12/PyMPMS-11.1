# api_mpms/results.py

"""Resultados con nombre de los procedimientos de API MPMS 11.1.

Son ``NamedTuple``: se pueden leer por atributo (``res.ctl``) o desempaquetar.
Ningún valor intermedio se redondea; ``ctpl_rounded`` es el CTPL redondeado a
0.00001 que la norma exige como salida final (11.1.3.9, 11.1.5.4).
"""

from typing import NamedTuple


class BaseToAlternateResult(NamedTuple):
    """11.1.6.1: condiciones base (60 °F, 0 psig) → condiciones alternas."""

    rho: float           # Densidad a condiciones alternas (kg/m³)
    ctl: float
    fp: float            # Factor de compresibilidad escalado (psi⁻¹)
    cpl: float
    ctpl: float
    ctpl_rounded: float
    alpha_60: float      # Coeficiente de expansión térmica a 60 °F (°F⁻¹)


class ObservedToBaseResult(NamedTuple):
    """11.1.6.2: condiciones observadas → condiciones base (60 °F, 0 psig)."""

    rho_60: float        # Densidad base (kg/m³)
    ctl: float
    fp: float            # psi⁻¹
    cpl: float
    ctpl: float
    ctpl_rounded: float
    iterations: int      # Iteración m en la que converge (correcciones de Newton aplicadas)


class ObservedToAlternateResult(NamedTuple):
    """11.1.6.3: condiciones observadas → condiciones alternas (vía condiciones base)."""

    observed: ObservedToBaseResult     # Paso 1 (factores de observadas a base)
    alternate: BaseToAlternateResult   # Paso 2 (factores de base a alternas)


class MetricBaseToAlternateResult(NamedTuple):
    """11.1.7.1: densidad base métrica (15 °C o 20 °C) → condiciones alternas."""

    rho: float           # Densidad a condiciones alternas (kg/m³)
    rho_60: float        # Densidad base a 60 °F (kg/m³)
    ctl: float
    fp: float            # En la unidad de presión de entrada: kPa⁻¹ o bar⁻¹
    cpl: float
    ctpl: float
    ctpl_rounded: float


class MetricObservedToBaseResult(NamedTuple):
    """11.1.7.2: condiciones observadas métricas → base métrica (15 °C o 20 °C)."""

    rho_base: float      # Densidad a la temperatura base métrica (kg/m³)
    rho_60: float        # Densidad base a 60 °F (kg/m³)
    ctl: float
    fp: float            # En la unidad de presión de entrada: kPa⁻¹ o bar⁻¹
    cpl: float
    ctpl: float
    ctpl_rounded: float


__all__ = [
    "BaseToAlternateResult",
    "MetricBaseToAlternateResult",
    "MetricObservedToBaseResult",
    "ObservedToAlternateResult",
    "ObservedToBaseResult",
]
