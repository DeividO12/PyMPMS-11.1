# api_mpms/constants/commodity_groups.py

from dataclasses import dataclass
from exceptions.validation import MPMSValidationError


@dataclass(frozen=True)
class CommodityGroup:
    id: int
    name: str
    rho_min: float
    rho_max: float
    K0: float
    K1: float
    K2: float


COMMODITY_GROUPS = {
    1: CommodityGroup(1, "Crude Oil", 610.6, 1163.5, 341.0957, 0.0, 0.0),
    2: CommodityGroup(2, "Fuel Oils", 838.3127, 1163.5, 103.8720, 0.2701, 0.0),
    3: CommodityGroup(3, "Jet Fuels", 787.5195, 838.3127, 330.3010, 0.0, 0.0),
    4: CommodityGroup(4, "Transition Zone", 770.3520, 787.5195, 1489.067, 0.0, -0.00186840),
    5: CommodityGroup(5, "Gasolines", 610.6, 770.3520, 192.4571, 0.2438, 0.0),
    6: CommodityGroup(6, "Lubricating Oil", 800.9, 1163.5, 0.0, 0.34878, 0.0),
}

COMMODITY_TYPE_GROUPS = {
    "a": {1},
    "b": {2, 3, 4, 5},
    "d": {6},
}

def resolve_commodity_group(
    rho: float,
    commodity_type: str,
) -> CommodityGroup:
    """
    Resolve commodity group based on density and commodity type (A, B, D).
    """

    commodity_type = commodity_type.lower()
    if commodity_type not in COMMODITY_TYPE_GROUPS:
        raise MPMSValidationError("commodity_group must be A, B, or D")

    allowed_ids = COMMODITY_TYPE_GROUPS[commodity_type]
    allowed_groups = [
        g for g in COMMODITY_GROUPS.values()
        if g.id in allowed_ids
    ]

    # 1. Exact range match
    matching = [
        g for g in allowed_groups
        if g.rho_min <= rho < g.rho_max
    ]

    if matching:
        return min(
            matching,
            key=lambda g: (g.rho_max - g.rho_min)
        )

    # 2. Nearest by boundary distance
    def distance(g: CommodityGroup) -> float:
        if rho < g.rho_min:
            return g.rho_min - rho
        return rho - g.rho_max

    return min(allowed_groups, key=distance)
