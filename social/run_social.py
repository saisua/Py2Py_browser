import os
import asyncio
from threading import Thread

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from config import (
	chat_dir,
	suffix,
	username,
	default_chat,
	ENABLE_KEYBOARD_LISTENER,
	BROADCAST,
	CLOSE,
)

from communication.communication import CommunicationUser

from social.widgets.keyboard_listener import KeyboardListener
from social.widgets.menu import ExpandableMenu
from social.widgets.chat import Chat
from social.utils.check_communication import check_communication

from utils.remove_tasks_forever import remove_tasks_forever


class SocialApp(App):
    _task_refs: list
    _del_task_ref: asyncio.Task
    _comm_task_ref: asyncio.Task
    _closed: bool = False

    _comm_user: CommunicationUser

    chat: Chat
    menu: ExpandableMenu

    def __init__(
        self,
        session_maker: "SessionMaker",  # noqa: F821 # type: ignore
        comm_user: CommunicationUser,
        user: str = username,
        chat: str = default_chat,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._session_maker = session_maker

        self._comm_user = comm_user

        os.makedirs(chat_dir, exist_ok=True)

        self.chat = Chat(self, chat=chat)
        self.menu = ExpandableMenu(self)

        self._task_refs = list()
        self._ref_task_del = None

        self._user = user

    def build(self):
        self.title = f"Social{suffix}"

        # Create main horizontal layout
        main_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            padding=10,
        )

        # Build chat and menu components
        self._menu = self.menu.build()
        self._chat = self.chat.build()

        # Add chat and menu to main layout
        main_layout.add_widget(self._menu)
        main_layout.add_widget(self._chat)

        self.layout = main_layout

        if ENABLE_KEYBOARD_LISTENER:
            self._keyboard = KeyboardListener(self)
        else:
            self._keyboard = None

        return self.layout

    async def async_run(self, *args, **kwargs):
        self._del_task_ref = asyncio.create_task(
            remove_tasks_forever(self._task_refs)
        )
        self._comm_task_ref = asyncio.create_task(
            check_communication(self._comm_user, self)
        )

        await super().async_run(*args, **kwargs)

    def run(self):
        # As threading entry point
        self._main_coro = asyncio.run(self.async_run())

    def start(self):
        self._main_thread = Thread(
            target=self.run,
            daemon=True,
        )
        self._main_thread.start()

    def stop(self, *args, **kwargs):
        return self.on_stop(*args, **kwargs)

    def on_stop(self, send_close=True):
        print("Stopping social")
        if not self._closed:
            self._closed = True
            super().stop()
            return

        if send_close:
            self._comm_user.send_message(
                BROADCAST,
                0,
                CLOSE,
                self._comm_user.id,
            )
        return True
