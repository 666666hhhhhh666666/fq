from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class EstimateResult:
    range_text: str
    median: float
    explanation: str


def estimate_purchase(
    industry: str,
    company_type: str,
    estimator_cfg: Dict,
) -> EstimateResult:
    default_range = estimator_cfg.get("default_range", {"min": 10, "max": 80})
    base_min = default_range.get("min", 10)
    base_max = default_range.get("max", 80)

    explanation_parts = [f"base({base_min}-{base_max})"]

    type_ranges = estimator_cfg.get("company_type_ranges", {})
    if company_type in type_ranges:
        base_min = type_ranges[company_type].get("min", base_min)
        base_max = type_ranges[company_type].get("max", base_max)
        explanation_parts.append(f"type({company_type})")

    industry_bias = estimator_cfg.get("industry_bias", {})
    if industry in industry_bias:
        base_min += industry_bias[industry].get("min_delta", 0)
        base_max += industry_bias[industry].get("max_delta", 0)
        explanation_parts.append(f"industry({industry})")

    median = round((base_min + base_max) / 2, 2)
    range_text = f"{base_min}-{base_max}"
    explanation = ", ".join(explanation_parts)

    return EstimateResult(range_text=range_text, median=median, explanation=explanation)
