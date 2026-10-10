# -*- coding: utf-8 -*-
"""فوق العاده اسکله ها - نسخه ساده موبایل (6 تب)"""

import sys
import os
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

Window.size = (400, 720)

def register_persian_font():
    for path in [
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        str(BASE_DIR / "assets" / "Vazir.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if os.path.isfile(path):
            try:
                LabelBase.register(name="Roboto", fn_regular=path)
                LabelBase.register(name="RobotoMedium", fn_regular=path)
                LabelBase.register(name="RobotoBold", fn_regular=path)
                LabelBase.register(name="PersianFont", fn_regular=path)
                print(f"[INFO] Font: {path}")
                return
            except Exception as e:
                print(f"[WARN] {e}")
    print("[WARN] No Persian font")


class JettyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "فوق العاده اسکله ها"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.current_user = None
        self.db = None

    def build(self):
        register_persian_font()
        try:
            from utils.database import Database
            from utils.helpers import get_data_dir
            from screens.login_screen import LoginScreen
            from screens.main_tabs import MainTabsScreen

            data_dir = get_data_dir(self)
            self.db = Database(str(data_dir / "entries.db"))
            print(f"[INFO] DB: {data_dir / 'entries.db'}")

            sm = MDScreenManager()
            sm.add_widget(LoginScreen())
            sm.add_widget(MainTabsScreen())
            return sm
        except Exception as e:
            traceback.print_exc()
            from kivymd.uix.screen import MDScreen
            from kivymd.uix.label import MDLabel
            s = MDScreen()
            s.add_widget(MDLabel(text=f"Error: {e}", halign="center"))
            return s


if __name__ == "__main__":
    try:
        JettyApp().run()
    except Exception:
        traceback.print_exc()
        input("Enter...")
