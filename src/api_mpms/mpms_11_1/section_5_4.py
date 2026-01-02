import math

"""
NORMA API MPMS 11.1.5.4 - PROCEDIMIENTO DE REDONDEO
--------------------------------------------------
Este script implementa el algoritmo de redondeo para variables de entrada
y calculadas según los estándares de la industria petrolera.

TABLA DE UNIDADES Y INCREMENTOS DE REDONDEO (Step 1):
Variable Type                       | Units             | Increment (δ)
------------------------------------|-------------------|--------------
Density                             | °API              | 0.1
                                    | Relative Density  | 0.0001
                                    | kg/m³             | 0.1
Temperature                         | °F                | 0.1
                                    | °C                | 0.05
Pressure                            | psig              | 1
                                    | kPa (gauge)       | 5
                                    | bar (gauge)       | 0.05
Thermal Expansion Coeff (α₆₀)       | °F⁻¹              | 0.0000001 (0.1x10⁻⁶)
                                    | °C⁻¹              | 0.0000002 (0.2x10⁻⁶)
CTL                                 | -                 | 0.00001
Scaled Compressibility Factor (Fp)  | psi⁻¹             | 0.001
                                    | kPa⁻¹             | 0.0001
                                    | bar⁻¹             | 0.01
CPL                                 | -                 | 0.00001
CTPL                                | -                 | 0.00001
"""

def api_round(x, delta):
    """
    Implementa los pasos 2 al 4 de la norma API MPMS 11.1.5.4.
    
    Args:
        x (float): El valor a redondear.
        delta (float): El incremento de redondeo (δ) según la tabla.
        
    Returns:
        float: El valor redondeado.
    """
    
    # Step 2: Normalizar la variable de entrada
    # Y = |X| / δ
    y = abs(x) / delta
    
    # Step 3: Encontrar el entero más cercano (I)
    # Si la parte decimal no es exactamente 0.5, usar trunc(Y + 0.5)
    # Si es exactamente 0.5, redondear al par más cercano.
    
    decimal_part = y - math.floor(y)
    trunc_y = math.floor(y) # trunc(Y) para valores positivos es floor
    
    # Verificación de 0.5 (usamos una tolerancia pequeña para errores de punto flotante)
    if not math.isclose(decimal_part, 0.5, rel_tol=1e-12):
        # Caso estándar
        i = math.floor(y + 0.5)
    else:
        # Caso exacto 0.5: Regla del Par (Banker's Rounding)
        if trunc_y % 2 != 0:
            # Si es impar, sumamos 1 para que sea par
            i = trunc_y + 1
        else:
            # Si es par, se queda como está
            i = trunc_y
            
    # Step 4: Reescalar el entero y mantener el signo original
    # X_round = ±δ * I
    signo = 1 if x >= 0 else -1
    x_round = signo * delta * i
    
    # --- LIMPIEZA DE PRECISIÓN ---
    # Determinamos la cantidad de decimales en delta para redondear el resultado final
    # Ejemplo: si delta es 0.05, redondeamos a 2 decimales.
    if delta < 1:
        precision = abs(int(math.log10(delta)))
        # Si delta es algo como 0.05 o 0.0000002, sumamos un dígito extra por seguridad
        return round(x_round, precision + 1)
    return round(x_round, 0)