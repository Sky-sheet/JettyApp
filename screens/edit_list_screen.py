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


class EditListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "edit_list"
        self._rows = []
        self._selected_id = None

        outer = MDBoxLayout(orientation="vertical", padding="8dp", spacing="4dp")
        outer.add_widget(MDButton(
            MDButtonText(text=rtl("بازگشت"), font_name=F), style="text", size_hint_x=1,
            on_release=lambda x: setattr(self.manager, "current", "home"),
        ))
        outer.add_widget(MDLabel(text=rtl("ويرايش اطلاعات"), halign="center",
                                 size_hint_y=None, height="36dp", font_name=F))

        # فيلتر
        outer.add_widget(field_label("سال / ماه"))
        filt = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="48dp", spacing="6dp")
        self.year_f = MDTextField(text=str(current_jalali_year()), size_hint_x=0.35, font_name=F)
        self.month_f = MDTextField(text=f"{current_jalali_month():02d}", size_hint_x=0.35, font_name=F)
        filt.add_widget(self.year_f)
        filt.add_widget(self.month_f)
        filt.add_widget(MDButton(
            MDButtonText(text=rtl("نمايش"), font_name=F), style="filled", size_hint_x=0.3,
            on_release=lambda x: self._load(),
        ))
        outer.add_widget(filt)

        scroll = MDScrollView()
        self.list_box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="4dp", padding="4dp")
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        outer.add_widget(scroll)

        outer.add_widget(field_label("تاريخ"))
        self.edit_date = MDTextField(font_name=F)
        outer.add_widget(self.edit_date)
        outer.add_widget(field_label("اسکله"))
        self.edit_jetty = MDTextField(font_name=F)
        outer.add_widget(self.edit_jetty)

        btns = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="44dp", spacing="8dp")
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("ذخيره"), font_name=F), style="filled", size_hint_x=0.5,
            on_release=lambda x: self._save(),
        ))
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("حذف"), font_name=F), style="outlined", size_hint_x=0.5,
            on_release=lambda x: self._delete(),
        ))
        outer.add_widget(btns)
        self.status = MDLabel(text="", size_hint_y=None, height="28dp", halign="center", font_name=F)
        outer.add_widget(self.status)
        self.add_widget(outer)

    def on_enter(self, *args):
        self._load()

    def _load(self):
        self.list_box.clear_widgets()
        self._selected_id = None
        year = (self.year_f.text or "").strip()
        month = (self.month_f.text or "").strip()
        if not year or not month:
            return
        self._rows = App.get_running_app().db.get_employees_by_month(year, month)
        if not self._rows:
            self.list_box.add_widget(MDLabel(
                text=rtl("داده اي وجود ندارد"), size_hint_y=None, height="40dp",
                halign="center", font_name=F,
            ))
            return
        for row in self._rows:
            eid, name, pnum, etype, date, jetty = row
            btn = MDButton(
                MDButtonText(text=rtl(f"{name} | {pnum} | {date} | {jetty}"), font_name=F),
                style="tonal", size_hint_x=1, size_hint_y=None, height="44dp",
                on_release=lambda x, r=row: self._select(r),
            )
            self.list_box.add_widget(btn)

    def _select(self, row):
        self._selected_id = row[0]
        self.edit_date.text = row[4]
        self.edit_jetty.text = row[5]
        self.status.text = rtl(f"انتخاب: {row[1]}")

    def _save(self):
        if not self._selected_id:
            self.status.text = rtl("ابتدا يک رديف را انتخاب کنيد")
            return
        date = (self.edit_date.text or "").strip()
        jetty = (self.edit_jetty.text or "").strip()
        ok, msg = App.get_running_app().db.update_employee(self._selected_id, date, jetty)
        self.status.text = rtl(msg)
        if ok:
            self._load()

    def _delete(self):
        if not self._selected_id:
            self.status.text = rtl("ابتدا يک رديف را انتخاب کنيد")
            return
        App.get_running_app().db.delete_employee(self._selected_id)
        self.status.text = rtl("حذف شد")
        self._selected_id = None
        self.edit_date.text = ""
        self.edit_jetty.text = ""
        self._load()
