# api_mpms/mpms_11_1/section_7_1.py

from typing import Optional

from api_mpms.mpms_11_1.section_5_1 import (
    alpha_c_to_alpha_f,
    celsius_to_fahrenheit,
    fp_from_psi,
    pressure_to_psig,
)
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_1 import CTPL_DELTA, correct_base_to_alternate
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.results import MetricBaseToAlternateResult
from api_mpms.validators.inputs import validate_metric_base_temperature, validate_pressure


def correct_metric_base_to_alternate(
    *,
    rho_base: float,
    t_base_c: float,
    t_c: float,
    p: float,
    pressure_unit: str,
    commodity_type: Optional[str] = None,
    alpha_60_c: Optional[float] = None,
) -> MetricBaseToAlternateResult:
    """
    API MPMS 11.1.7.1

    Corrige volumen y densidad desde la temperatura base métrica (15 °C o
    20 °C, presión 0) a una temperatura y presión alternas.

    Parameters
    ----------
    rho_base : float
        Densidad a la temperatura base métrica (kg/m³).
    t_base_c : {15, 20}
        Temperatura base (°C).
    t_c : float
        Temperatura alterna (°C, ITS-90), de −50.00 a 150.00.
    p : float
        Presión alterna manométrica en ``pressure_unit``. Negativa → 0.
    pressure_unit : {"kPa", "bar"}
        Unidad de ``p``; también fija la unidad de ``fp`` (kPa⁻¹ o bar⁻¹).
    commodity_type : {"A", "B", "C", "D"}, optional
        Obligatorio si no se da ``alpha_60_c``.
    alpha_60_c : float, optional
        Coeficiente de expansión térmica a 60 °F en °C⁻¹ (414e-6 a 1674e-6),
        para el tipo C.
    """
    # Step 1 – convertir a unidades del sistema inglés
    t_base_f = celsius_to_fahrenheit(validate_metric_base_temperature(t_base_c))
    t_f = celsius_to_fahrenheit(t_c)
    p_psig = pressure_to_psig(validate_pressure(p), pressure_unit)
    alpha_60 = alpha_c_to_alpha_f(alpha_60_c) if alpha_60_c is not None else None

    # Step 2 – densidad a 60 °F y CTL de la base métrica a 60 °F
    base = correct_observed_to_base(
        rho_o=rho_base, t_o=t_base_f, p_o=0, commodity_type=commodity_type, alpha_60=alpha_60
    )
    # Step 3 – de 60 °F a las condiciones alternas
    alt = correct_base_to_alternate(
        rho_60=base.rho_60, t_f=t_f, p_psig=p_psig,
        commodity_type=commodity_type, alpha_60=alpha_60,
    )

    # Step 4 – factores referidos a la base métrica
    ctl = alt.ctl / base.ctl
    ctpl = ctl * alt.cpl
    # Step 5 – densidad a condiciones alternas
    rho = ctl * alt.cpl * rho_base
    return MetricBaseToAlternateResult(
        rho, base.rho_60, ctl, fp_from_psi(alt.fp, pressure_unit), alt.cpl,
        ctpl, api_round(ctpl, CTPL_DELTA),
    )
