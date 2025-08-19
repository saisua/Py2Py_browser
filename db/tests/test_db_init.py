import unittest
import asyncio
from db import __init__ as db_init


class TestDbInit(unittest.TestCase):
    def test_setup_database(self):
        async def test():
            engine, session_maker = await db_init.setup_database()
            self.assertIsNotNone(engine)
            self.assertIsNotNone(session_maker)

        asyncio.run(test())
