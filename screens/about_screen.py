# -*- coding: utf-8 -*-
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from utils.rtl import rtl

F = "Roboto"


class AboutScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "about"
        root = MDBoxLayout(orientation="vertical", padding="20dp", spacing="12dp")
        root.add_widget(MDButton(
            MDButtonText(text=rtl("بازگشت"), font_name=F), style="text", size_hint_x=1,
            on_release=lambda x: setattr(self.manager, "current", "home"),
        ))
        for line in [
            "نرم افزار ثبت فوق العاده اسکله ها",
            "طراحي: عليرضا برادران",
            "نسخه موبايل: 1.0.0",
            "تاريخ: فروردين 1404",
            "eng.alireza86@gmail.com",
            "",
            "نسخه Kivy/KivyMD براي اندرويد",
        ]:
            root.add_widget(MDLabel(
                text=rtl(line) if line else "",
                halign="center", size_hint_y=None, height="32dp", font_name=F,
            ))
        self.add_widget(root)
