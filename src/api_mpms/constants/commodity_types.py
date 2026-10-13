# api_mpms/constants/commodity_types.py

from enum import Enum


class CommodityType(str, Enum):
    """Tipos de producto de API MPMS 11.1."""

    CRUDE_OIL = "a"
    REFINED_PRODUCTS = "b"
    SPECIAL_APPLICATIONS = "c"
    LUBRICATING_OILS = "d"
