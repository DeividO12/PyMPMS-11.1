"""
Ejemplos resueltos de API MPMS 11.1 (2004), secciones 11.1.5 a 11.1.7 y 11.1.8.23-24.

La norma exige coincidir al menos 8 cifras significativas (11.1.5, págs. 29-30)
y los valores redondeados deben ser exactos.
"""

import json
from pathlib import Path

import pytest

from api_mpms.exceptions.validation import MPMSRangeError
from api_mpms.mpms_11_1 import tables
from api_mpms.mpms_11_1.section_5_3 import its90_to_ipts68
from api_mpms.mpms_11_1.section_5_4 import api_round
from api_mpms.mpms_11_1.section_6_1 import correct_base_to_alternate, ctl_from_alpha
from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base
from api_mpms.mpms_11_1.section_6_3 import correct_observed_to_alternate
from api_mpms.mpms_11_1.section_7_1 import correct_metric_base_to_alternate
from api_mpms.mpms_11_1.section_7_2 import correct_metric_observed_to_base

EXAMPLES = json.loads(
    (Path(__file__).parent / "data" / "norm_core_examples.json").read_text(encoding="utf8")
)


def _alpha_c(i):
    if i.get("alpha_60_per_C") is not None:
        return i["alpha_60_per_C"]
    if i.get("alpha_60_per_F") is not None:
        return 1.8 * i["alpha_60_per_F"]
    return None


def _ct(i):
    return None if i.get("commodity") == "C" else i.get("commodity")


def _run(ex):
    """Ejecuta el ejemplo y devuelve {clave_esperada: valor_calculado}."""
    s, i = ex["section"], ex["inputs"]
    if s == "11.1.6.1":
        r = correct_base_to_alternate(rho_60=i["rho_60"], t_f=i["t_f"], p_psig=i["p_psig"],
                                      commodity_type=_ct(i), alpha_60=i.get("alpha_60"))
        return {**r._asdict(), "t_star": its90_to_ipts68(t_f_90=i["t_f"])}
    if s == "11.1.6.2":
        return correct_observed_to_base(rho_o=i["rho_o"], t_o=i["t_f"], p_o=i["p_psig"],
                                        commodity_type=_ct(i), alpha_60=i.get("alpha_60"))._asdict()
    if s == "11.1.6.3":
        r = correct_observed_to_alternate(
            rho_o=i["rho_o"], t_o=i["t_o_f"], p_o=i["p_o_psig"], t_f=i["t_f"], p_psig=i["p_psig"],
            commodity_type=_ct(i), alpha_60=i.get("alpha_60"))
        o, a = r.observed, r.alternate
        return {"rho_60": o.rho_60, "ctl_o": o.ctl, "fp_o": o.fp, "cpl_o": o.cpl, "ctpl_o": o.ctpl,
                "ctpl_o_rounded": o.ctpl_rounded, "ctl": a.ctl, "fp": a.fp, "cpl": a.cpl,
                "ctpl": a.ctpl, "ctpl_rounded": a.ctpl_rounded, "rho": a.rho}
    if s == "11.1.7.1":
        r = correct_metric_base_to_alternate(
            rho_base=i["rho_T"], t_base_c=i["T_base_c"], t_c=i["t_c"], p=i["p"],
            pressure_unit=i["p_unit"], commodity_type=_ct(i), alpha_60_c=_alpha_c(i))
        out = {**r._asdict(), "fp_kpa": r.fp, "fp_bar": r.fp}
        # NORM-28: los ejemplos imprimen ρ = ρT · CTPL redondeado
        out["rho"] = i["rho_T"] * r.ctpl_rounded
        return out
    if s == "11.1.7.2":
        r = correct_metric_observed_to_base(
            rho_o=i["rho_o"], t_o_c=i["t_o_c"], p_o=i["p_o"], pressure_unit=i["p_unit"],
            t_base_c=i["T_base_c"], commodity_type=_ct(i), alpha_60_c=_alpha_c(i))
        return {**r._asdict(), "rho_T": r.rho_base, "fp_kpa": r.fp, "fp_bar": r.fp}
    if s.startswith("11.1.5.2/") or s == "11.1.5.3":
        return {"t_f_68": its90_to_ipts68(t_f_90=i["t_f_90"])}
    if s == "11.1.5.4":
        return {"x_round": api_round(i["x"], i["delta"])}
    if s.startswith("11.1.8.23"):
        return {"ctl_rounded": api_round(ctl_from_alpha(alpha_60=i["alpha_60"], t_f=i["t_f"]), 0.00001)}
    if s.startswith("11.1.8.24"):
        return {"ctl_rounded": tables.table_54c(alpha_obs=i["alpha_60_per_C"], t_c_obs=i["t_c"])}
    raise AssertionError(f"Sección sin ejecutor: {s}")


# Claves esperadas que el resultado no expone (intermedios o volúmenes derivados)
_SKIP = {"rho_star", "delta_t", "volume_base", "volume_alt", "T_f", "t_f", "t_o_f", "p_psi",
         "ctl_60", "ctl_star", "ctpl_star", "fp_psi"}
# 7.2: el número de iteraciones es el de 11.1.6.2 interno, no se expone
_SKIP_BY_SECTION = {"11.1.7.2": {"iterations"}}


@pytest.mark.parametrize("ex", EXAMPLES, ids=[e["id"] for e in EXAMPLES])
def test_norm_example(ex):
    if ex["expected"].get("error"):
        with pytest.raises(MPMSRangeError):
            _run(ex)
        return

    got = _run(ex)
    tol = ex.get("tolerance") or {}
    skip = _SKIP | _SKIP_BY_SECTION.get(ex["section"], set())
    checked = 0
    for key, expected in ex["expected"].items():
        if key in skip or (key.startswith("fp_") and key not in got):
            continue
        assert key in got, f"{ex['id']}: no se calcula '{key}'"
        if key.endswith("_rounded") or key in ("iterations", "x_round"):
            assert got[key] == expected, key
        else:
            approx = pytest.approx(expected, rel=tol.get("rel", 1e-8), abs=tol.get("abs", 0))
            assert got[key] == approx, key
        checked += 1
    assert checked, f"{ex['id']}: ninguna magnitud comparada"
