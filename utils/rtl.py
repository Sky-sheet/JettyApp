# -*- coding: utf-8 -*-
"""تبديل متن فارسي براي نمايش صحيح در Kivy"""

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _HAS = True
except ImportError:
    _HAS = False
    print("[WARN] pip install arabic-reshaper python-bidi")


def rtl(text) -> str:
    """متن را براي نمايش در ليبل/دکمه آماده مي‌کند."""
    if text is None or text == "":
        return ""
    if not _HAS:
        return str(text)
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return str(text)


def to_logical(display_text: str) -> str:
    """
    تلاش براي برگرداندن متن نمايشي به ترتيب منطقي.
    اگر ممکن نباشد همان متن را برمي‌گرداند.
    """
    if not display_text:
        return ""
    if not _HAS:
        return display_text
    try:
        # get_display دوباره روي متن display معمولاً به logical نزديک مي‌شود
        return get_display(display_text)
    except Exception:
        return display_text
