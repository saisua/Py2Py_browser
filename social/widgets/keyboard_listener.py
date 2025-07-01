import logging

from kivy.core.window import Window
from kivy.uix.widget import Widget

from config import (
    logger,
)


class KeyboardListener(Widget):
    def __init__(self, app, **kwargs):
        super(KeyboardListener, self).__init__(**kwargs)

        self.app = app

        self._keyboard = Window.request_keyboard(
            self._keyboard_closed,
            self,
            ''
        )
        if self._keyboard.widget:
            pass

        self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        if logger.isEnabledFor(logging.INFO):
            logger.info('My keyboard have been closed!')

        if not self.app._closed:
            return

        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_up(self, keyboard, keycode):
        match keycode[0]:
            case 13:
                self.app.chat.send_message(None)
            case _:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'Unassigned keycode {keycode}')
                return False

        return True
