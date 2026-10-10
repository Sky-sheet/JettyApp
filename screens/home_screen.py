# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.scrollview import MDScrollView
from kivy.app import App
from utils.rtl import rtl

F = "Roboto"


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"

        outer = MDBoxLayout(orientation="vertical", padding="12dp", spacing="8dp")

        self.user_label = MDLabel(
            text=rtl("کاربر: -"), halign="center", size_hint_y=None, height="36dp", font_name=F,
        )
        outer.add_widget(self.user_label)
        outer.add_widget(MDLabel(
            text=rtl("منوي اصلي"), halign="center", size_hint_y=None, height="36dp", font_name=F,
        ))

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="8dp", padding="4dp")
        box.bind(minimum_height=box.setter("height"))

        menus = [
            ("ثبت کارمند", "register"),
            ("ويرايش اطلاعات", "edit_list"),
            ("ثبت شرح کار", "task_register"),
            ("ويرايش شرح کار", "task_edit"),
            ("جستجو", "search"),
            ("مديريت کارمندان", "emp_manage"),
            ("خروجی Excel", "export"),
            ("مديريت کاربران", "users"),
            ("درباره", "about"),
            ("خروج", "logout"),
        ]
        for title, action in menus:
            style = "outlined" if action == "logout" else "filled"
            box.add_widget(MDButton(
                MDButtonText(text=rtl(title), font_name=F),
                style=style, size_hint_x=1, size_hint_y=None, height="48dp",
                on_release=lambda x, a=action: self._go(a),
            ))

        scroll.add_widget(box)
        outer.add_widget(scroll)
        self.add_widget(outer)

    def on_enter(self, *args):
        app = App.get_running_app()
        self.user_label.text = rtl(f"کاربر: {getattr(app, 'current_user', '-')}")

    def _go(self, action):
        if action == "logout":
            App.get_running_app().current_user = None
            self.manager.current = "login"
        elif action in self.manager.screen_names:
            self.manager.current = action
        else:
            print(f"Screen not found: {action}")
