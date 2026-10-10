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


class TaskRegisterScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "task_register"
        self.jetty = "اسکله شرقي"

        root = MDBoxLayout(orientation="vertical", padding="12dp", spacing="8dp")
        root.add_widget(MDButton(
            MDButtonText(text=rtl("بازگشت"), font_name=F), style="text", size_hint_x=1,
            on_release=lambda x: setattr(self.manager, "current", "home"),
        ))
        root.add_widget(MDLabel(text=rtl("ثبت شرح کار تعميراتي"), halign="center",
                                size_hint_y=None, height="36dp", font_name=F))

        root.add_widget(field_label("شرح کار"))
        self.desc = MDTextField(multiline=True, size_hint_y=None, height="120dp", font_name=F)
        root.add_widget(self.desc)

        root.add_widget(field_label("انتخاب اسکله"))
        root.add_widget(MDButton(
            MDButtonText(text=rtl("اسکله شرقي"), font_name=F), style="tonal", size_hint_x=1,
            on_release=lambda x: self._set("اسکله شرقي"),
        ))
        root.add_widget(MDButton(
            MDButtonText(text=rtl("اسکله غربي"), font_name=F), style="tonal", size_hint_x=1,
            on_release=lambda x: self._set("اسکله غربي"),
        ))
        self.jetty_lbl = MDLabel(text=rtl("انتخاب شده: اسکله شرقي"), size_hint_y=None, height="28dp",
                                 halign="center", font_name=F)
        root.add_widget(self.jetty_lbl)

        root.add_widget(MDButton(
            MDButtonText(text=rtl("ثبت شرح کار"), font_name=F), style="filled", size_hint_x=1,
            on_release=self._save,
        ))
        self.status = MDLabel(text="", size_hint_y=None, height="36dp", halign="center", font_name=F)
        root.add_widget(self.status)
        self.add_widget(root)

    def _set(self, v):
        self.jetty = v
        self.jetty_lbl.text = rtl(f"انتخاب شده: {v}")

    def _save(self, *args):
        desc = (self.desc.text or "").strip()
        if not desc:
            self.status.text = rtl("شرح کار را وارد کنيد")
            return
        App.get_running_app().db.add_task(desc, normalize_jetty(self.jetty), today_jalali())
        self.status.text = rtl("شرح کار ثبت شد")
        self.desc.text = ""


class TaskEditScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "task_edit"
        self._selected_id = None

        outer = MDBoxLayout(orientation="vertical", padding="8dp", spacing="4dp")
        outer.add_widget(MDButton(
            MDButtonText(text=rtl("بازگشت"), font_name=F), style="text", size_hint_x=1,
            on_release=lambda x: setattr(self.manager, "current", "home"),
        ))
        outer.add_widget(MDLabel(text=rtl("ويرايش شرح کار"), halign="center",
                                 size_hint_y=None, height="36dp", font_name=F))

        scroll = MDScrollView()
        self.list_box = MDBoxLayout(orientation="vertical", size_hint_y=None, spacing="4dp")
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)
        outer.add_widget(scroll)

        outer.add_widget(field_label("شرح کار"))
        self.edit_desc = MDTextField(multiline=True, size_hint_y=None, height="80dp", font_name=F)
        outer.add_widget(self.edit_desc)
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
        rows = App.get_running_app().db.get_tasks()
        if not rows:
            self.list_box.add_widget(MDLabel(
                text=rtl("داده اي وجود ندارد"), size_hint_y=None, height="40dp",
                halign="center", font_name=F,
            ))
            return
        for row in rows:
            btn = MDButton(
                MDButtonText(text=rtl(f"{row[2]} | {row[1][:40]}"), font_name=F),
                style="tonal", size_hint_x=1, size_hint_y=None, height="44dp",
                on_release=lambda x, r=row: self._select(r),
            )
            self.list_box.add_widget(btn)

    def _select(self, row):
        self._selected_id = row[0]
        self.edit_desc.text = row[1]
        self.edit_jetty.text = row[2]
        self.status.text = rtl("انتخاب شد")

    def _save(self):
        if not self._selected_id:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        desc = (self.edit_desc.text or "").strip()
        jetty = normalize_jetty((self.edit_jetty.text or "").strip())
        if not desc:
            self.status.text = rtl("شرح کار خالي است")
            return
        App.get_running_app().db.update_task(self._selected_id, desc, jetty)
        self.status.text = rtl("ذخيره شد")
        self._load()

    def _delete(self):
        if not self._selected_id:
            self.status.text = rtl("ابتدا انتخاب کنيد")
            return
        App.get_running_app().db.delete_task(self._selected_id)
        self.status.text = rtl("حذف شد")
        self._selected_id = None
        self.edit_desc.text = ""
        self.edit_jetty.text = ""
        self._load()
