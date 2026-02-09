from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class ExtractionResult:
    industry: str
    printer_info: str
    business_type: str
    keywords: List[str]


INDUSTRY_KEYWORDS = {
    "包装": ["包装", "彩盒", "瓦楞", "包装材料"],
    "标签": ["标签", "不干胶", "条码", "label"],
    "印刷": ["印刷", "印务", "胶印", "数码印刷"],
    "广告": ["广告", "喷绘", "写真", "展示"],
}

BUSINESS_KEYWORDS = {
    "制造": ["生产", "制造", "工厂", "车间"],
    "贸易": ["贸易", "进出口", "供应", "采购"],
    "服务": ["服务", "解决方案", "支持"],
}

PRINTER_BRANDS = [
    "HP",
    "Epson",
    "Canon",
    "Xerox",
    "Ricoh",
    "Konica",
    "Brother",
    "Durst",
    "Mimaki",
    "Roland",
]

PRINTER_MODEL_RE = re.compile(rf"({'|'.join(PRINTER_BRANDS)})\\s*-?\\s*[A-Z]?\\d{{3,4}}", re.IGNORECASE)


def _match_keywords(text: str, keywords_map: dict) -> str:
    for label, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                return label
    return "未知"


def extract_info(text: str) -> ExtractionResult:
    industry = _match_keywords(text, INDUSTRY_KEYWORDS)
    business_type = _match_keywords(text, BUSINESS_KEYWORDS)

    models = [match.group(0) for match in PRINTER_MODEL_RE.finditer(text)]
    printer_info = "、".join(sorted(set(models))) or "未知"

    hit_keywords = []
    for keywords in INDUSTRY_KEYWORDS.values():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                hit_keywords.append(keyword)
    for keywords in BUSINESS_KEYWORDS.values():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                hit_keywords.append(keyword)

    return ExtractionResult(
        industry=industry,
        printer_info=printer_info,
        business_type=business_type,
        keywords=sorted(set(hit_keywords)),
    )
