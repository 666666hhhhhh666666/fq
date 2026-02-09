from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass
from html import unescape
from typing import Optional

import requests


@dataclass
class CrawlResult:
    url: str
    ok: bool
    text: str
    reason: str


CAPTCHA_PATTERNS = re.compile(
    r"captcha|验证|安全检查|robot|cloudflare|访问受限|unusual traffic",
    re.IGNORECASE,
)


def _clean_html(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<[^>]+>", " ", html)
    html = unescape(html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()


def _detect_block(html: str) -> Optional[str]:
    if CAPTCHA_PATTERNS.search(html):
        return "captcha_or_block"
    return None


def _requests_fetch(url: str, timeout_s: int, retries: int, user_agent: str) -> CrawlResult:
    headers = {"User-Agent": user_agent}
    last_exc: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=timeout_s, headers=headers)
            if resp.status_code >= 400:
                return CrawlResult(url=url, ok=False, text="", reason=f"http_{resp.status_code}")
            html = resp.text
            block_reason = _detect_block(html)
            if block_reason:
                return CrawlResult(url=url, ok=False, text="", reason=block_reason)
            return CrawlResult(url=url, ok=True, text=_clean_html(html), reason="ok")
        except requests.RequestException as exc:
            last_exc = exc
            time.sleep(1 + attempt)
    return CrawlResult(url=url, ok=False, text="", reason=f"request_error:{last_exc}")


async def _playwright_fetch(url: str, timeout_s: int) -> CrawlResult:
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:  # pragma: no cover - optional dependency
        return CrawlResult(url=url, ok=False, text="", reason=f"playwright_unavailable:{exc}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=timeout_s * 1000)
            html = await page.content()
            await browser.close()
            block_reason = _detect_block(html)
            if block_reason:
                return CrawlResult(url=url, ok=False, text="", reason=block_reason)
            return CrawlResult(url=url, ok=True, text=_clean_html(html), reason="ok")
    except Exception as exc:  # pragma: no cover - best effort
        return CrawlResult(url=url, ok=False, text="", reason=f"playwright_error:{exc}")


def fetch_text(
    url: str,
    timeout_s: int = 20,
    retries: int = 2,
    use_playwright_fallback: bool = True,
    user_agent: str = "Mozilla/5.0",
) -> CrawlResult:
    result = _requests_fetch(url, timeout_s=timeout_s, retries=retries, user_agent=user_agent)
    if result.ok:
        return result
    if not use_playwright_fallback:
        return result
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(_playwright_fetch(url, timeout_s=timeout_s))
    finally:
        loop.close()
