# -*- coding: utf-8 -*-
"""صفحه اصلي با 6 تب (سازگار با KivyMD 2.0)"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.scrollview import MDScrollView
from kivy.app import App
from pathlib import Path

from utils.rtl import rtl
from utils.helpers import (
    today_jalali, current_jalali_year, current_jalali_month,
    normalize_jetty, get_data_dir,
)

F = "Roboto"
RLM = "\u200F"  # Right-to-Left Mark


def pf(text):
    """متن فارسي براي داخل فيلد ورودي"""
    if not text:
        return ""
    s = str(text)
    # فقط اگر کاراکتر فارسي/عربي دارد
    if any("\u0600" <= c <= "\u06FF" for c in s):
        return RLM + s
    return s


def lbl(text):
    return MDLabel(
        text=rtl(text),halign="right", size_hint_y=None, height="26dp",
        font_name=F, theme_text_color="Secondary",
    )


def title_lbl(text):
    return MDLabel(
        text=rtl(text),halign="center", size_hint_y=None, height="36dp", font_name=F,
    )


# ---------- تب 1: کارمند ----------
class TabEmployee(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding="10dp", spacing="4dp", **kwargs)
        self._selected_id = None

        self.add_widget(title_lbl("ثبت و ويرايش کارمند"))
        self.add_widget(lbl("شماره پرسنلي (6 رقم)"))
        self.pnum = MDTextField(input_filter="int", font_name=F, size_hint_y=None, height="48dp")
        self.pnum.bind(text=self._on_pnum)
        self.add_widget(self.pnum)

        self.add_widget(lbl("نام و نام خانوادگي"))
        self.name = MDTextField(font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.name)

        self.add_widget(lbl("تاريخ (YYYY/MM/DD)"))
        self.date = MDTextField(text=today_jalali(), font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.date)

        self.add_widget(lbl("نوع اسکله"))
        self.jetty_value = "اسکله شرقي"
        jetty_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="44dp", spacing="8dp")
        self.btn_east = MDButton(
            MDButtonText(text=rtl("شرقي"), font_name=F), style="filled", size_hint_x=0.5,
            on_release=lambda x: self._set_jetty("اسکله شرقي"),
        )
        self.btn_west = MDButton(
            MDButtonText(text=rtl("غربي"), font_name=F), style="outlined", size_hint_x=0.5,
            on_release=lambda x: self._set_jetty("اسکله غربي"),
        )
        jetty_row.add_widget(self.btn_east)
        jetty_row.add_widget(self.btn_west)
        self.add_widget(jetty_row)

        btns = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="44dp", spacing="6dp")
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("ثبت"), font_name=F), style="filled", size_hint_x=0.5,
            on_release=lambda x: self._register(),
        ))
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("ذخيره ويرايش"), font_name=F), style="tonal", size_hint_x=0.5,
            on_release=lambda x: self._save_edit(),
        ))
        self.add_widget(btns)

        row2 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="40dp", spacing="6dp")
        row2.add_widget(MDButton(
            MDButtonText(text=rtl("حذف"), font_name=F), style="outlined", size_hint_x=0.5,
            on_release=lambda x: self._delete(),
        ))
        row2.add_widget(MDButton(
            MDButtonText(text=rtl("پاک کردن فرم"), font_name=F), style="text", size_hint_x=0.5,
            on_release=lambda x: self._clear(),
        ))
        self.add_widget(row2)

        self.status = MDLabel(text="", size_hint_y=None, height="28dp",halign="center", font_name=F)
        self.add_widget(self.status)

        self.add_widget(lbl("ليست (سال / ماه)"))
        filt = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="44dp", spacing="4dp")
        self.year_f = MDTextField(text=str(current_jalali_year()), size_hint_x=0.35, font_name=F)
        self.month_f = MDTextField(text=f"{current_jalali_month():02d}", size_hint_x=0.35, font_name=F)
        filt.add_widget(self.year_f)
        filt.add_widget(self.month_f)
        filt.add_widget(MDButton(
            MDButtonText(text=rtl("نمايش"), font_name=F), style="filled", size_hint_x=0.3,
            on_release=lambda x: self.refresh(),
        ))
        self.add_widget(filt)

        scroll = MDScrollView()
        self.list_box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="3dp")
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        self.add_widget(scroll)

    def refresh(self):
        self.date.text = today_jalali()
        self.list_box.clear_widgets()
        year = (self.year_f.text or "").strip()
        month = (self.month_f.text or "").strip()
        if not year or not month:
            return
        rows = App.get_running_app().db.get_employees_by_month(year, month)
        if not rows:
            self.list_box.add_widget(MDLabel(
                text=rtl("داده اي نيست"), size_hint_y=None, height="36dp",
               halign="center", font_name=F,
            ))
            return
        for row in rows:
            self.list_box.add_widget(MDButton(
                MDButtonText(text=rtl(f"{row[1]} | {row[2]} | {row[4]} | {row[5]}"), font_name=F),
                style="tonal", size_hint_x=1, size_hint_y=None, height="40dp",
                on_release=lambda x, r=row: self._select(r),
            ))


    def _set_jetty(self, value):
        self.jetty_value = value
        if "غرب" in value:
            self.btn_east.style = "outlined"
            self.btn_west.style = "filled"
        else:
            self.btn_east.style = "filled"
            self.btn_west.style = "outlined"

    def _on_pnum(self, inst, value):
        if len(value) == 6:
            emp = App.get_running_app().db.get_employee_by_personnel(value)
            if emp:
                self.name.text = pf(emp[0])

    def _register(self):
        pnum = (self.pnum.text or "").strip().replace("\u200F", "")
        name = (self.name.text or "").strip().replace("\u200F", "")
        date = (self.date.text or "").strip().replace("\u200F", "")
        jetty = normalize_jetty(self.jetty_value)
        if not all([pnum, name, date]):
            self.status.text = rtl("همه فيلدها را پر کنيد")
            return
        if not (pnum.isdigit() and len(pnum) == 6):
            self.status.text = rtl("شماره بايد 6 رقم باشد")
            return
        ok, msg = App.get_running_app().db.register_employee(name, pnum, "رسمي", date, jetty)
        self.status.text = rtl(msg)
        if ok:
            self._clear()
            self.refresh()

    def _select(self, row):
        self._selected_id = row[0]
        self.name.text = pf(row[1])
        self.pnum.text = row[2]
        self.date.text = row[4]
        self._set_jetty(row[5] if "غرب" in row[5] else "اسکله شرقي")
        self.status.text = rtl(f"انتخاب: {row[1]}")

    def _save_edit(self):
        if not self._selected_id:
            self.status.text = rtl("ابتدا از ليست انتخاب کنيد")
            return
        name = (self.name.text or "").strip().replace("\u200F", "")
        pnum = (self.pnum.text or "").strip().replace("\u200F", "")
        date = (self.date.text or "").strip().replace("\u200F", "")
        jetty = normalize_jetty(self.jetty_value)
        if not all([name, pnum, date]):
            self.status.text = rtl("همه فيلدها را پر کنيد")
            return
        if not (pnum.isdigit() and len(pnum) == 6):
            self.status.text = rtl("شماره بايد 6 رقم باشد")
            return
        ok, msg = App.get_running_app().db.update_employee(
            self._selected_id, name, pnum, date, jetty,
        )
        self.status.text = rtl(msg)
        if ok:
            self._clear()
            self.refresh()

    def _delete(self):
        if not self._selected_id:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        App.get_running_app().db.delete_employee(self._selected_id)
        self.status.text = rtl("حذف شد")
        self._clear()
        self.refresh()

    def _clear(self):
        self._selected_id = None
        self.pnum.text = ""
        self.name.text = ""
        self.date.text = today_jalali()
        self._set_jetty("اسکله شرقي")
        self.status.text = ""


# ---------- تب 2: شرح کار ----------
class TabTask(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding="10dp", spacing="4dp", **kwargs)
        self._selected_id = None

        self.add_widget(title_lbl("ثبت و ويرايش شرح کار"))
        self.add_widget(lbl("شرح کار تعميراتي"))
        self.desc = MDTextField(multiline=True, size_hint_y=None, height="100dp", font_name=F)
        self.add_widget(self.desc)

        self.add_widget(lbl("نوع اسکله"))
        self.jetty_value = "اسکله شرقي"
        jetty_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="44dp", spacing="8dp")
        self.btn_east = MDButton(
            MDButtonText(text=rtl("شرقي"), font_name=F), style="filled", size_hint_x=0.5,
            on_release=lambda x: self._set_jetty("اسکله شرقي"),
        )
        self.btn_west = MDButton(
            MDButtonText(text=rtl("غربي"), font_name=F), style="outlined", size_hint_x=0.5,
            on_release=lambda x: self._set_jetty("اسکله غربي"),
        )
        jetty_row.add_widget(self.btn_east)
        jetty_row.add_widget(self.btn_west)
        self.add_widget(jetty_row)

        btns = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="44dp", spacing="6dp")
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("ثبت"), font_name=F), style="filled", size_hint_x=0.33,
            on_release=lambda x: self._add(),
        ))
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("ذخيره"), font_name=F), style="tonal", size_hint_x=0.33,
            on_release=lambda x: self._save(),
        ))
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("حذف"), font_name=F), style="outlined", size_hint_x=0.33,
            on_release=lambda x: self._delete(),
        ))
        self.add_widget(btns)
        self.status = MDLabel(text="", size_hint_y=None, height="28dp",halign="center", font_name=F)
        self.add_widget(self.status)

        self.add_widget(lbl("ليست (انتخاب براي ويرايش)"))
        scroll = MDScrollView()
        self.list_box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="3dp")
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        self.add_widget(scroll)

    def refresh(self):
        self.list_box.clear_widgets()
        rows = App.get_running_app().db.get_tasks()
        if not rows:
            self.list_box.add_widget(MDLabel(
                text=rtl("داده اي نيست"), size_hint_y=None, height="36dp",
               halign="center", font_name=F,
            ))
            return
        for row in rows:
            self.list_box.add_widget(MDButton(
                MDButtonText(text=rtl(f"{row[2]} | {row[1][:50]}"), font_name=F),
                style="tonal", size_hint_x=1, size_hint_y=None, height="40dp",
                on_release=lambda x, r=row: self._select(r),
            ))


    def _set_jetty(self, value):
        self.jetty_value = value
        if "غرب" in value:
            self.btn_east.style = "outlined"
            self.btn_west.style = "filled"
        else:
            self.btn_east.style = "filled"
            self.btn_west.style = "outlined"

    def _add(self):
        desc = (self.desc.text or "").strip().replace("\u200F", "")
        if not desc:
            self.status.text = rtl("شرح کار را وارد کنيد")
            return
        App.get_running_app().db.add_task(desc, normalize_jetty(self.jetty_value), today_jalali())
        self.status.text = rtl("ثبت شد")
        self.desc.text = ""
        self._selected_id = None
        self.refresh()

    def _select(self, row):
        self._selected_id = row[0]
        self.desc.text = pf(row[1])
        self._set_jetty(row[2] if "غرب" in row[2] else "اسکله شرقي")
        self.status.text = rtl("انتخاب شد")

    def _save(self):
        if not self._selected_id:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        desc = (self.desc.text or "").strip().replace("\u200F", "")
        if not desc:
            self.status.text = rtl("شرح خالي است")
            return
        App.get_running_app().db.update_task(
            self._selected_id, desc, normalize_jetty(self.jetty_value)
        )
        self.status.text = rtl("ذخيره شد")
        self.refresh()

    def _delete(self):
        if not self._selected_id:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        App.get_running_app().db.delete_task(self._selected_id)
        self.status.text = rtl("حذف شد")
        self.desc.text = ""
        self._selected_id = None
        self.refresh()


# ---------- تب 3: جستجو ----------
class TabSearch(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding="10dp", spacing="4dp", **kwargs)
        self.add_widget(title_lbl("جستجو"))
        self.add_widget(lbl("شماره پرسنلي (اختياري)"))
        self.pnum = MDTextField(input_filter="int", font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.pnum)
        self.add_widget(lbl("از تاريخ (اختياري)"))
        self.start = MDTextField(font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.start)
        self.add_widget(lbl("تا تاريخ (اختياري)"))
        self.end = MDTextField(font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.end)

        self.name_lbl = MDLabel(text="", size_hint_y=None, height="28dp",halign="center", font_name=F)
        self.add_widget(self.name_lbl)

        days = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="32dp")
        self.east = MDLabel(text=rtl("شرقي: 0"),halign="center", font_name=F)
        self.west = MDLabel(text=rtl("غربي: 0"),halign="center", font_name=F)
        self.total = MDLabel(text=rtl("جمع: 0"),halign="center", font_name=F)
        days.add_widget(self.east)
        days.add_widget(self.west)
        days.add_widget(self.total)
        self.add_widget(days)

        self.add_widget(MDButton(
            MDButtonText(text=rtl("جستجو"), font_name=F), style="filled", size_hint_x=1,
            on_release=lambda x: self._search(),
        ))
        scroll = MDScrollView()
        self.results = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="3dp", padding="4dp")
        self.results.bind(minimum_height=self.results.setter("height"))
        scroll.add_widget(self.results)
        self.add_widget(scroll)

    def refresh(self):
        y, m = current_jalali_year(), current_jalali_month()
        self.start.text = f"{y}/{m:02d}/01"
        last = 31 if m <= 6 else (29 if m == 12 else 30)
        self.end.text = f"{y}/{m:02d}/{last}"

    def _search(self):
        pnum = (self.pnum.text or "").strip()
        start = (self.start.text or "").strip() or None
        end = (self.end.text or "").strip() or None
        self.results.clear_widgets()
        self.name_lbl.text = ""

        if pnum and not (pnum.isdigit() and len(pnum) == 6):
            self.east.text = rtl("شماره نامعتبر")
            self.west.text = ""
            self.total.text = ""
            return
        if not pnum and not start and not end:
            self.east.text = rtl("کد يا تاريخ را وارد کنيد")
            self.west.text = ""
            self.total.text = ""
            return

        app = App.get_running_app()

        if pnum:
            rows = app.db.search_employee(pnum, start, end)
            # search returns: name, pnum, type, date, jetty
            e, w = app.db.count_days(
                pnum,
                start or "0000/00/00",
                end or "9999/99/99",
            )
            emp = app.db.get_employee_by_personnel(pnum)
            if emp:
                self.name_lbl.text = rtl(f"نام: {emp[0]}  |  {emp[2]}")
            elif rows:
                self.name_lbl.text = rtl(f"نام: {rows[0][0]}")
            display = [(r[0], r[1], r[2], r[3], r[4]) for r in rows]
        else:
            # فقط بازه تاريخ — همه افراد
            if start and end:
                raw = app.db.get_employees_by_range(start, end)
            elif start:
                raw = app.db.get_employees_by_range(start, "9999/99/99")
            else:
                raw = app.db.get_employees_by_range("0000/00/00", end)
            # raw: id, name, pnum, type, date, jetty
            display = [(r[1], r[2], r[3], r[4], r[5]) for r in raw]
            e = sum(1 for r in display if "شرق" in str(r[4]))
            w = sum(1 for r in display if "غرب" in str(r[4]))

        self.east.text = rtl(f"شرقي: {e}")
        self.west.text = rtl(f"غربي: {w}")
        self.total.text = rtl(f"جمع: {e + w}")

        if not display:
            self.results.add_widget(MDLabel(
                text=rtl("نتيجه اي نيست"), size_hint_y=None, height="36dp",
                halign="center", font_name=F,
            ))
            return
        self.results.add_widget(MDLabel(
            text=rtl("رديف | نام | پرسنلي | تاريخ | اسکله"), size_hint_y=None, height="30dp",
            halign="right", font_name=F, theme_text_color="Secondary",
        ))
        for i, r in enumerate(display, 1):
            self.results.add_widget(MDLabel(
                text=rtl(f"{i} | {r[0]} | {r[1]} | {r[3]} | {r[4]}"),
                size_hint_y=None, height="34dp",halign="right", font_name=F,
            ))



class TabExport(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding="16dp", spacing="6dp", **kwargs)
        self.add_widget(title_lbl("خروجي PDF"))
        self.add_widget(lbl("سال (اختياري)"))
        self.year = MDTextField(text=str(current_jalali_year()), font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.year)
        self.add_widget(lbl("ماه 01-12 (اختياري)"))
        self.month = MDTextField(text=f"{current_jalali_month():02d}", font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.month)
        self.add_widget(lbl("کد پرسنلي (اختياري — خالي = همه)"))
        self.pnum = MDTextField(input_filter="int", font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.pnum)

        row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="48dp", spacing="8dp")
        row.add_widget(MDButton(
            MDButtonText(text=rtl("توليد PDF"), font_name=F), style="filled", size_hint_x=0.55,
            on_release=lambda x: self._export(),
        ))
        row.add_widget(MDButton(
            MDButtonText(text=rtl("پاک کردن فرم"), font_name=F), style="outlined", size_hint_x=0.45,
            on_release=lambda x: self._clear_form(),
        ))
        self.add_widget(row)

        self.status = MDLabel(text="", size_hint_y=None, height="100dp",halign="center", font_name=F)
        self.add_widget(self.status)

    def refresh(self):
        pass

    def _clear_form(self):
        self.year.text = str(current_jalali_year())
        self.month.text = f"{current_jalali_month():02d}"
        self.pnum.text = ""
        self.status.text = rtl("فرم پاک شد — تاريخ امروز قرار گرفت")

    def _export(self):
        year = (self.year.text or "").strip()
        month = (self.month.text or "").strip()
        pnum_filter = (self.pnum.text or "").strip()

        if pnum_filter and not (pnum_filter.isdigit() and len(pnum_filter) == 6):
            self.status.text = rtl("کد پرسنلي بايد 6 رقم باشد يا خالي")
            return
        has_period = bool(year and month)
        has_pnum = bool(pnum_filter)
        if not has_period and not has_pnum:
            self.status.text = rtl("سال و ماه، يا فقط کد پرسنلي را وارد کنيد")
            return

        app = App.get_running_app()

        if has_pnum and not has_period:
            rows_raw = app.db.search_employee(pnum_filter, None, None)
            rows = [(0, r[0], r[1], r[2], r[3], r[4]) for r in rows_raw]
        else:
            rows = app.db.get_employees_by_month(year, month)
            if has_pnum:
                rows = [r for r in rows if str(r[2]) == pnum_filter]

        all_tasks = app.db.get_tasks()
        if has_period:
            pattern = f"{year}/{int(month):02d}/"
            tasks = [tk for tk in all_tasks if str(tk[3]).startswith(pattern)]
        else:
            tasks = list(all_tasks)
        tasks = sorted(tasks, key=lambda x: str(x[3]))

        if not rows and not tasks:
            self.status.text = rtl("داده اي نيست")
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.units import cm
            import arabic_reshaper
            from bidi.algorithm import get_display
        except ImportError:
            self.status.text = rtl("نصب: pip install reportlab arabic-reshaper python-bidi")
            return

        def ptext(s):
            if s is None:
                return ""
            try:
                return get_display(arabic_reshaper.reshape(str(s)))
            except Exception:
                return str(s)

        default_name = "report"
        if has_period:
            default_name += f"_{year}_{month}"
        if has_pnum:
            default_name += f"_{pnum_filter}"
        default_name += ".pdf"

        path = None
        # دسکتاپ: پرسش مسیر با tkinter
        try:
            from tkinter import filedialog
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            try:
                root.attributes("-topmost", True)
            except Exception:
                pass
            path_str = filedialog.asksaveasfilename(
                title="ذخيره فایل PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialfile=default_name,
                initialdir=str(Path.home() / "Desktop"),
            )
            root.destroy()
            if path_str:
                path = Path(path_str)
            else:
                self.status.text = rtl("لغو شد")
                return
        except Exception:
            # اندروید / بدون tkinter: ذخیره در پوشه داده برنامه
            path = get_data_dir(app) / default_name

        font_name = "Helvetica"
        font_candidates = [
            r"C:\Windows\Fonts\tahoma.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            "/system/fonts/NotoNaskhArabic-Regular.ttf",
            "/system/fonts/NotoSansArabic-Regular.ttf",
            "/system/fonts/DroidSansArabic.ttf",
            "/system/fonts/Roboto-Regular.ttf",
            str(Path(__file__).resolve().parent.parent / "assets" / "Vazir.ttf"),
        ]
        for fp in font_candidates:
            if Path(fp).is_file():
                try:
                    pdfmetrics.registerFont(TTFont("PersianPDF", fp))
                    font_name = "PersianPDF"
                    break
                except Exception:
                    pass

        c = canvas.Canvas(str(path), pagesize=A4)
        w, h = A4
        margin = 1.5 * cm
        right = w - margin
        y = h - 2 * cm

        def new_page_if_needed(need=1.0):
            nonlocal y
            if y < margin + need * cm:
                c.showPage()
                y = h - 2 * cm
                c.setFont(font_name, 10)

        def rdraw(x_from_right, text, size=10):
            """رسم راست‌چين: x_from_right فاصله از لبه راست محتوا"""
            c.setFont(font_name, size)
            c.drawRightString(right - x_from_right, y, ptext(text))

        # عنوان وسط
        c.setFont(font_name, 16)
        title = "گزارش فوق العاده اسکله ها"
        if has_period:
            title += f" — {year}/{month}"
        if has_pnum:
            title += f" — پرسنلي {pnum_filter}"
        c.drawCentredString(w / 2, y, ptext(title))
        y -= 1.0 * cm

        # --- کارمندان (راست‌چين) ---
        # ستون‌ها از راست: ردیف | نام | پرسنلی | تاریخ | اسکله
        # فاصله از لبه راست
        # ردیف نزدیک راست، بعد نام، ...
        cols = [0, 1.3*cm, 6.5*cm, 10*cm, 13.5*cm]  # فاصله از راست برای drawRightString

        rdraw(0, "لیست کارمندان ثبت شده", 13)
        y -= 0.7 * cm
        headers = ["ردیف", "نام و نام خانوادگی", "شماره پرسنلی", "تاریخ", "اسکله"]
        for i, hd in enumerate(headers):
            rdraw(cols[i], hd, 10)
        y -= 0.35 * cm
        c.line(margin, y, right, y)
        y -= 0.45 * cm

        if not rows:
            rdraw(0, "(بدون کارمند)", 10)
            y -= 0.6 * cm
        else:
            for idx, row in enumerate(rows, 1):
                new_page_if_needed(0.6)
                vals = [str(idx), str(row[1])[:28], str(row[2]), str(row[4]), str(row[5])]
                for i, v in enumerate(vals):
                    rdraw(cols[i], v, 10)
                y -= 0.5 * cm

        y -= 0.4 * cm
        new_page_if_needed(2)
        c.line(margin, y, right, y)
        y -= 0.7 * cm

        # --- شرح کار (راست‌چين جدولی) ---
        rdraw(0, "شرح کارهای تعمیراتی انجام شده", 13)
        y -= 0.7 * cm
        tcols = [0, 1.3*cm, 4.5*cm, 8*cm]  # ردیف، تاریخ، اسکله، شرح
        for i, hd in enumerate(["ردیف", "تاریخ", "اسکله", "شرح کار"]):
            rdraw(tcols[i], hd, 10)
        y -= 0.35 * cm
        c.line(margin, y, right, y)
        y -= 0.45 * cm

        if not tasks:
            rdraw(0, "(بدون شرح کار)", 10)
            y -= 0.6 * cm
        else:
            for idx, tk in enumerate(tasks, 1):
                desc = str(tk[1])
                max_c = 40
                chunks = []
                while desc:
                    chunks.append(desc[:max_c])
                    desc = desc[max_c:]
                if not chunks:
                    chunks = [""]
                new_page_if_needed(0.5 * len(chunks) + 0.2)
                rdraw(tcols[0], str(idx), 10)
                rdraw(tcols[1], str(tk[3]), 10)
                rdraw(tcols[2], str(tk[2])[:18], 10)
                rdraw(tcols[3], chunks[0], 10)
                y -= 0.45 * cm
                for ch in chunks[1:]:
                    new_page_if_needed(0.5)
                    rdraw(tcols[3], ch, 10)
                    y -= 0.4 * cm

        c.save()
        self.status.text = rtl(f"ذخيره شد:\n{path}")
        print("[PDF]", path)



class TabUsers(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding="10dp", spacing="4dp", **kwargs)
        self._old = None
        self.add_widget(title_lbl("مديريت کاربران"))
        scroll = MDScrollView(size_hint_y=0.4)
        self.list_box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="3dp")
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        self.add_widget(scroll)

        self.add_widget(lbl("نام کاربري"))
        self.user_f = MDTextField(font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.user_f)
        self.add_widget(lbl("رمز عبور"))
        self.pwd_f = MDTextField(password=True, font_name=F, size_hint_y=None, height="48dp")
        self.add_widget(self.pwd_f)

        btns = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="44dp", spacing="6dp")
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("ثبت"), font_name=F), style="filled", size_hint_x=0.33,
            on_release=lambda x: self._add(),
        ))
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("ويرايش"), font_name=F), style="tonal", size_hint_x=0.33,
            on_release=lambda x: self._edit(),
        ))
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("حذف"), font_name=F), style="outlined", size_hint_x=0.33,
            on_release=lambda x: self._delete(),
        ))
        self.add_widget(btns)
        self.status = MDLabel(text="", size_hint_y=None, height="28dp",halign="center", font_name=F)
        self.add_widget(self.status)

    def refresh(self):
        self.list_box.clear_widgets()
        app = App.get_running_app()
        for u, _ in app.db.get_users():
            if app.current_user != "Administrator" and u == "Administrator":
                continue
            self.list_box.add_widget(MDButton(
                MDButtonText(text=rtl(u), font_name=F),
                style="tonal", size_hint_x=1, size_hint_y=None, height="40dp",
                on_release=lambda x, n=u: self._select(n),
            ))

    def _select(self, name):
        self.user_f.text = name
        self.pwd_f.text = ""
        self._old = name
        self.status.text = rtl(f"انتخاب: {name}")

    def _add(self):
        u = (self.user_f.text or "").strip()
        p = (self.pwd_f.text or "").strip()
        if not u or not p:
            self.status.text = rtl("نام و رمز را وارد کنيد")
            return
        ok = App.get_running_app().db.add_user(u, p)
        self.status.text = rtl("ثبت شد" if ok else "اين نام وجود دارد")
        if ok:
            self.user_f.text = ""
            self.pwd_f.text = ""
            self._old = None
            self.refresh()

    def _edit(self):
        if not self._old:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        nu = (self.user_f.text or "").strip()
        np = (self.pwd_f.text or "").strip()
        if not nu:
            self.status.text = rtl("نام خالي است")
            return
        ok = App.get_running_app().db.update_user(self._old, nu, np or None)
        self.status.text = rtl("ويرايش شد" if ok else "خطا")
        if ok:
            self._old = nu
            self.refresh()

    def _delete(self):
        name = self._old or (self.user_f.text or "").strip()
        if not name:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        if name == "Administrator":
            self.status.text = rtl("Administrator قابل حذف نيست")
            return
        App.get_running_app().db.delete_user(name)
        self.status.text = rtl("حذف شد")
        self.user_f.text = ""
        self.pwd_f.text = ""
        self._old = None
        self.refresh()


# ---------- تب 6: درباره ----------
class TabAbout(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding="20dp", spacing="12dp", **kwargs)
        for line in [
            "نرم افزار ثبت فوق العاده اسکله ها",
            "طراحي: عليرضا برادران",
            "نسخه موبايل ساده: 2.0",
            "eng.alireza86@gmail.com",
        ]:
            self.add_widget(MDLabel(
                text=rtl(line),halign="center", size_hint_y=None, height="36dp", font_name=F,
            ))
        self.add_widget(MDButton(
            MDButtonText(text=rtl("خروج از حساب"), font_name=F), style="outlined", size_hint_x=1,
            on_release=self._logout,
        ))

    def refresh(self):
        pass

    def _logout(self, *args):
        app = App.get_running_app()
        app.current_user = None
        app.root.current = "login"


# ---------- صفحه اصلي با دکمه‌هاي تب ----------
class MainTabsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"

        root = MDBoxLayout(orientation="vertical")

        # ناحيه محتوا
        self.content = MDBoxLayout(orientation="vertical")
        root.add_widget(self.content)

        # نوار تب پايين
        bar = MDBoxLayout(
            orientation="horizontal", size_hint_y=None, height="56dp",
            spacing="2dp", padding="4dp",
        )
        self.tabs = {}
        tab_defs = [
            ("emp", "کارمند", TabEmployee),
            ("task", "شرح کار", TabTask),
            ("search", "جستجو", TabSearch),
            ("export", "خروجی PDF", TabExport),
            ("users", "کاربران", TabUsers),
            ("about", "درباره", TabAbout),
        ]
        self.tab_instances = {}
        for key, title, cls in tab_defs:
            inst = cls()
            self.tab_instances[key] = inst
            bar.add_widget(MDButton(
                MDButtonText(text=rtl(title), font_name=F),
                style="tonal", size_hint_x=1,
                on_release=lambda x, k=key: self._switch(k),
            ))
        root.add_widget(bar)
        self.add_widget(root)

        self._current = None
        self._switch("emp")

    def on_enter(self, *args):
        if self._current and hasattr(self.tab_instances[self._current], "refresh"):
            self.tab_instances[self._current].refresh()

    def _switch(self, key):
        self.content.clear_widgets()
        self.content.add_widget(self.tab_instances[key])
        self._current = key
        if hasattr(self.tab_instances[key], "refresh"):
            self.tab_instances[key].refresh()
