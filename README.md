# PyMPMS-11.1

**PyMPMS-11.1** is a Python implementation of **API MPMS Chapter 11.1 (2004)** — temperature and pressure volume correction factors for generalized crude oils, refined products and lubricating oils.

The calculation engine reproduces the worked examples of the standard (sections 11.1.5–11.1.7) and the values printed in its sample tables (section 11.1.8). Both are part of the automated test suite.

---

## Scope

| Section | Procedure | Function |
|---|---|---|
| 11.1.5.1 | Unit conversions (API, relative density, °C/°F, kPa/bar/psi, α, Fp) | `api_mpms.mpms_11_1.section_5_1` |
| 11.1.5.3 | ITS-90 → IPTS-68 temperature conversion | `its90_to_ipts68` |
| 11.1.5.4 | Rounding of values | `api_round` |
| 11.1.6.1 | Base (60 °F, 0 psig) → alternate conditions | `correct_base_to_alternate` |
| 11.1.6.2 | Observed → base conditions (iterative) | `correct_observed_to_base` |
| 11.1.6.3 | Observed → alternate conditions | `correct_observed_to_alternate` |
| 11.1.7.1 | Metric base (15 °C / 20 °C) → alternate conditions | `correct_metric_base_to_alternate` |
| 11.1.7.2 | Metric observed → metric base (15 °C / 20 °C) | `correct_metric_observed_to_base` |
| 11.1.8 | Tables 5, 6, 23, 24, 53, 54, 59, 60 (A/B/D) and 6C, 24C, 54C, 60C | `api_mpms.mpms_11_1.tables` |

Not implemented: 11.1.5.2 (α60 from measured data) and the compressibility tables 11.2.1 / 11.2.1M.

---

## Installation

The project is private and intended for internal use. From a clone of the repository:

```bash
pip install .              # library
pip install ".[tables]"    # + numpy/pandas for the table generator
pip install -e ".[dev]"    # development (pytest, hypothesis, ruff, mypy)
```

The distribution is named `pympms-11-1`; the import package is `api_mpms`.

---

## Usage

```python
from api_mpms import correct_observed_to_base, correct_metric_observed_to_base

# 11.1.6.2 – observed density (kg/m³), °F, psig  →  base conditions
res = correct_observed_to_base(rho_o=823.7, t_o=80.3, p_o=-5, commodity_type="A")
res.rho_60          # 832.0485161842337
res.ctpl_rounded    # 0.98997  (final VCF, rounded per 11.1.5.4)

# 11.1.7.2 – metric observed conditions → 15 °C (pressure in kPa or bar)
res = correct_metric_observed_to_base(
    rho_o=721.1, t_o_c=82.35, p_o=10005, pressure_unit="kPa",
    t_base_c=15, commodity_type="B",
)
res.rho_base, res.ctpl_rounded, res.fp   # fp in kPa⁻¹
```

Special applications (type C) use the thermal expansion coefficient instead of a commodity group:

```python
correct_observed_to_base(rho_o=853.7, t_o=84.5, p_o=573, alpha_60=0.00057634)
```

Results are `NamedTuple`s: fields can be read by name (`res.ctl`) or unpacked.

### Units and limits

| Input | Unit | Limits (11.1.2.3) |
|---|---|---|
| Temperature | °F (6.x) / °C (7.x), ITS-90 | −58.0 to 302.0 °F (−50 to 150 °C) |
| Pressure | psig (6.x) / kPa or bar (7.x) | 0 to 1500 psig; negative values are set to 0 |
| Base density ρ60 | kg/m³ | A, B: 610.6–1163.5; D: 800.9–1163.5 |
| Observed density ρo | kg/m³ | A: 470.5–1201.8; B: 470.4–1209.5; D: 714.3–1208.3 |
| α60 (type C) | °F⁻¹ (°C⁻¹ in 7.x) | 230.0–930.0 ×10⁻⁶ °F⁻¹ |

### Errors

| Exception | Meaning |
|---|---|
| `MPMSRangeError` | An input (or the resulting base density) is outside the limits of the procedure. Subclass of `MPMSValidationError`. |
| `MPMSValidationError` | Invalid input: wrong type, NaN, unknown commodity type, α60 combined with A/B/D… |
| `MPMSConvergenceError` | 11.1.6.2 did not converge in 15 iterations. `err.last_result` holds the last iteration, which the standard allows to be used if flagged (11.1.6.2, Step 6 note). |

### Rounding

Following 11.1.3.9, intermediate values are never rounded. Each procedure returns the unrounded factors plus `ctpl_rounded` (0.00001). Inputs are rounded only by the table functions in `api_mpms.mpms_11_1.tables`.

---

## Tables

`api_mpms.mpms_11_1.tables` provides one function per table of section 11.1.8 (rounded input and output). For example, `table_5x`, `table_6x`, `table_54x` and `table_6c_24c`.

`ctl_from_observed_api`, `ctl_from_observed_relative_density`, `ctl_from_observed_density_15c` and `ctl_from_observed_density_20c` return the CTL obtained directly from an observed density by 11.1.6.2 / 11.1.7.2. They do not round the intermediate base density, as 11.1.3.9 requires.

Full tables can be generated as CSV (temperature in rows):

```bash
python scripts/generate_tables.py --list
python scripts/generate_tables.py 5A 6A 54C --out-dir tablas --workers 8
```

---

## Testing

```bash
pytest
```

The suite includes:

- 105 worked examples of the standard (11.1.5.3, 11.1.5.4, 11.1.6.1–11.1.6.3, 11.1.7.1–11.1.7.2), including the out-of-range cases;
- 253 values from the sample tables of section 11.1.8;
- edge-case validation and rounding tests.

---

## Project Structure

```
src/api_mpms/
├── __init__.py            # public API
├── results.py             # NamedTuple results
├── constants/             # commodity groups, commodity types, physical constants
├── exceptions/            # MPMSValidationError, MPMSRangeError, MPMSConvergenceError
├── validators/            # input validation
└── mpms_11_1/
    ├── section_5_1.py … section_7_2.py
    └── tables.py
scripts/generate_tables.py # CSV table generator
tests/                     # pytest suite and normative data
docs/                      # audit reports
```

---

## Disclaimer

This library is an independent implementation of API MPMS 11.1. It is **not affiliated with or endorsed by the American Petroleum Institute (API)**. Users are responsible for validating results against the official standard and regulatory requirements before operational use.

## License

Proprietary — © 2026 SYZ Colombia SAS. See [LICENSE](LICENSE).

## Author

Developed as part of a metrology-focused backend for petroleum measurement systems.
