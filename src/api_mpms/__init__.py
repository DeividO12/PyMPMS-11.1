"""Implementación en Python de API MPMS Capítulo 11.1 (2004).

API pública:

- Procedimientos de corrección y resultados: este módulo (``api_mpms``).
- Conversión de unidades y redondeo: ``api_mpms.conversions``.
- Valores en formato de tabla (11.1.8): ``api_mpms.tables``.
"""

from api_mpms import conversions, tables

from api_mpms.constants.commodity_types import CommodityType
from api_mpms.exceptions.convergence import MPMSConvergenceError
from api_mpms.exceptions.validation import MPMSRangeError, MPMSValidationError
from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate, ctl_from_alpha
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.mpms_11_1.section_6_3 import correct_observed_to_alternate
from api_mpms.mpms_11_1.section_7_1 import correct_metric_base_to_alternate
from api_mpms.mpms_11_1.section_7_2 import correct_metric_observed_to_base
from api_mpms.results import (
    BaseToAlternateResult,
    MetricBaseToAlternateResult,
    MetricObservedToBaseResult,
    ObservedToAlternateResult,
    ObservedToBaseResult,
)

try:  # generado por setuptools-scm a partir del tag de git al instalar
    from api_mpms._version import __version__
except ImportError:  # pragma: no cover - código fuente sin instalar
    __version__ = "0+unknown"

__all__ = [
    "BaseToAlternateResult",
    "CommodityType",
    "MPMSConvergenceError",
    "MPMSRangeError",
    "MPMSValidationError",
    "MetricBaseToAlternateResult",
    "MetricObservedToBaseResult",
    "ObservedToAlternateResult",
    "ObservedToBaseResult",
    "api_round",
    "conversions",
    "correct_base_to_alternate",
    "correct_metric_base_to_alternate",
    "correct_metric_observed_to_base",
    "correct_observed_to_alternate",
    "correct_observed_to_base",
    "ctl_from_alpha",
    "its90_to_ipts68",
    "tables",
]
