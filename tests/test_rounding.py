"""API MPMS 11.1.5.4 (auditoría N-01, N-02; NORM-04)."""

from decimal import ROUND_HALF_EVEN, Decimal

import pytest

from api_mpms.exceptions.validation import MPMSValidationError
from api_mpms.mpms_11_1.section_5_4 import api_round


@pytest.mark.parametrize("x,delta,expected", [
    # Ejemplos de la norma (pág. 38)
    (5.34, 0.05, 5.35),
    (-5.34, 0.05, -5.35),
    (10.05, 0.1, 10.0),
    # Empates en magnitudes grandes (N-01)
    (611.15, 0.1, 611.2),
    (1000.05, 0.1, 1000.0),
    (205.075, 0.05, 205.1),
    (0.800055, 0.00001, 0.80006),
    (0.15, 0.1, 0.2),
    (0.25, 0.1, 0.2),
    # Incrementos no decimales (N-02)
    (0.75, 0.25, 0.75),
    (12.5, 2.5, 12.5),
    (7, 5, 5),
    (1234.4, 5, 1235),
    # Alpha
    (0.00047005, 0.0000001, 0.0004700),
    (0.00047015, 0.0000001, 0.0004702),
    # Signo
    (-27.75, 0.05, -27.75),
    (-0.01, 0.1, 0.0),
])
def test_api_round(x, delta, expected):
    assert api_round(x, delta) == expected


def test_no_negative_zero():
    assert str(api_round(-0.01, 0.1)) == "0.0"


@pytest.mark.parametrize("delta,start,stop,scale", [
    (0.1, 6106, 11635, 10),          # densidad kg/m³ 610.65 … 1163.45
    (0.00001, 80000, 110000, 100000),  # CTL 0.800005 … 1.099995
])
def test_all_decimal_ties_match_half_even(delta, start, stop, scale):
    step = Decimal(str(delta))
    for i in range(start, stop):
        s = str(Decimal(i) / scale + step / 2)
        expected = float((Decimal(s) / step).to_integral_value(rounding=ROUND_HALF_EVEN) * step)
        assert api_round(float(s), delta) == expected, s


@pytest.mark.parametrize("x,delta", [
    (float("nan"), 0.1), (float("inf"), 0.1), (1.0, 0), (1.0, -0.1), (None, 0.1),
])
def test_invalid(x, delta):
    with pytest.raises(MPMSValidationError):
        api_round(x, delta)
