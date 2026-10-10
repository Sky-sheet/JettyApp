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


class UsersScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "users"
        self._old_user = None

        outer = MDBoxLayout(orientation="vertical", padding="8dp", spacing="4dp")
        outer.add_widget(MDButton(
            MDButtonText(text=rtl("بازگشت"), font_name=F), style="text", size_hint_x=1,
            on_release=lambda x: setattr(self.manager, "current", "home"),
        ))
        outer.add_widget(MDLabel(text=rtl("مديريت کاربران"), halign="center",
                                 size_hint_y=None, height="36dp", font_name=F))

        scroll = MDScrollView(size_hint_y=0.4)
        self.list_box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="4dp")
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        outer.add_widget(scroll)

        outer.add_widget(field_label("نام کاربري"))
        self.user_f = MDTextField(font_name=F)
        outer.add_widget(self.user_f)

        outer.add_widget(field_label("رمز عبور"))
        self.pwd_f = MDTextField(password=True, font_name=F)
        outer.add_widget(self.pwd_f)

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
        outer.add_widget(btns)
        self.status = MDLabel(text="", size_hint_y=None, height="28dp", halign="center", font_name=F)
        outer.add_widget(self.status)
        self.add_widget(outer)

    def on_enter(self, *args):
        self._load()

    def _load(self):
        self.list_box.clear_widgets()
        app = App.get_running_app()
        users = app.db.get_users()
        for u, _ in users:
            if app.current_user != "Administrator" and u == "Administrator":
                continue
            btn = MDButton(
                MDButtonText(text=rtl(u), font_name=F),
                style="tonal", size_hint_x=1, size_hint_y=None, height="44dp",
                on_release=lambda x, name=u: self._select(name),
            )
            self.list_box.add_widget(btn)

    def _select(self, name):
        self.user_f.text = name
        self.pwd_f.text = ""
        self._old_user = name
        self.status.text = rtl(f"انتخاب: {name}")

    def _add(self):
        u = (self.user_f.text or "").strip()
        p = (self.pwd_f.text or "").strip()
        if not u or not p:
            self.status.text = rtl("نام و رمز را وارد کنيد")
            return
        ok = App.get_running_app().db.add_user(u, p)
        self.status.text = rtl("ثبت شد" if ok else "اين نام کاربري وجود دارد")
        if ok:
            self.user_f.text = ""
            self.pwd_f.text = ""
            self._old_user = None
            self._load()

    def _edit(self):
        if not self._old_user:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        new_u = (self.user_f.text or "").strip()
        new_p = (self.pwd_f.text or "").strip()
        if not new_u:
            self.status.text = rtl("نام کاربري خالي است")
            return
        ok = App.get_running_app().db.update_user(self._old_user, new_u, new_p or None)
        self.status.text = rtl("ويرايش شد" if ok else "خطا")
        if ok:
            self._old_user = new_u
            self._load()

    def _delete(self):
        name = self._old_user or (self.user_f.text or "").strip()
        if not name:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        if name == "Administrator":
            self.status.text = rtl("Administrator قابل حذف نيست")
            return
        ok = App.get_running_app().db.delete_user(name)
        self.status.text = rtl("حذف شد" if ok else "خطا")
        self.user_f.text = ""
        self.pwd_f.text = ""
        self._old_user = None
        self._load()
