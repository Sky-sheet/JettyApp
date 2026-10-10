# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.scrollview import MDScrollView
from kivy.app import App
from utils.rtl import rtl

F = "Roboto"


def field_label(text):
    return MDLabel(
        text=rtl(text), halign="right", size_hint_y=None, height="26dp",
        font_name=F, theme_text_color="Secondary",
    )


class EmpManageScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "emp_manage"
        self._old_pnum = None

        outer = MDBoxLayout(orientation="vertical", padding="8dp", spacing="4dp")
        outer.add_widget(MDButton(
            MDButtonText(text=rtl("بازگشت"), font_name=F), style="text", size_hint_x=1,
            on_release=lambda x: setattr(self.manager, "current", "home"),
        ))
        outer.add_widget(MDLabel(text=rtl("مديريت کارمندان"), halign="center",
                                 size_hint_y=None, height="36dp", font_name=F))

        scroll = MDScrollView(size_hint_y=0.4)
        self.list_box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="4dp")
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        outer.add_widget(scroll)

        outer.add_widget(field_label("نام و نام خانوادگي"))
        self.name_f = MDTextField(font_name=F)
        outer.add_widget(self.name_f)

        outer.add_widget(field_label("شماره پرسنلي (6 رقم)"))
        self.pnum_f = MDTextField(input_filter="int", font_name=F)
        outer.add_widget(self.pnum_f)

        outer.add_widget(field_label("نوع استخدام"))
        self.type_f = MDTextField(font_name=F)
        outer.add_widget(self.type_f)

        btns = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="44dp", spacing="6dp")
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("ثبت/ويرايش"), font_name=F), style="filled", size_hint_x=0.5,
            on_release=lambda x: self._save(),
        ))
        btns.add_widget(MDButton(
            MDButtonText(text=rtl("حذف"), font_name=F), style="outlined", size_hint_x=0.5,
            on_release=lambda x: self._delete(),
        ))
        outer.add_widget(btns)
        outer.add_widget(MDButton(
            MDButtonText(text=rtl("پاک کردن فرم"), font_name=F), style="text", size_hint_x=1,
            on_release=lambda x: self._clear(),
        ))
        self.status = MDLabel(text="", size_hint_y=None, height="28dp", halign="center", font_name=F)
        outer.add_widget(self.status)
        self.add_widget(outer)

    def on_enter(self, *args):
        self._load()

    def _load(self):
        self.list_box.clear_widgets()
        rows = App.get_running_app().db.get_default_employees()
        if not rows:
            self.list_box.add_widget(MDLabel(
                text=rtl("کارمندي ثبت نشده"), size_hint_y=None, height="40dp",
                halign="center", font_name=F,
            ))
            return
        for row in rows:
            btn = MDButton(
                MDButtonText(text=rtl(f"{row[0]} | {row[1]} | {row[2]}"), font_name=F),
                style="tonal", size_hint_x=1, size_hint_y=None, height="44dp",
                on_release=lambda x, r=row: self._select(r),
            )
            self.list_box.add_widget(btn)

    def _select(self, row):
        self.name_f.text = row[0]
        self.pnum_f.text = row[1]
        self.type_f.text = row[2]
        self._old_pnum = row[1]
        self.status.text = rtl(f"انتخاب: {row[0]}")

    def _clear(self):
        self.name_f.text = ""
        self.pnum_f.text = ""
        self.type_f.text = ""
        self._old_pnum = None
        self.status.text = ""

    def _save(self):
        name = (self.name_f.text or "").strip()
        pnum = (self.pnum_f.text or "").strip()
        etype = (self.type_f.text or "").strip()
        if not all([name, pnum, etype]):
            self.status.text = rtl("همه فيلدها را پر کنيد")
            return
        if not (pnum.isdigit() and len(pnum) == 6):
            self.status.text = rtl("شماره پرسنلي بايد 6 رقم باشد")
            return
        db = App.get_running_app().db
        if self._old_pnum:
            ok = db.update_default_employee(self._old_pnum, name, pnum, etype)
            self.status.text = rtl("ويرايش شد" if ok else "خطا در ويرايش")
        else:
            ok = db.add_default_employee(name, pnum, etype)
            self.status.text = rtl("ثبت شد" if ok else "اين شماره قبلا ثبت شده")
        if ok:
            self._clear()
            self._load()

    def _delete(self):
        pnum = (self.pnum_f.text or "").strip() or self._old_pnum
        if not pnum:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        App.get_running_app().db.delete_default_employee(pnum)
        self.status.text = rtl("حذف شد")
        self._clear()
        self._load()
