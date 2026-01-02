from api_mpms.mpms_11_1.section_6_2 import correct_observed_to_base

"""
------------------------------Example 1 --------------------------------
Input data:
Commodity ................................ Generalized Crude Oil
t observed temperature, °F ..............   80.3
P observed pressure, pSI ................     -5
Dens, kg/m³, observed t & P .............  823.7

Output values:
density at 60°F ..............   832.048516184234
ctl ..........................     0.989966310837 
FP for psi ...................     0.567045450015
cpl ..........................     1.000000000000
ctpl .........................     0.989966310837
ctpl, round ..................            0.98997
"""

print("------------------------------Example 1 --------------------------------")
print(correct_observed_to_base(rho_o=823.7,t_o=80.3,p_o=-5, commodity_type='A'))

"""
------------------------------Example 2 --------------------------------
Input data:
Commodity ................................ Generalized Crude Oil
t observed temperature, °F ..............   -57.95
P observed pressure, pSI ................    113.5
Rel density, observed t & P  ............  0.72332

Calculation of Intermediate Results 
Density kg/m³ meter .............  722.608253120000

Output values:
density at 60°F ..............   663.445062852402
ctl ..........................     1.088429741690 
FP for psi ...................     0.603436540820
cpl ..........................     1.000685369884
ctpl .........................     1.089175718656
ctpl, round ..................            1.08918
"""

print("\n------------------------------Example 2 --------------------------------")
print(correct_observed_to_base(rho_o=722.60825312,t_o=-57.95,p_o=113.5, commodity_type='A'))

"""
------------------------------Example 5 --------------------------------
Input data:
Commodity ................................ Generalized Refined product
t observed temperature, °F ..............     25.3 
P observed pressure, pSI ................      267
Dens, kg/m³, observed t & P .............  803.141

Output values:
density at 60°F ..............   787.507922593917
ctl ..........................     1.018381017381
FP for psi ...................     0.539959363768
cpl ..........................     1.001443772976
ctpl .........................     1.019851328373
ctpl, round ..................            1.01985
"""

print("\n------------------------------Example 5 --------------------------------")
print(correct_observed_to_base(rho_o=803.141,t_o=25.3,p_o=267, commodity_type='B'))

"""
------------------------------Example 6 --------------------------------
Input data:
Commodity ................................ Generalized Refined product
t observed temperature, °F ..............      139
P observed pressure, pSI ................      100
Rel density, observed t & P  ............   0.7322

Calculation of Intermediate Results 
Density kg/m³ meter .............  731.479515200000

Output values:
density at 60°F ..............   770.349794252060
ctl ..........................     0.948677079691 
FP for psi ...................     0.910923457238
cpl ..........................     1.000911753995
ctpl .........................     0.949542039808
ctpl, round ..................            0.94954
"""

print("\n------------------------------Example 6 --------------------------------")
print(correct_observed_to_base(rho_o=731.4795152,t_o=139,p_o=100, commodity_type='B'))

"""
------------------------------Example 7 --------------------------------
Input data:
Commodity ............................... Specialized liquid
Alpha at 60'~ per 'F .................... 0.00057634
t observed temperature, °F ..............       84.5 
P observed pressure, pSI ................        573
Dens, kg/m³, observed t & P  ............      853.7

Output values:
density at 60°F ..............   863.403098613648
ctl ..........................     0.985817857839 
FP for psi ...................     0.519616156675
cpl ..........................     1.002986291965
ctpl .........................     0.988761797787
ctpl, round ..................            0.98876
"""

print("\n------------------------------Example 7 --------------------------------")
print(correct_observed_to_base(rho_o=853.7,t_o=84.5,p_o=573, alpha_60= 0.00057634, commodity_type='C'))
