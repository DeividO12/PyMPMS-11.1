# api_mpms/exceptions/convergence.py

from typing import Optional


class MPMSConvergenceError(RuntimeError):
    """
    El procedimiento iterativo de 11.1.6.2 no convergió.

    Conserva la última iteración: la nota del Paso 6 (pág. 59) permite usarla
    para calcular CTPL siempre que el resultado se marque como no convergido.
    """

    def __init__(self, message: str, last_result: Optional[object] = None):
        super().__init__(message)
        self.last_result = last_result
