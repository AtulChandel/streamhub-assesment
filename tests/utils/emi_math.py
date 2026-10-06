"""
Independent Financial Mathematics Engine
Used in test assertions to independently calculate expected EMI, total interest,
and total payment without relying on application-under-test logic.
"""

import math
import re
from typing import Dict, Union


def compute_expected_emi(principal: float, annual_rate: float, tenure_months: int) -> Dict[str, float]:
    """
    Computes exact financial metrics using the standard financial annuity formula:
      E = P * [ r * (1 + r)^n ] / [ (1 + r)^n - 1 ]
    Where:
      P = Principal
      r = Monthly interest rate (annual_rate / 12 / 100)
      n = Total months (tenure)
    """
    if principal <= 0 or tenure_months <= 0:
        return {
            "monthly_emi": 0.0,
            "total_interest": 0.0,
            "total_payment": 0.0,
            "principal_pct": 100.0,
            "interest_pct": 0.0,
        }

    monthly_rate = (annual_rate / 100.0) / 12.0

    if monthly_rate == 0:
        emi = principal / tenure_months
        return {
            "monthly_emi": round(emi, 2),
            "total_interest": 0.0,
            "total_payment": round(principal, 2),
            "principal_pct": 100.0,
            "interest_pct": 0.0,
        }

    compounded = math.pow(1 + monthly_rate, tenure_months)
    monthly_emi = (principal * monthly_rate * compounded) / (compounded - 1)
    total_payment = monthly_emi * tenure_months
    total_interest = total_payment - principal

    principal_pct = (principal / total_payment) * 100.0
    interest_pct = (total_interest / total_payment) * 100.0

    return {
        "monthly_emi": round(monthly_emi, 2),
        "total_interest": round(total_interest, 2),
        "total_payment": round(total_payment, 2),
        "principal_pct": round(principal_pct, 1),
        "interest_pct": round(interest_pct, 1),
    }


def parse_currency(value_str: Union[str, float, int]) -> float:
    """
    Parses currency strings like '$8,678.23', '₹ 1,00,000.00', '€500.50' into a float.
    """
    if isinstance(value_str, (int, float)):
        return float(value_str)

    cleaned = re.sub(r"[^\d.-]", "", str(value_str).strip())
    if not cleaned:
        return 0.0
    return float(cleaned)


def is_approximately_equal(actual: float, expected: float, tolerance: float = 1.0) -> bool:
    """
    Checks if actual matches expected within a tolerance (default $1.00 for rounding differences).
    """
    return abs(actual - expected) <= tolerance
