from typing import Callable
import asyncio
import logging

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, BooleanProperty
from kivy.animation import Animation

from config import (
    logger,
    chats,
    MAX_CHAT_BUTTON_LENGTH,
)


class MenuItem(Button):
    def __init__(self, text: str, image_source: str = None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (80, 80)
        self.background_normal = ''
        self.background_color = (0.2, 0.6, 1, 1)

        self.text = text
        self.image_source = image_source

    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=5)

        if self.image_source:
            img = Image(source=self.image_source, size_hint=(1, 0.7))
            layout.add_widget(img)

        label = Label(text=self.text, size_hint=(1, 0.3), font_size='12sp')
        layout.add_widget(label)

        self.add_widget(layout)

        return self


class ExpandableMenu(BoxLayout):
    is_expanded = BooleanProperty(False)

    expanded_width = NumericProperty(200)
    collapsed_width = NumericProperty(80)

    menu_items: dict

    def __init__(
        self,
        app: "SocialApp",  # type: ignore # noqa: F821
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.app = app

        self.orientation = 'horizontal'
        self.size_hint_x = None
        self.width = self.collapsed_width

        self.menu_items = dict()

    def build(self):
        # Menu toggle button
        self.toggle_button = ToggleButton(
            text='☰',
            size_hint=(None, None),
            size=(40, 40),
            pos_hint={'center_y': 0.5},
            group='menu_toggle'
        )
        self.toggle_button.bind(state=self.on_toggle)

        # Menu container
        self.menu_container = ScrollView(
            size_hint=(None, 1),
            width=self.collapsed_width,
            do_scroll_x=False
        )

        self.menu_grid = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.menu_grid.bind(minimum_height=self.menu_grid.setter('height'))
        self.menu_container.add_widget(self.menu_grid)

        self.add_widget(self.menu_container)
        self.add_widget(self.toggle_button)

        for chat in chats:
            self.add_item(
                chat,
                self._change_chat_callback(chat)
            )

        return self

    def _change_chat_callback(self, chat):
        def __change_chat_callback(*args):
            self.app._task_refs.append(
                asyncio.create_task(self.app.chat.change_chat(chat))
            )

        return __change_chat_callback

    def add_item(
            self,
            text: str,
            callback: Callable = None,
            image_source: str = None,
    ):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Adding menu item: {text}")

        if len(text) > MAX_CHAT_BUTTON_LENGTH:
            text = text[:MAX_CHAT_BUTTON_LENGTH]

        item = MenuItem(text=text, image_source=image_source).build()
        if self.is_expanded:
            item.width = self.expanded_width
        else:
            item.width = self.collapsed_width

        if callback:
            item.bind(on_press=callback)
        self.menu_grid.add_widget(item)
        self.menu_grid.height = len(self.menu_grid.children) * 90

        self.menu_items['text'] = item

    def set_item(
        self,
        index: int,
        text: str,
        callback: Callable = None,
        image_source: str = None,
    ):
        item = self.menu_grid.children[index]
        item.text = text
        item.image_source = image_source
        if callback:
            item.bind(on_press=callback)

    def on_toggle(self, instance, state):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Toggling menu: {state}")
        if self.is_expanded:
            self.collapse_menu()
        else:
            self.expand_menu()

    def expand_menu(self):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Expanding menu")
        self.is_expanded = True
        anim = Animation(width=self.expanded_width, duration=0.2)
        anim.start(self)
        anim.start(self.menu_container)
        anim.start(self.menu_grid)
        for child in self.menu_grid.children:
            if hasattr(child, 'width'):
                anim.start(child)

    def collapse_menu(self):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Collapsing menu")
        self.is_expanded = False
        anim = Animation(width=self.collapsed_width, duration=0.2)
        anim.start(self)
        anim.start(self.menu_container)
        anim.start(self.menu_grid)
        for child in self.menu_grid.children:
            if hasattr(child, 'width'):
                anim.start(child)
