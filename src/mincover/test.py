import unittest
from product import Product


class TestProduct(unittest.TestCase):
    def test_add(self):
        self.assertEqual(Product({0, 1}, size=2) + Product({0, 2}, size=2), Product({0, 1, 2}, size=2))

    def test_str(self):
        self.assertEqual(str(Product({0}, size=3)), '000')
        self.assertEqual(str(Product({1}, size=3)), '001')
        self.assertEqual(str(Product({0, 1}, size=3)), '00-')
        self.assertEqual(str(Product({1, 2}, size=3)), '[001, 010]')

    def test_eq(self):
        self.assertEqual(Product({0, 1}, size=3), Product({0, 1}, size=3))
        self.assertNotEqual(Product({0, 1, 2}, size=3), Product({0, 1, 2}, size=4))
        self.assertNotEqual(Product({0, 1}, size=2), Product({0, 2}, size=2))
        self.assertNotEqual(Product({0, 1}, size=4), Product({1, 2}, size=3))

if __name__ == '__main__':
    unittest.main()
