# api_mpms/constants/commodity_groups.py

from dataclasses import dataclass
from typing import Dict, Tuple

from api_mpms.constants.commodity_types import CommodityType
from api_mpms.exceptions.validation import MPMSRangeError


@dataclass(frozen=True)
class CommodityGroup:
    id: int
    name: str
    rho_min: float
    rho_max: float
    K0: float
    K1: float
    K2: float
    Da: float  # Coeficiente de la iteración 11.1.6.2 (Tabla Da)


COMMODITY_GROUPS = {
    1: CommodityGroup(1, "Crude Oil", 610.6, 1163.5, 341.0957, 0.0, 0.0, 2.0),
    2: CommodityGroup(2, "Fuel Oils", 838.3127, 1163.5, 103.8720, 0.2701, 0.0, 1.3),
    3: CommodityGroup(3, "Jet Fuels", 787.5195, 838.3127, 330.3010, 0.0, 0.0, 2.0),
    4: CommodityGroup(4, "Transition Zone", 770.3520, 787.5195, 1489.067, 0.0, -0.00186840, 8.5),
    5: CommodityGroup(5, "Gasolines", 610.6, 770.3520, 192.4571, 0.2438, 0.0, 1.5),
    6: CommodityGroup(6, "Lubricating Oil", 800.9, 1163.5, 0.0, 0.34878, 0.0, 1.0),
}

COMMODITY_TYPE_GROUPS: Dict[CommodityType, Tuple[CommodityGroup, ...]] = {
    CommodityType.CRUDE_OIL: (COMMODITY_GROUPS[1],),
    CommodityType.REFINED_PRODUCTS: tuple(
        sorted((COMMODITY_GROUPS[i] for i in (2, 3, 4, 5)), key=lambda g: g.rho_min)
    ),
    CommodityType.LUBRICATING_OILS: (COMMODITY_GROUPS[6],),
}

# Límites de densidad base por tipo de producto (kg/m³)
COMMODITY_TYPE_BOUNDS: Dict[CommodityType, Tuple[float, float]] = {
    ct: (min(g.rho_min for g in groups), max(g.rho_max for g in groups))
    for ct, groups in COMMODITY_TYPE_GROUPS.items()
}


# Límites de densidad observada por tipo (11.1.6.2 Paso 1, pág. 57)
OBSERVED_DENSITY_BOUNDS: Dict[CommodityType, Tuple[float, float]] = {
    CommodityType.CRUDE_OIL: (470.5, 1201.8),
    CommodityType.REFINED_PRODUCTS: (470.4, 1209.5),
    CommodityType.LUBRICATING_OILS: (714.3, 1208.3),
}


def resolve_commodity_group(rho: float, commodity_type: CommodityType) -> CommodityGroup:
    """
    Subgrupo de producto según la densidad base (tablas K y Da, págs. 41 y 58).

    Los intervalos son [min, max), salvo el extremo superior del tipo
    (1163.5 kg/m³: fuel oils, crudo, lubricantes), que es inclusivo.
    Fuera del rango del tipo lanza MPMSRangeError: la norma no extrapola.
    """
    groups = COMMODITY_TYPE_GROUPS[commodity_type]
    for g in groups:
        if g.rho_min <= rho < g.rho_max:
            return g
    if rho == groups[-1].rho_max:
        return groups[-1]
    rho_min, rho_max = COMMODITY_TYPE_BOUNDS[commodity_type]
    raise MPMSRangeError(
        f"rho_60 {rho} kg/m3 out of range for commodity type "
        f"{commodity_type.value.upper()} ({rho_min} to {rho_max} kg/m3)"
    )
