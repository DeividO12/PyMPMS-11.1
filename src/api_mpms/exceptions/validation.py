# api_mpms/exceptions/validation.py


class MPMSValidationError(ValueError):
    """Entrada inválida o fuera de los límites de API MPMS 11.1."""


class MPMSRangeError(MPMSValidationError):
    """Valor fuera de los límites del procedimiento (11.1.2.3; 11.1.6.x Paso 1 y Paso 7)."""
