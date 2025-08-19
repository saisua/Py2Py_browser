import unittest
from db.base import Base


class TestBase(unittest.TestCase):
    def test_base_class(self):
        self.assertTrue(hasattr(Base, 'metadata'))
