import unittest
import io
import sys

from simc.parser.array_parser import array_initializer
from simc.token_class import Token
from simc.symbol_table import SymbolTable

class TestArrayParser(unittest.TestCase):

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

    def __test_error_case(self, tokens_list, table=None):
        if table == None:
            table = SymbolTable()  
            
        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _, _ = array_initializer(tokens=tokens_list, i=1, table=table, size_of_array=2, msg="Test message")

        self.__release_print()

    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test_array_initializer_missing_left_brace(self):
        tokens_list = [Token("assignment", "", 1), Token("right_brace", "", 1)]

        self.__test_error_case(tokens_list)        

    def test_array_initializer_missing_too_many_initializers(self):
        tokens_list = [Token("assignment", "", 1), Token("left_brace", "", 1), Token('number', 3, 1), 
                       Token('comma', '', 1), Token('number', 4, 1), Token('comma', '', 1),
                       Token('number', 5, 1)]
        
        self.__test_error_case(tokens_list)

    def test_array_initializer_missing_missing_comma_separator(self):
        tokens_list = [Token("assignment", "", 1), Token("left_brace", "", 1), Token('number', 3, 1), 
                       Token('number', 4, 1), Token('comma', '', 1),
                       Token('number', 5, 1), Token("right_brace", "", 1)]
        
        self.__test_error_case(tokens_list)

    def test_array_initializer_missing_too_many_unique_types(self):
        tokens_list = [Token("assignment", "", 1), Token("left_brace", "", 1), Token('number', 1, 1), 
                       Token('comma', '', 1), Token('number', 2, 1), Token("right_brace", "", 1)]
        table = SymbolTable()
        table.entry("1", "int", "variable")
        table.entry("3.14", "float", "variable")

        self.__test_error_case(tokens_list, table)

    def test_array_initializer_missing_cannot_find_type(self):
        tokens_list = [Token("assignment", "", 1), Token("left_brace", "", 1), Token('number', 1, 1), 
                       Token('comma', '', 1), Token('number', 2, 1), Token("right_brace", "", 1)]
        table = SymbolTable()
        table.entry("1", "var", "variable")
        table.entry("3.14", "var", "variable")

        self.__test_error_case(tokens_list, table)

    def test_array_initializer_missing_no_ending_right_brace(self):
        tokens_list = [Token("assignment", "", 1), Token("left_brace", "", 1), Token('number', 1, 1), 
                       Token('comma', '', 1), Token('number', 2, 1)]

        self.__test_error_case(tokens_list)

    def test_array_initializer_missing_no_errors(self):
        tokens_list = [Token("assignment", "", 1), Token("left_brace", "", 1), Token('number', 1, 1), 
                       Token('comma', '', 1), Token('number', 2, 1), Token("right_brace", "", 1)]
        table = SymbolTable()
        table.entry("1", "int", "variable")
        table.entry("2", "int", "variable")

        op_value, op_type, i = array_initializer(tokens=tokens_list, i=1, table=table, size_of_array=2, msg="Test message")

        self.assertEqual(op_value, "{1,2")
        self.assertEqual(op_type, 3)