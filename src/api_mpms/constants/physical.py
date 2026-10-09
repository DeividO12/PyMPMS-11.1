# api_mpms/constants/physical.py

"""Constantes físicas y límites de aplicación compartidos por toda la librería."""

# Densidad del agua a 60 °F (kg/m³) usada para °API y densidad relativa (11.1.5.1)
WATER_DENSITY_KGM3 = 999.016

# Conversión de presión (11.1.5.1)
KPA_PER_PSI = 6.894757
BAR_PER_PSI = 0.06894757

# Condiciones base (ITS-90)
T_BASE_F = 60.0

# Límites de aplicación de temperatura y presión (11.1.2.3)
T_MIN_F = -58.0
T_MAX_F = 302.0
P_MAX_PSIG = 1500.0

# Temperaturas base métricas aceptadas (11.1.3.1)
METRIC_BASE_TEMPERATURES_C = (15.0, 20.0)

# Límites del coeficiente de expansión térmica a 60 °F para el tipo C (°F⁻¹) (11.1.6.1 paso 1)
ALPHA_60_MIN_F = 230.0e-6
ALPHA_60_MAX_F = 930.0e-6
