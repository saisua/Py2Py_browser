import asyncio
import os
import logging

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from config import (
    logger,
    chat_dir,
)

from files.social.store_msg_to_disk import store_msg_to_disk

from social.utils.load_all_chat_msgs import load_all_chat_msgs
from social.utils.get_user_color import get_user_hash_color
from utils.hash_str import _hash_str


class Chat(BoxLayout):
    app: "SocialApp"  # type: ignore # noqa: F821

    def __init__(
        self,
        app: "SocialApp",  # type: ignore # noqa: F821
        chat: str,
        **kwargs,
    ):
        super(Chat, self).__init__(**kwargs)

        self.app = app
        self._chat = chat

    def build(self):
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        self.chat_scroll = ScrollView(
            size_hint=(1, 0.9),
            bar_width=10,
            bar_color=(0.8, 0.8, 0.8, 1),
            bar_inactive_color=(0.6, 0.6, 0.6, 1)
        )
        self.chat_layout = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)

        # Input area with rounded corners
        self.message_input = TextInput(
            hint_text='Type a message...',
            size_hint_y=None,
            height=60,
            multiline=False,
            background_color=(1, 1, 1, 0.8),
            foreground_color=(0, 0, 0, 1),
            padding=10,
            font_size=16
        )

        # Styled send button
        self.send_button = Button(
            text='Send',
            size_hint_y=None,
            height=60,
            background_color=(0.2, 0.6, 1, 1),
            background_normal='',
            font_size=16,
            bold=True
        )
        self.send_button.bind(on_press=self.send_message)

        # Input layout with some spacing
        input_layout = BoxLayout(
            size_hint_y=None,
            height=60,
            spacing=10,
            padding=(0, 0, 0, 5)
        )
        input_layout.add_widget(self.message_input)
        input_layout.add_widget(self.send_button)

        # Add widgets to main layout
        self.add_widget(self.chat_scroll)
        self.add_widget(input_layout)

        if self._chat:
            self.app._task_refs.append(
                asyncio.create_task(
                    self.change_chat(self._chat)
                )
            )

        return self

    async def async_send_message(
        self,
        user: str,
        message: str,
        chat: str,
        *,
        pos: int | None = None,
        store: bool = True,
    ):
        if logger.isEnabledFor(logging.INFO):
            logger.info(f"Sending message: {user}: {message}")

        if user == self.app._user:
            label = Label(
                text=message,
                size_hint_y=None,
                height=30,
                halign='left',
                valign='middle',
                markup=True,
            )
        else:
            label = Label(
                text=f'{user}: {message}',
                size_hint_y=None,
                height=30,
                halign='right',
                valign='middle',
                color=get_user_hash_color(user),
                markup=True,
            )
        label.bind(
            size=lambda label, pos: label.setter('text_size')(label.size, pos)
        )

        if (
            self.chat_scroll.scroll_y > self.chat_scroll.height
            or  # noqa: W503 W504
            not self.chat_layout.children
        ):
            self.chat_scroll.scroll_y = 0

        if pos is not None:
            self.chat_layout.children.insert(pos, label)
        else:
            self.chat_layout.add_widget(label)

        if store:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Storing message")
            chat_hash = _hash_str(chat)

            os.makedirs(os.path.join(chat_dir, chat_hash), exist_ok=True)

            self.app._task_refs.append(
                asyncio.create_task(
                    store_msg_to_disk(
                        {
                            'user': user,
                            'message': message,
                        },
                        chat=chat,
                    )
                )
            )

    def send_message(
        self,
        instance,
        *,
        user: str | None = None,
        chat: str | None = None,
    ):
        if user is None:
            user = self.app._user

        if chat is None:
            chat = self._chat

        message = self.message_input.text.strip()
        if message:
            self.app._task_refs.append(
                asyncio.create_task(
                    self.async_send_message(user, message, chat=chat)
                )
            )
            self.message_input.text = ''

    def clear_messages(self):
        self.chat_layout.clear_widgets()

    async def send_messages(
        self,
        messages: list[dict[str, str]],
        chat: str | None = None,
        *,
        reverse: bool = False,
        clear: bool = False,
    ):
        if chat is None:
            chat = self._chat

        if clear:
            self.clear_messages()

        if reverse:
            pos = -1
            for message in messages:
                await self.async_send_message(
                    message['user'],
                    message['message'],
                    chat,
                    pos=pos,
                    store=False,
                )
                pos -= 1
        else:
            for message in messages:
                await self.async_send_message(
                    message['user'],
                    message['message'],
                    chat,
                    store=False,
                )

    async def reload_chat(self, *, request: bool = True):
        if logger.isEnabledFor(logging.INFO):
            logger.info("Reloading chat")
        chat_hash = _hash_str(self._chat)
        await load_all_chat_msgs(self, chat_hash, request=request)

    async def change_chat(
        self,
        chat: str,
        *,
        force: bool = False,
        request: bool = True,
    ) -> bool:
        if (
            not force and  # noqa: W504
            chat == self._chat and  # noqa: W504
            len(self.chat_layout.children) != 0
        ):
            return False

        if logger.isEnabledFor(logging.INFO):
            logger.info(f"Changing chat to {chat}")

        self._chat = chat
        await self.reload_chat(request=request)

        return True
