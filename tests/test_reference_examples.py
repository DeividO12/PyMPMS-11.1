"""Ejemplos resueltos de API MPMS 11.1 (antes impresos en src/api_mpms/tests)."""

import pytest

from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base

ABS = 1e-9

# rho_60, t_f, p_psig, tipo, (CTL, Fp, CPL, CTPL)
BASE_TO_ALTERNATE = [
    pytest.param(946.918739324112, -27.7, 0, "A",
                 (1.033011591958, 0.305779891997, 1.0, 1.033011591958), id="6.1-ej1"),
    pytest.param(1163.463078189300, 301.93, 1500, "A",
                 (0.938051116886, 0.427958509999, 1.006460852301, 0.944111726603), id="6.1-ej2"),
    pytest.param(936.784387011266, 48.04, -7.3, "B",
                 (1.004858068990, 0.384339609206, 1.0, 1.004858068990), id="6.1-ej3"),
]


@pytest.mark.parametrize("rho_60,t_f,p,ct,expected", BASE_TO_ALTERNATE)
def test_base_to_alternate(rho_60, t_f, p, ct, expected):
    _, ctl, fp, cpl, ctpl, _ = correct_base_to_alternate(
        rho_60=rho_60, t_f=t_f, p_psig=p, commodity_type=ct
    )
    assert (ctl, fp, cpl, ctpl) == pytest.approx(expected, abs=ABS)


# rho_o, t_o, p_o, tipo, alpha_60, (rho_60, CTL, Fp, CPL, CTPL)
OBSERVED_TO_BASE = [
    pytest.param(823.7, 80.3, -5, "A", None,
                 (832.048516184234, 0.989966310837, 0.567045450015, 1.0, 0.989966310837),
                 id="6.2-ej1"),
    pytest.param(722.60825312, -57.95, 113.5, "A", None,
                 (663.445062852402, 1.088429741690, 0.603436540820, 1.000685369884, 1.089175718656),
                 id="6.2-ej2"),
    pytest.param(803.141, 25.3, 267, "B", None,
                 (787.507922593917, 1.018381017381, 0.539959363768, 1.001443772976, 1.019851328373),
                 id="6.2-ej5"),
    pytest.param(731.4795152, 139, 100, "B", None,
                 (770.349794252060, 0.948677079691, 0.910923457238, 1.000911753995, 0.949542039808),
                 id="6.2-ej6"),
    pytest.param(853.7, 84.5, 573, "C", 0.00057634,
                 (863.403098613648, 0.985817857839, 0.519616156675, 1.002986291965, 0.988761797787),
                 id="6.2-ej7"),
]


@pytest.mark.parametrize("rho_o,t_o,p_o,ct,alpha,expected", OBSERVED_TO_BASE)
def test_observed_to_base(rho_o, t_o, p_o, ct, alpha, expected):
    result = correct_observed_to_base(
        rho_o=rho_o, t_o=t_o, p_o=p_o, commodity_type=ct, alpha_60=alpha
    )
    assert tuple(result) == pytest.approx(expected, abs=ABS)
