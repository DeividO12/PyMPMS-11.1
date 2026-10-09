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

from api_mpms.exceptions.validation import MPMSValidationError


def api_round(x: float, delta: float) -> float:
    """
    Pasos 2 a 4 de 11.1.5.4: redondea ``x`` al múltiplo de ``delta`` más cercano.

    Los empates (parte decimal de |x|/δ exactamente 0.5) se resuelven al entero
    par. El valor se interpreta como el decimal que representa (``repr``), igual
    que en el ejemplo de la norma: 10.05 °F con δ = 0.1 da Y = 100.5 exacto → 10.0.
    La aritmética decimal evita que el error binario de |x|/δ oculte los empates.
    """
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise MPMSValidationError(f"Cannot round {x!r}")
    d = Decimal(repr(delta))
    if not d.is_finite() or d <= 0:
        raise MPMSValidationError(f"Rounding increment must be > 0, got {delta!r}")

    # Paso 2 – normalizar; Paso 3 – entero más cercano (empates al par)
    i = (Decimal(repr(abs(float(x)))) / d).to_integral_value(rounding=ROUND_HALF_EVEN)
    # Paso 4 – reescalar y conservar el signo
    x_round = float(i * d)
    return -x_round if x < 0 and x_round else x_round
