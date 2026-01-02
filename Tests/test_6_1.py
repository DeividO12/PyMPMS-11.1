from mpms_11_1.section_6_1 import correct_base_to_alternate

"""
------------------------------Example 1 --------------------------------
Input data:
Commodity ................................ Generalized Crude Oil
t observed temperature, °F ..............   -27.7
P observed pressure, pSI ................       0
Base API grabity ........................  17.785

Calculation of Intermediate Results 
Density kg/cu meter (Rho60) .... 946.918739324112 

Output values:
ctl ..........................     1.033011591958
FP for psi ...................     0.305779891997
cpl ..........................     1.000000000000
ctpl .........................     1.033011591958
ctpl, round ..................            1.03301
"""

print("------------------------------Example 1 --------------------------------")
print(correct_base_to_alternate(rho_60=946.918739324112,t_f=-27.7, p_psig=0, commodity_group='A'))

"""
------------------------------Example 2 --------------------------------
Input data:
Commodity ................................ Generalized Crude Oil
t observed temperature, °F ..............   301.93
P observed pressure, pSI ................     1500
Base API grabity ........................      -10

Calculation of Intermediate Results 
Density kg/cu meter (Rho60) .... 1163.463078189300

Output values:
ctl ..........................     0.938051116886
FP for psi ...................     0.427958509999
cpl ..........................     1.006460852301
ctpl .........................     0.944111726603
ctpl, round ..................            0.94411
"""

print("\n------------------------------Example 2 --------------------------------")
print(correct_base_to_alternate(rho_60=1163.463078189300,t_f=301.93, p_psig=1500, commodity_group='A'))

"""
------------------------------Example 3 --------------------------------
Input data:
Commodity ................................ Generalized Refined product
t observed temperature, °F ..............   48.04 
P observed pressure, pSI ................    -7.3
Base API grabity ........................    19.4

Calculation of Intermediate Results 
Density kg/cu meter (Rho60) .... 936.784387011266

Output values:
ctl ..........................     1.004858068990
FP for psi ...................     0.384339609206
cpl ..........................     1.000000000000
ctpl .........................     1.004858068990
ctpl, round ..................            1.00486
"""

print("\n------------------------------Example 3 --------------------------------")
print(correct_base_to_alternate(rho_60=936.784387011266,t_f=48.04, p_psig=-7.3, commodity_group='B'))

print("\n------------------------------Example 4 --------------------------------")
print(correct_base_to_alternate(rho_60=936.784387011266,t_f=48.04, p_psig=0, commodity_group='A'))