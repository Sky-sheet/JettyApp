# -*- coding: utf-8 -*-
"""توابع کمکی تاریخ شمسی و مسیرها"""

from datetime import datetime
from pathlib import Path
import jdatetime


def gregorian_to_jalali(gy: int = None, gm: int = None, gd: int = None) -> str:
    """تبدیل به شمسی با فرمت YYYY/MM/DD. اگر آرگومان ندهید، امروز برمی‌گردد."""
    if gy is None:
        today = datetime.now()
        gy, gm, gd = today.year, today.month, today.day
    j = jdatetime.date.fromgregorian(year=gy, month=gm, day=gd)
    return f"{j.year:04d}/{j.month:02d}/{j.day:02d}"


def today_jalali() -> str:
    return gregorian_to_jalali()


def current_jalali_year() -> int:
    return jdatetime.date.today().year


def current_jalali_month() -> int:
    return jdatetime.date.today().month


def persian_month_name(month: int) -> str:
    names = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    return names[month - 1] if 1 <= month <= 12 else ""


def month_name_to_num(name: str) -> int:
    mapping = {
        "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4,
        "مرداد": 5, "شهریور": 6, "مهر": 7, "آبان": 8,
        "آذر": 9, "دی": 10, "بهمن": 11, "اسفند": 12
    }
    return mapping.get(name, 0)


def normalize_jetty(text: str) -> str:
    text = text.strip().replace("ي", "ی")
    if "شرقی" in text:
        return "اسکله شرقی"
    if "غربی" in text or "غرب" in text:
        return "اسکله غربی"
    return text


def to_persian_digits(text) -> str:
    persian = "۰۱۲۳۴۵۶۷۸۹"
    english = "0123456789"
    return str(text).translate(str.maketrans(english, persian))


def get_data_dir(app) -> Path:
    """مسیر داده‌های کاربر (روی اندروید قابل نوشتن است)"""
    try:
        p = Path(app.user_data_dir)
    except Exception:
        p = Path("data")
    p.mkdir(parents=True, exist_ok=True)
    return p
