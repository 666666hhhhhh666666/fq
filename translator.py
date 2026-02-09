from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import requests


CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")


@dataclass
class TranslationResult:
    text: str
    detected_lang: str
    translated: bool
    reason: str


def detect_language(text: str) -> str:
    if CHINESE_RE.search(text):
        return "zh"
    try:
        from langdetect import detect

        return detect(text)
    except Exception:
        return "unknown"


def translate_to_chinese(
    text: str,
    provider: str,
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout_s: int = 15,
    retries: int = 1,
) -> TranslationResult:
    detected_lang = detect_language(text)
    if detected_lang == "zh":
        return TranslationResult(text=text, detected_lang=detected_lang, translated=False, reason="already_zh")

    if provider == "libretranslate" and endpoint:
        payload = {
            "q": text,
            "source": "auto",
            "target": "zh",
            "format": "text",
        }
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        last_exc: Optional[Exception] = None
        for _ in range(retries + 1):
            try:
                resp = requests.post(endpoint, json=payload, headers=headers, timeout=timeout_s)
                if resp.status_code >= 400:
                    return TranslationResult(
                        text=text,
                        detected_lang=detected_lang,
                        translated=False,
                        reason=f"translate_http_{resp.status_code}",
                    )
                data = resp.json()
                translated = data.get("translatedText") or text
                return TranslationResult(
                    text=translated,
                    detected_lang=detected_lang,
                    translated=True,
                    reason="translated",
                )
            except Exception as exc:
                last_exc = exc
        return TranslationResult(
            text=text,
            detected_lang=detected_lang,
            translated=False,
            reason=f"translate_error:{last_exc}",
        )

    return TranslationResult(
        text=text,
        detected_lang=detected_lang,
        translated=False,
        reason="no_translator_configured",
    )
