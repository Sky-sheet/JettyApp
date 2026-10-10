# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.scrollview import MDScrollView
from kivy.app import App
from utils.helpers import today_jalali, normalize_jetty
from utils.rtl import rtl

F = "Roboto"


def field_label(text):
    return MDLabel(
        text=rtl(text), halign="right", size_hint_y=None, height="26dp",
        font_name=F, theme_text_color="Secondary",
    )


class RegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "register"
        self.jetty = "اسکله شرقي"

        outer = MDBoxLayout(orientation="vertical", padding="8dp", spacing="4dp")
        outer.add_widget(MDButton(
            MDButtonText(text=rtl("بازگشت"), font_name=F),
            style="text", size_hint_x=1,
            on_release=lambda x: setattr(self.manager, "current", "home"),
        ))

        scroll = MDScrollView()
        form = MDBoxLayout(orientation="vertical", padding="16dp", spacing="6dp",
                           size_hint_y=None, height="560dp")

        form.add_widget(MDLabel(text=rtl("ثبت کارمند"), halign="center",
                                size_hint_y=None, height="36dp", font_name=F))

        form.add_widget(field_label("شماره پرسنلي (6 رقم)"))
        self.pnum_field = MDTextField(input_filter="int", font_name=F)
        self.pnum_field.bind(text=self._on_pnum)
        form.add_widget(self.pnum_field)

        form.add_widget(field_label("نام و نام خانوادگي"))
        self.name_field = MDTextField(font_name=F)
        form.add_widget(self.name_field)

        form.add_widget(field_label("نوع استخدام (رسمي / قراردادي)"))
        self.emp_type_field = MDTextField(font_name=F)
        form.add_widget(self.emp_type_field)

        form.add_widget(field_label("تاريخ (YYYY/MM/DD)"))
        self.date_field = MDTextField(text=today_jalali(), font_name=F)
        form.add_widget(self.date_field)

        form.add_widget(field_label("انتخاب اسکله"))
        form.add_widget(MDButton(
            MDButtonText(text=rtl("اسکله شرقي"), font_name=F), style="tonal", size_hint_x=1,
            on_release=lambda x: self._set_jetty("اسکله شرقي"),
        ))
        form.add_widget(MDButton(
            MDButtonText(text=rtl("اسکله غربي"), font_name=F), style="tonal", size_hint_x=1,
            on_release=lambda x: self._set_jetty("اسکله غربي"),
        ))
        self.jetty_label = MDLabel(text=rtl("انتخاب شده: اسکله شرقي"), size_hint_y=None, height="28dp",
                                   halign="center", font_name=F)
        form.add_widget(self.jetty_label)

        form.add_widget(MDButton(
            MDButtonText(text=rtl("ثبت"), font_name=F), style="filled", size_hint_x=1, on_release=self._save,
        ))
        self.status = MDLabel(text="", halign="center", size_hint_y=None, height="36dp", font_name=F)
        form.add_widget(self.status)

        scroll.add_widget(form)
        outer.add_widget(scroll)
        self.add_widget(outer)

    def on_enter(self, *args):
        self.date_field.text = today_jalali()
        self.pnum_field.text = ""
        self.name_field.text = ""
        self.emp_type_field.text = ""
        self.status.text = ""

    def _set_jetty(self, v):
        self.jetty = v
        self.jetty_label.text = rtl(f"انتخاب شده: {v}")

    def _on_pnum(self, instance, value):
        if len(value) == 6:
            emp = App.get_running_app().db.get_employee_by_personnel(value)
            if emp:
                self.name_field.text = emp[0]
                self.emp_type_field.text = emp[2]

    def _save(self, *args):
        pnum = (self.pnum_field.text or "").strip()
        name = (self.name_field.text or "").strip()
        emp_type = (self.emp_type_field.text or "").strip()
        date = (self.date_field.text or "").strip()
        jetty = normalize_jetty(self.jetty)
        if not all([pnum, name, emp_type, date]):
            self.status.text = rtl("همه فيلدها را پر کنيد")
            return
        if not (pnum.isdigit() and len(pnum) == 6):
            self.status.text = rtl("شماره پرسنلي بايد 6 رقم باشد")
            return
        ok, msg = App.get_running_app().db.register_employee(name, pnum, emp_type, date, jetty)
        self.status.text = rtl(msg)
        if ok:
            self.pnum_field.text = ""
            self.name_field.text = ""
            self.emp_type_field.text = ""
            self.date_field.text = today_jalali()
