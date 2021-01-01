import unittest
import os
import sys
import io

from simc.global_helpers import *

class TestGlobalHelpers(unittest.TestCase):

    ####################################################################################################
    # HELPERS
    ####################################################################################################

    def __suppress_print(self):
        # Suppress print
        suppress_text = io.StringIO()
        sys.stdout = suppress_text 

    def __release_print(self):
        # Release print
        sys.stdout = sys.__stdout__

    ####################################################################################################
    # TESTS
    ####################################################################################################

    def test_check_if_error_case(self):
        self.__suppress_print()

        # Case when check_if fails and calls error which calls sys.exit()
        with self.assertRaises(SystemExit):
            check_if("left_paren", "right_paren", "Expected (", 1)

        self.__release_print()

    def test___keyword_identifier_success_case(self):
        # Case when check_if passes thus returning None
        self.assertEqual(check_if("print", "print", "Expected print", 100), None)

    def test_error(self):
        self.__suppress_print()

        # error calls sys.exit()
        with self.assertRaises(SystemExit):
            error("Some error message", 1)

        self.__release_print()

    def test_is_digit_true_cases(self):
        # True cases
        self.assertEqual(is_digit("1"), True)
        self.assertEqual(is_digit("."), True)

    def test_is_digit_false_cases(self):
        # False cases
        self.assertEqual(is_digit("a"), False)
        self.assertEqual(is_digit("*"), False)

    def test_is_alpha_true_cases(self):
        # True cases
        self.assertEqual(is_alpha("a"), True)
        self.assertEqual(is_alpha("Z"), True)
        self.assertEqual(is_alpha("_"), True)

    def test_is_alpha_false_cases(self):
        # False cases
        self.assertEqual(is_alpha("1"), False)
        self.assertEqual(is_alpha("."), False)
        self.assertEqual(is_alpha("+"), False)

    def test_is_alnum_true_cases(self):
        # True cases
        self.assertEqual(is_alnum("a"), True)
        self.assertEqual(is_alnum("Z"), True)
        self.assertEqual(is_alnum("_"), True)
        self.assertEqual(is_alnum("1"), True)
        self.assertEqual(is_alnum("."), True)

    def test_is_alnum_false_cases(self):
        # False cases
        self.assertEqual(is_alnum("+"), False)
        self.assertEqual(is_alnum("*"), False)