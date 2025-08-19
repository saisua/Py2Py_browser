import unittest
from communication.concurrency_layers import (
    ThreadLayer,
    ProcessLayer,
    MainThreadLayer,
)


class TestConcurrencyLayers(unittest.TestCase):
    def test_thread_layer(self):
        layer1 = ThreadLayer(1)
        layer2 = ThreadLayer(2)
        layer1_same = ThreadLayer(1)

        self.assertTrue(layer1.must_lock(layer2))
        self.assertFalse(layer1.must_lock(layer1_same))

    def test_process_layer(self):
        layer1 = ProcessLayer(1)
        layer2 = ProcessLayer(2)
        layer1_same = ProcessLayer(1)

        self.assertTrue(layer1.must_lock(layer2))
        self.assertFalse(layer1.must_lock(layer1_same))

    def test_main_thread_layer(self):
        layer = MainThreadLayer()
        self.assertEqual(layer.id, 0)
        self.assertIsInstance(layer, ThreadLayer)
