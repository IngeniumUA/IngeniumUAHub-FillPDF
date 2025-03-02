import math
from decimal import Decimal


def round_half_up(number, decimals=2):
    multiplier = Decimal(10**decimals)
    return math.floor(number * multiplier + Decimal(0.5)) / multiplier
