# api_mpms/validators/inputs.py

from api_mpms.exceptions.validation import MPMSValidationError


def validate_temperature_f(t: float):
    if not (-58.0 <= t <= 302.0):
        raise MPMSValidationError(
            f"Temperature {t} °F out of range (-58 to 302)"
        )


def validate_pressure_psig(P: float) -> float:
    if P < 0:
        return 0.0
    if P > 1500:
        raise MPMSValidationError(
            f"Pressure {P} psig out of range (0–1500)"
        )
    return P
