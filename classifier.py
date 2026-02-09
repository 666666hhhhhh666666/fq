from __future__ import annotations


CLASSIFIER_RULES = [
    ("打印厂", ["印刷", "印务", "印厂", "包装印刷", "标签印刷"]),
    ("打印机代理商", ["代理", "授权", "经销", "售后", "OEM"]),
    ("分销商", ["分销", "渠道", "总代", "批发"]),
    ("贸易商", ["贸易", "进出口", "外贸", "供应链"]),
    ("终端产品商", ["终端", "品牌", "产品制造", "消费品", "电子产品"]),
]


def classify_company(text: str) -> str:
    lower_text = text.lower()
    for label, keywords in CLASSIFIER_RULES:
        for keyword in keywords:
            if keyword.lower() in lower_text:
                return label
    return "未知"
