import unittest
from new1 import game as g
class TestStringMethods(unittest.TestCase):

    def test_tic_tac_toe_blocker(self):
        self.assertEqual(g().tic_tac_toe_blocker(1,2), {3})

if __name__ == '__main__':
    unittest.main()