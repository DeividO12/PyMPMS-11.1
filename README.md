# PyMPMS-11.1

**PyMPMS-11.1** is a Python implementation of **API MPMS Chapter 11.1**, focused on accurate petroleum measurement calculations. The library provides validated algorithms for density and volume correction under temperature and pressure variations, following the normative procedures and examples defined by API.

---

## Scope

This project implements the following sections of API MPMS 11.1:

* **11.1.5.3** – Temperature conversion from ITS-90 to IPTS-68
* **11.1.6.1** – Correct volume and density from base conditions (60 °F, 0 psig) to observed conditions
* **11.1.6.2** – Correct volume and density from observed conditions to base conditions using iterative methods

The implementation strictly follows the mathematical formulations, coefficients, iteration limits, and convergence criteria defined by the standard.

---

## Key Features

* Accurate calculation of **CTL**, **CPL**, **CTPL**, and **Fp**
* Iterative solution for base density (ρ₆₀) per API MPMS 11.1.6.2
* Automatic commodity group resolution based on density ranges
* Support for Crude Oil, Refined Products, and Lubricating Oils
* Strict input validation and convergence error handling
* Modular, testable, and extensible architecture

---

## Project Structure

```
api_mpms/
│
├── mpms_11_1/
│   ├── section_5_3.py   # ITS-90 → IPTS-68 temperature conversion
│   ├── section_6_1.py   # Base → observed correction
│   └── section_6_2.py   # Observed → base correction (iterative)
│
├── constants/
│   ├── commodity_groups.py
│   └── iteration_coefficients.py
│
├── validators/
│   └── inputs.py
│
├── exceptions/
│   ├── validation.py
│   └── convergence.py
│
└── tests/
    ├── test_6_1/
    └── test_6_2/
```

---

## Installation

Currently, the project is private and intended for internal or controlled use.

```bash
pip install pympms-11-1
```

*(PyPI publication planned once validation is complete.)*

---

## Usage Examples

### Convert observed density to base conditions (API MPMS 11.1.6.2)

```python
from mpms_11_1.section_6_2 import correct_observed_to_base

rho_60, CTL, Fp, CPL, CTPL = correct_observed_to_base(
    rho_o=823.7,
    t_o=80.3,
    p_o=-5,          # Negative pressure forced to zero
    commodity_type="a"  # Crude Oil
)
```

---

## Testing

Normative examples from API MPMS 11.1 are implemented as automated tests.

```bash
pytest
```

Each test validates numerical convergence and tolerance against published API examples.

---

## Design Principles

* **Normative fidelity over optimization**
* **Explicit units and validation**
* **Deterministic iteration and convergence control**
* **Separation of constants, logic, and validation**

---

## Disclaimer

This library is an independent implementation of API MPMS 11.1.
It is **not affiliated with or endorsed by the American Petroleum Institute (API)**.

Users are responsible for validating results against official standards and regulatory requirements before operational use.

---

## License

License to be defined prior to public release.

---

## Roadmap

* Full coverage of API MPMS 11.1 tables
* Unit handling via `pint`
* PyPI public release
* Performance benchmarking

---

## Author

Developed as part of a metrology-focused backend for petroleum measurement systems.