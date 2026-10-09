# api_mpms/results.py

"""Resultados con nombre de los procedimientos de API MPMS 11.1.

Son ``NamedTuple``: se pueden leer por atributo (``res.ctl``) o desempaquetar.
"""

from typing import NamedTuple


class BaseToAlternateResult(NamedTuple):
    """Corrección desde condiciones base a condiciones alternas (11.1.6.1)."""

    rho: float       # Densidad a condiciones alternas (kg/m³)
    ctl: float
    fp: float        # Factor de compresibilidad escalado (psi⁻¹)
    cpl: float
    ctpl: float
    alpha_60: float  # Coeficiente de expansión térmica a 60 °F (°F⁻¹)


class ObservedToBaseResult(NamedTuple):
    """Corrección desde condiciones observadas a condiciones base (11.1.6.2)."""

    rho_60: float    # Densidad base a 60 °F y 0 psig (kg/m³)
    ctl: float
    fp: float
    cpl: float
    ctpl: float
