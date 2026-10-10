# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDButton, MDButtonText
from kivy.app import App
from utils.rtl import rtl

F = "Roboto"


def field_label(text):
    return MDLabel(
        text=rtl(text), halign="right", size_hint_y=None, height="28dp",
        font_name=F, theme_text_color="Secondary",
    )


class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"

        root = MDBoxLayout(orientation="vertical", padding="24dp", spacing="8dp")

        root.add_widget(MDLabel(
            text=rtl("فوق العاده اسکله ها"),
            halign="center", size_hint_y=None, height="50dp",
            theme_text_color="Custom", text_color=(0.8, 0.1, 0.1, 1),
            font_name=F, font_size="22sp",
        ))
        root.add_widget(MDLabel(
            text=rtl("اسکله شرقي / اسکله غربي"),
            halign="center", size_hint_y=None, height="28dp",
            theme_text_color="Secondary", font_name=F,
        ))

        root.add_widget(field_label("نام کاربري"))
        self.username = MDTextField(hint_text="", size_hint_x=1, font_name=F)
        root.add_widget(self.username)

        root.add_widget(field_label("رمز عبور"))
        self.password = MDTextField(hint_text="", password=True, size_hint_x=1, font_name=F)
        root.add_widget(self.password)

        root.add_widget(MDButton(
            MDButtonText(text=rtl("ورود"), font_name=F),
            style="filled", size_hint_x=1, on_release=self._do_login,
        ))

        self.error_label = MDLabel(
            text="", halign="center", size_hint_y=None, height="40dp",
            theme_text_color="Error", font_name=F,
        )
        root.add_widget(self.error_label)

        root.add_widget(MDLabel(
            text=rtl("طراحي: عليرضا برادران | نسخه 1.0"),
            halign="center", size_hint_y=None, height="30dp",
            theme_text_color="Secondary", font_name=F,
        ))
        self.add_widget(root)

    def _do_login(self, *args):
        user = (self.username.text or "").strip()
        pwd = (self.password.text or "").strip()
        if not user or not pwd:
            self.error_label.text = rtl("نام کاربري و رمز را وارد کنيد")
            return
        app = App.get_running_app()
        try:
            if app.db.check_login(user, pwd):
                app.current_user = user
                self.error_label.text = ""
                self.manager.current = "main"
            else:
                self.error_label.text = rtl("نام کاربري يا رمز اشتباه است")
        except Exception as e:
            self.error_label.text = rtl(f"خطا: {e}")
