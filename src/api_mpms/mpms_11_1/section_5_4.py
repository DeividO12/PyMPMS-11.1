# api_mpms/mpms_11_1/section_5_4.py

"""
API MPMS 11.1.5.4 – Redondeo de valores.

Incrementos de redondeo δ (Paso 1):

    Variable                            | Unidades          | δ
    ------------------------------------|-------------------|-----------
    Densidad                            | °API              | 0.1
                                        | Densidad relativa | 0.0001
                                        | kg/m³             | 0.1
    Temperatura                         | °F                | 0.1
                                        | °C                | 0.05
    Presión                             | psig              | 1
                                        | kPa (manométrica) | 5
                                        | bar (manométrica) | 0.05
    Coef. de expansión térmica (α60)    | °F⁻¹              | 0.0000001
                                        | °C⁻¹              | 0.0000002
    CTL, CPL, CTPL                      | -                 | 0.00001
    Factor de compresibilidad (Fp)      | psi⁻¹             | 0.001
                                        | kPa⁻¹             | 0.0001
                                        | bar⁻¹             | 0.01

Según 11.1.3.9 solo se redondea el CTPL final; las entradas se redondean
únicamente al generar tablas y los valores intermedios nunca.
"""

import math
from decimal import ROUND_HALF_EVEN, Decimal
from functools import lru_cache
from typing import Optional, Tuple

from api_mpms.exceptions.validation import MPMSValidationError

# Fuera de esta distancia a un empate (y con |x|/δ acotado) el cálculo en
# coma flotante da el mismo entero que la aritmética decimal exacta.
_TIE_MARGIN = 1e-6
_FAST_MAX_Y = 1e9


@lru_cache(maxsize=64)
def _parse_delta(delta: float) -> Tuple[Decimal, Optional[int]]:
    """δ como Decimal y, si 1/δ es entero (0.1, 0.05, 0.00001…), ese entero."""
    d = Decimal(repr(delta))
    if not d.is_finite() or d <= 0:
        raise MPMSValidationError(f"Rounding increment must be > 0, got {delta!r}")
    inv = 1 / d
    return d, int(inv) if inv == inv.to_integral_value() else None


def api_round(x: float, delta: float) -> float:
    """
    Pasos 2 a 4 de 11.1.5.4: redondea ``x`` al múltiplo de ``delta`` más cercano.

    Los empates (parte decimal de |x|/δ exactamente 0.5) se resuelven al entero
    par. El valor se interpreta como el decimal que representa (``repr``), igual
    que en el ejemplo de la norma: 10.05 °F con δ = 0.1 da Y = 100.5 exacto → 10.0.
    Cerca de un empate se usa aritmética decimal para que el error binario de
    |x|/δ no lo oculte.
    """
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise MPMSValidationError(f"Cannot round {x!r}")
    if isinstance(delta, bool) or not isinstance(delta, (int, float)):
        raise MPMSValidationError(f"Rounding increment must be > 0, got {delta!r}")
    d, inv = _parse_delta(delta)

    # Paso 2 – normalizar
    ax = abs(float(x))
    y = ax / delta
    frac = y - math.floor(y)
    if inv is not None and y < _FAST_MAX_Y and abs(frac - 0.5) > _TIE_MARGIN:
        # Paso 3 – entero más cercano (sin empate posible); Paso 4 – reescalar
        x_round = math.floor(y + 0.5) / inv
    else:
        # Paso 3 exacto en decimal (empates al par); Paso 4 – reescalar
        i = (Decimal(repr(ax)) / d).to_integral_value(rounding=ROUND_HALF_EVEN)
        x_round = float(i * d)
    return -x_round if x < 0 and x_round else x_round
