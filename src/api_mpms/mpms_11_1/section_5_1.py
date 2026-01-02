# Informacion tomada de la norma API MPMS 11.1
# 11.1.5.1  Method to Convert Units of Temperature, Pressure, Thermal Expansion Factor, and Density-Related Values

"""
Esquema de Cálculos

Este procedimiento acepta los valores de densidad, temperatura y presión en las unidades en que se ingresan y los convierte a
las unidades requeridas por el procedimiento de cálculo.

Los valores de densidad relativa y gravedad AF'I están en vacuo.

Valores posibles de entrada y salida

t_C = (t°C)                     Valor de temperatura (°C)
P_kpa = (Pₖₚₐ)                  Valor de presión (kpa (manómetro))
G = (API)                       API gravity (°API)
rho = (ρ)                       Valor de densidad (kg/m3)
gamma_t = (γₜ)                  Valor de densidad relativa basado en el agua a la temperatura T
"""
def rho_to_API(rho:float):
    API = (141.5 / (rho/999.016))-131.5
    return API
    
def API_to_rho(API:float):
    rho = (141.5*999.016)/(API + 131.5)
    return rho

def gamma_t_to_rho(gamma_t:float):
    rho = gamma_t *  999.016
    return rho

def rho_to_gamma_t(rho: float):
    gamma_t = rho/999.016
    return gamma_t