from exceptions.convergence import MPMSConvergenceError
from mpms_11_1.section_5_1 import API_to_rho, rho_to_API, gamma_t_to_rho, rho_to_gamma_t
from mpms_11_1.section_5_4 import api_round
from mpms_11_1.section_6_1 import correct_base_to_alternate
from mpms_11_1.section_6_2 import correct_observed_to_base

import math
import pandas as pd
import numpy as np
from typing import Optional, Tuple

def generar_tabla_5a():
    # Paso 1: Presión fija a 0 psig
    p_o = 0.0
    commodity_group = "A" # Generalized Crude Oils
    
    # Paso 2 y 3: Rangos de API y Temperatura
    # Nota: Usamos incrementos de 0.1 y redondeamos cada paso según 11.1.5.4
    api_range = np.arange(-13.4, 169, 0.1) # rango: -13.4 a 168.9
    temp_range = np.arange(-58.0, 302.1, 0.1) # rango: -58.0 a 302.0

    results = []

    for api_obs_raw in api_range:
        # Asegurar redondeo consistente en la entrada
        api_obs = api_round(api_obs_raw, 0.1)
        
        row = {"API_Obs": api_obs}
        
        for t_obs_raw in temp_range:
            t_obs = api_round(t_obs_raw, 0.1)
            
            # Paso 4: Convertir API a kg/m³
            rho_o = API_to_rho(api_obs)
            
            # Paso 5: Determinar densidad base (rho_60)
            # Usar tu función: correct_observed_to_base
            try:
                rho_60, _, _, _, _ = correct_observed_to_base(
                    rho_o=rho_o, t_o=t_obs, p_o=p_o, commodity_type=commodity_group
                )
                # Paso 6: Convertir de vuelta a API y redondear
                api_60_raw = rho_to_API(rho_60)
                api_60 = api_round(api_60_raw, 0.1)
            except:
                api_60 = '-'
            
            row[f"T_{t_obs}"] = api_60
            
        results.append(row)

    # Crear DataFrame
    df = pd.DataFrame(results).set_index("API_Obs")
    
    # Guardar en formato CSV (excelente para lectura rápida)
    df.to_csv("Tabla_5A.csv")
    print("Tabla 5A generada exitosamente en 'Tabla_5A.csv'")
    return df

def generar_tabla_5b():
    # Paso 1: Presión fija a 0 psig
    p_o = 0.0
    commodity_group = "B" #  Generalized Products
    
    # Paso 2 y 3: Rangos de API y Temperatura
    # Nota: Usamos incrementos de 0.1 y redondeamos cada paso según 11.1.5.4
    api_range = np.arange(-14.2, 169, 0.1) # rango: -14.2 a 168.9
    temp_range = np.arange(-58.0, 302.1, 0.1) # rango: -58.0 a 302.0

    results = []

    for api_obs_raw in api_range:
        # Asegurar redondeo consistente en la entrada
        api_obs = api_round(api_obs_raw, 0.1)
        
        row = {"API_Obs": api_obs}
        
        for t_obs_raw in temp_range:
            t_obs = api_round(t_obs_raw, 0.1)
            
            # Paso 4: Convertir API a kg/m³
            rho_o = API_to_rho(api_obs)
            
            # Paso 5: Determinar densidad base (rho_60)
            # Usar tu función: correct_observed_to_base
            try:
                rho_60, _, _, _, _ = correct_observed_to_base(
                    rho_o=rho_o, t_o=t_obs, p_o=p_o, commodity_type=commodity_group
                )
                # Paso 6: Convertir de vuelta a API y redondear
                api_60_raw = rho_to_API(rho_60)
                api_60 = api_round(api_60_raw, 0.1)
            except:
                api_60 = '-'
            
            row[f"T_{t_obs}"] = api_60
            
        results.append(row)

    # Crear DataFrame
    df = pd.DataFrame(results).set_index("API_Obs")
    
    # Guardar en formato CSV (excelente para lectura rápida)
    df.to_csv("Tabla_5B.csv")
    print("Tabla 5B generada exitosamente en 'Tabla_5B.csv'")
    return df

def generar_tabla_5d():
    # Paso 1: Presión fija a 0 psig
    p_o = 0.0
    commodity_group = "D" #  Generalized Lubricating Oils
    
    # Paso 2 y 3: Rangos de API y Temperatura
    # Nota: Usamos incrementos de 0.1 y redondeamos cada paso según 11.1.5.4
    api_range = np.arange(-14.1, 66.4, 0.1) # rango: -14.1 a 66.3
    temp_range = np.arange(-58.0, 302.1, 0.1) # rango: -58.0 a 302.0

    results = []

    for api_obs_raw in api_range:
        # Asegurar redondeo consistente en la entrada
        api_obs = api_round(api_obs_raw, 0.1)
        
        row = {"API_Obs": api_obs}
        
        for t_obs_raw in temp_range:
            t_obs = api_round(t_obs_raw, 0.1)
            
            # Paso 4: Convertir API a kg/m³
            rho_o = API_to_rho(api_obs)
            
            # Paso 5: Determinar densidad base (rho_60)
            # Usar tu función: correct_observed_to_base
            try:
                rho_60, _, _, _, _ = correct_observed_to_base(
                    rho_o=rho_o, t_o=t_obs, p_o=p_o, commodity_type=commodity_group
                )
                # Paso 6: Convertir de vuelta a API y redondear
                api_60_raw = rho_to_API(rho_60)
                api_60 = api_round(api_60_raw, 0.1)
            except MPMSConvergenceError:
                api_60 = '-'
            
            row[f"T_{t_obs}"] = api_60
            
        results.append(row)

    # Crear DataFrame
    df = pd.DataFrame(results).set_index("API_Obs")
    
    # Guardar en formato CSV (excelente para lectura rápida)
    df.to_csv("Tabla_5D.csv")
    print("Tabla 5D generada exitosamente en 'Tabla_5D.csv'")
    return df

def generar_tabla_6a():
    # Paso 1: Presión fija a 0 psig
    p_o = 0.0
    commodity_group = "A" #  Generalized Crude Oils and Products
    
    # Paso 2 y 3: Rangos de API y Temperatura
    # Nota: Usamos incrementos de 0.1 y redondeamos cada paso según 11.1.5.4
    api_range = np.arange(-10, 100.1, 0.1) # rango: -10 a 100
    temp_range = np.arange(-58.0, 302.1, 0.1) # rango: -58.0 a 302.0

    results = []

    for api_60_raw in api_range:
        # Asegurar redondeo consistente en la entrada
        api_60 = api_round(api_60_raw, 0.1)
        
        row = {"API_60°F": api_60}
        
        for t_obs_raw in temp_range:
            t_obs = api_round(t_obs_raw, 0.1)
            
            # Paso 4: Convertir API a kg/m³
            rho_60 = API_to_rho(api_60)
            
            # Paso 5: Determinar densidad base (rho_60)
            # Usar tu función: correct_observed_to_base
            try:
                CTL_60, _, _, _, _ = correct_base_to_alternate(
                    rho_60=rho_60, t_f=t_obs, p_psig=p_o, commodity_group=commodity_group
                )
                CTL_60 = api_round(CTL_60, 0.00001)
            except Exception as e:
                print(e)
                CTL_60 = '-'
            
            row[f"T_{t_obs}"] = CTL_60
            
        results.append(row)

    # Crear DataFrame
    df = pd.DataFrame(results).set_index("API_60°F")
    
    # Guardar en formato CSV (excelente para lectura rápida)
    df.to_csv("Tabla_6A.csv")
    print("Tabla 6A generada exitosamente en 'Tabla_6A.csv'")
    return df

def generar_tabla_6b():
    # Paso 1: Presión fija a 0 psig
    p_o = 0.0
    commodity_group = "B" #  Generalized Crude Oils and Products
    
    # Paso 2 y 3: Rangos de API y Temperatura
    # Nota: Usamos incrementos de 0.1 y redondeamos cada paso según 11.1.5.4
    api_range = np.arange(-10, 100.1, 0.1) # rango: -10 a 100
    temp_range = np.arange(-58.0, 302.1, 0.1) # rango: -58.0 a 302.0

    results = []

    for api_60_raw in api_range:
        # Asegurar redondeo consistente en la entrada
        api_60 = api_round(api_60_raw, 0.1)
        
        row = {"API_60°F": api_60}
        
        for t_obs_raw in temp_range:
            t_obs = api_round(t_obs_raw, 0.1)
            
            # Paso 4: Convertir API a kg/m³
            rho_60 = API_to_rho(api_60)
            
            # Paso 5: Determinar densidad base (rho_60)
            # Usar tu función: correct_observed_to_base
            try:
                CTL_60, _, _, _, _ = correct_base_to_alternate(
                    rho_60=rho_60, t_f=t_obs, p_psig=p_o, commodity_group=commodity_group
                )
                CTL_60 = api_round(CTL_60, 0.00001)
            except:
                CTL_60 = '-'
            
            row[f"T_{t_obs}"] = CTL_60
            
        results.append(row)

    # Crear DataFrame
    df = pd.DataFrame(results).set_index("API_60°F")
    
    # Guardar en formato CSV (excelente para lectura rápida)
    df.to_csv("Tabla_6B.csv")
    print("Tabla 6B generada exitosamente en 'Tabla_6B.csv'")
    return df

def generar_tabla_6d():
    # Paso 1: Presión fija a 0 psig
    p_o = 0.0
    commodity_group = "D" #  Generalized Crude Oils and Products
    
    # Paso 2 y 3: Rangos de API y Temperatura
    # Nota: Usamos incrementos de 0.1 y redondeamos cada paso según 11.1.5.4
    api_range = np.arange(-10, 45.1, 0.1) # rango: -10 a 45
    temp_range = np.arange(-58.0, 302.1, 0.1) # rango: -58.0 a 302.0

    results = []

    for api_60_raw in api_range:
        # Asegurar redondeo consistente en la entrada
        api_60 = api_round(api_60_raw, 0.1)
        
        row = {"API_60°F": api_60}
        
        for t_obs_raw in temp_range:
            t_obs = api_round(t_obs_raw, 0.1)
            
            # Paso 4: Convertir API a kg/m³
            rho_60 = API_to_rho(api_60)
            
            # Paso 5: Determinar densidad base (rho_60)
            # Usar tu función: correct_observed_to_base
            try:
                CTL_60, _, _, _, _ = correct_base_to_alternate(
                    rho_60=rho_60, t_f=t_obs, p_psig=p_o, commodity_group=commodity_group
                )
                CTL_60 = api_round(CTL_60, 0.00001)
            except:
                CTL_60 = '-'
            
            row[f"T_{t_obs}"] = CTL_60
            
        results.append(row)

    # Crear DataFrame
    df = pd.DataFrame(results).set_index("API_60°F")
    
    # Guardar en formato CSV (excelente para lectura rápida)
    df.to_csv("Tabla_6D.csv")
    print("Tabla 6D generada exitosamente en 'Tabla_6D.csv'")
    return df

def generar_tabla_23a():
    # Paso 1: Presión fija a 0 psig
    p_o = 0.0
    commodity_group = "A" # Generalized Crude Oils
    
    # Paso 2 y 3: Rangos de densidad relativa y Temperatura
    # Nota: Usamos incrementos de 0.1 y redondeamos cada paso según 11.1.5.4
    rel_range = np.arange(0.4710, 1.199, 0.0001) # rango: 0.4710 a 1.1989
    temp_range = np.arange(-58.0, 302.1, 0.1) # rango: -58.0 a 302.0

    results = []

    for rel_obs_raw in rel_range:
        # Asegurar redondeo consistente en la entrada
        rel_obs = api_round(rel_obs_raw, 0.0001)
        
        row = {"Rel_Obs": rel_obs}
        
        for t_obs_raw in temp_range:
            t_obs = api_round(t_obs_raw, 0.1)
            
            # Paso 4: Convertir γ densidad relativa a kg/m³
            rho_o = gamma_t_to_rho(t_obs_raw)
            
            # Paso 5: Determinar densidad base (rho_60)
            # Usar tu función: correct_observed_to_base
            try:
                rho_60, _, _, _, _ = correct_observed_to_base(
                    rho_o=rho_o, t_o=t_obs, p_o=p_o, commodity_type=commodity_group
                )
                # Paso 6: Convertir de vuelta a API y redondear
                gamma_60_raw = rho_to_gamma_t(rho_60)
                gamma_60 = api_round(gamma_60_raw, 0.0001)
            except:
                gamma_60 = '-'
            
            row[f"T_{t_obs}"] = gamma_60
            
        results.append(row)

    # Crear DataFrame
    df = pd.DataFrame(results).set_index("Rel_Obs")
    
    # Guardar en formato CSV (excelente para lectura rápida)
    df.to_csv("Tabla_23A.csv")
    print("Tabla 23A generada exitosamente en 'Tabla_23A.csv'")
    return df