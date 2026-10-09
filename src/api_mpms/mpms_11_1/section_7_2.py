# api_mpms/mpms_11_1/section_7_2.py

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
from api_mpms.results import MetricObservedToBaseResult
from api_mpms.validators.inputs import validate_metric_base_temperature, validate_pressure


def correct_metric_observed_to_base(
    *,
    rho_o: float,
    t_o_c: float,
    p_o: float,
    pressure_unit: str,
    t_base_c: float,
    commodity_type: Optional[str] = None,
    alpha_60_c: Optional[float] = None,
) -> MetricObservedToBaseResult:
    """
    API MPMS 11.1.7.2

    Corrige volumen y densidad desde condiciones observadas métricas a la
    temperatura base métrica (15 °C o 20 °C, presión 0).

    Parameters
    ----------
    rho_o : float
        Densidad observada (kg/m³).
    t_o_c : float
        Temperatura observada (°C, ITS-90), de −50.00 a 150.00.
    p_o : float
        Presión observada manométrica en ``pressure_unit``. Negativa → 0.
    pressure_unit : {"kPa", "bar"}
        Unidad de ``p_o``; también fija la unidad de ``fp`` (kPa⁻¹ o bar⁻¹).
    t_base_c : {15, 20}
        Temperatura base (°C).
    commodity_type : {"A", "B", "C", "D"}, optional
        Obligatorio si no se da ``alpha_60_c``.
    alpha_60_c : float, optional
        Coeficiente de expansión térmica a 60 °F en °C⁻¹ (414e-6 a 1674e-6),
        para el tipo C.
    """
    # Step 1 – convertir a unidades del sistema inglés
    t_base_f = celsius_to_fahrenheit(validate_metric_base_temperature(t_base_c))
    t_o_f = celsius_to_fahrenheit(t_o_c)
    p_psig = pressure_to_psig(validate_pressure(p_o), pressure_unit)
    alpha_60 = alpha_c_to_alpha_f(alpha_60_c) if alpha_60_c is not None else None

    # Step 2 – de condiciones observadas a 60 °F
    obs = correct_observed_to_base(
        rho_o=rho_o, t_o=t_o_f, p_o=p_psig, commodity_type=commodity_type, alpha_60=alpha_60
    )
    # Step 3 – de 60 °F a la temperatura base métrica
    base = correct_base_to_alternate(
        rho_60=obs.rho_60, t_f=t_base_f, p_psig=0,
        commodity_type=commodity_type, alpha_60=alpha_60,
    )

    # Step 4 – factores referidos a la base métrica
    ctl = obs.ctl / base.ctl
    ctpl = ctl * obs.cpl
    return MetricObservedToBaseResult(
        base.rho, obs.rho_60, ctl, fp_from_psi(obs.fp, pressure_unit), obs.cpl,
        ctpl, api_round(ctpl, CTPL_DELTA),
    )
