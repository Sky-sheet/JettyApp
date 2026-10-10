# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.scrollview import MDScrollView
from kivy.app import App
from utils.helpers import current_jalali_year, current_jalali_month
from utils.rtl import rtl

F = "Roboto"


def field_label(text):
    return MDLabel(
        text=rtl(text), halign="right", size_hint_y=None, height="26dp",
        font_name=F, theme_text_color="Secondary",
    )


class SearchScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "search"

        outer = MDBoxLayout(orientation="vertical", padding="8dp", spacing="4dp")
        outer.add_widget(MDButton(
            MDButtonText(text=rtl("بازگشت"), font_name=F), style="text", size_hint_x=1,
            on_release=lambda x: setattr(self.manager, "current", "home"),
        ))
        outer.add_widget(MDLabel(text=rtl("جستجوي کارمند"), halign="center",
                                 size_hint_y=None, height="36dp", font_name=F))

        form = MDBoxLayout(orientation="vertical", padding="12dp", spacing="4dp",
                           size_hint_y=None, height="300dp")

        form.add_widget(field_label("شماره پرسنلي (6 رقم)"))
        self.pnum_field = MDTextField(input_filter="int", font_name=F)
        form.add_widget(self.pnum_field)

        form.add_widget(field_label("از تاريخ"))
        self.start_field = MDTextField(font_name=F)
        form.add_widget(self.start_field)

        form.add_widget(field_label("تا تاريخ"))
        self.end_field = MDTextField(font_name=F)
        form.add_widget(self.end_field)

        days = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="32dp")
        self.east_label = MDLabel(text=rtl("شرقي: 0"), halign="center", font_name=F)
        self.west_label = MDLabel(text=rtl("غربي: 0"), halign="center", font_name=F)
        days.add_widget(self.east_label)
        days.add_widget(self.west_label)
        form.add_widget(days)

        form.add_widget(MDButton(
            MDButtonText(text=rtl("جستجو"), font_name=F), style="filled", size_hint_x=1, on_release=self._search,
        ))
        outer.add_widget(form)

        scroll = MDScrollView()
        self.result_box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="4dp", padding="8dp")
        self.result_box.bind(minimum_height=self.result_box.setter("height"))
        scroll.add_widget(self.result_box)
        outer.add_widget(scroll)
        self.add_widget(outer)

    def on_enter(self, *args):
        y, m = current_jalali_year(), current_jalali_month()
        self.start_field.text = f"{y}/{m:02d}/01"
        last = 31 if m <= 6 else (29 if m == 12 else 30)
        self.end_field.text = f"{y}/{m:02d}/{last}"

    def _search(self, *args):
        pnum = (self.pnum_field.text or "").strip()
        start = (self.start_field.text or "").strip()
        end = (self.end_field.text or "").strip()
        self.result_box.clear_widgets()
        if not (pnum.isdigit() and len(pnum) == 6):
            self.east_label.text = rtl("شماره نامعتبر")
            return
        app = App.get_running_app()
        rows = app.db.search_employee(pnum, start or None, end or None)
        east, west = app.db.count_days(pnum, start, end)
        self.east_label.text = rtl(f"شرقي: {east}")
        self.west_label.text = rtl(f"غربي: {west}")
        if not rows:
            self.result_box.add_widget(MDLabel(
                text=rtl("نتيجه اي يافت نشد"), size_hint_y=None, height="40dp",
                halign="center", font_name=F,
            ))
            return
        for r in rows:
            self.result_box.add_widget(MDLabel(
                text=rtl(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}"),
                size_hint_y=None, height="36dp", halign="right", font_name=F,
            ))
