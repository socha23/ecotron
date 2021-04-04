import unittest

from value_source import multiply, wave_mask

class TestValueSource(unittest.TestCase):

    def test_multiply(self):
        self.assertEqual(multiply(2, 2), 4)
        self.assertEqual(multiply((1, 2, 3), 2), (2, 4, 6))
        self.assertEqual(multiply([1, 2, 3], 2), [2, 4, 6])
        self.assertEqual(multiply([(1, 2), (3, 4)], 2), [(2, 4), (6, 8)])
        self.assertEqual(multiply([1, 2, 3], [4, 5, 6]), [4, 10, 18])
        self.assertEqual(multiply(2, [1, 2, 3]), [2, 4, 6])
        self.assertEqual(multiply((1,2), [1, 2, 3]), [(1,2), (2,4), (3,6)])
        
    def test_wave_mask(self):
        self.assertEqual(
            wave_mask(5, 10, 0),
            [1, 0.5, 0, 0, 0]
        )

        self.assertEqual(
            wave_mask(5, 10, 0, wave_width=4),
            [1, 0.75, 0.5, 0.25, 0]
        )

        self.assertEqual(
            wave_mask(5, 10, 1),
            [0.5, 1, 0.5, 0, 0]
        )

        self.assertEqual(
            wave_mask(10, 7, 0),
            [1, 0.5, 0, 0, 0, 0, 0.5, 1, 0.5, 0]
        )

        self.assertEqual(
            wave_mask(10, 7, 7),
            [1, 0.5, 0, 0, 0, 0, 0.5, 1, 0.5, 0]
        )


        self.assertEqual(
            wave_mask(6, 2, 0),
            [1, 0.5, 1, 0.5, 1, 0.5]
        )


if __name__ == '__main__':
    unittest.main()