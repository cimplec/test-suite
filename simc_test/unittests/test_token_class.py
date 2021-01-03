import unittest

from simc.token_class import Token

class TestTokenClass(unittest.TestCase):

    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test___str__match_case(self):
        token = Token("print", "", 1)

        self.assertEqual(str(token), str(Token("print", "", 1)))

    def test___str__no_match_case(self):
        token = Token("print", "", 1)

        self.assertNotEqual(str(token), str(Token("id", 1, 1)))

    def test___eq__match_case(self):
        token_1 = Token("id", 1, 2)
        token_2 = Token("id", 1, 2)

        self.assertEqual(token_1, token_2)

    def test___eq__no_match_case(self):
        token_1 = Token("id", 1, 2)
        token_2 = Token("print", "", 2)

        self.assertNotEqual(token_1, token_2)