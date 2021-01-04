import unittest
import io
import sys

from simc.parser.loop_parser import *
from simc.token_class import Token
from simc.symbol_table import SymbolTable

class TestLoopParser(unittest.TestCase):

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

    def __test_error_case(self, tokens_list, table=None, print_err=False):
        if table == None:
            table = SymbolTable()  
            
        if not print_err:
            self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _, _ = for_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test_for_statement_missing_iterator(self):
        tokens_list = [Token("for", "", 1), Token("print", "", 1)]

        self.__test_error_case(tokens_list)

    def test_for_statement_missing_in_keyword(self):
        tokens_list = [Token("for", "", 1), Token("id", 1, 1), Token("print", "", 1)]

        self.__test_error_case(tokens_list)

    def test_for_statement_missing_starting_value(self):
        tokens_list = [Token("for", "", 1), Token("id", 1, 1), Token("in", "", 1),
                       Token('print', '', 1)]

        self.__test_error_case(tokens_list)

    def test_for_statement_missing_to_keyword(self):
        tokens_list = [Token("for", "", 1), Token("id", 1, 1), Token("in", "", 1),
                       Token('number', 2, 1), Token("print", "", 1)]
        table = SymbolTable()
        table.entry("a", "int", "variable")
        table.entry("1", "int", "variable")

        self.__test_error_case(tokens_list, table=table)

    def test_for_statement_missing_ending_value(self):
        tokens_list = [Token("for", "", 1), Token("id", 1, 1), Token("in", "", 1),
                       Token('number', 2, 1), Token("to", "", 1), Token("print", "", 1)]
        table = SymbolTable()
        table.entry("a", "int", "variable")
        table.entry("1", "int", "variable")

        self.__test_error_case(tokens_list, table=table)

    def test_for_statement_missing_by_keyword(self):
        tokens_list = [Token("for", "", 1), Token("id", 1, 1), Token("in", "", 1),
                       Token('number', 2, 1), Token("to", "", 1), Token("number", 3, 1),
                       Token("print", "", 1)]
        table = SymbolTable()
        table.entry("a", "int", "variable")
        table.entry("1", "int", "variable")
        table.entry("10", "int", "variable")

        self.__test_error_case(tokens_list, table=table)

    def test_for_statement_missing_missing_change_value(self):
        tokens_list = [Token("for", "", 1), Token("id", 1, 1), Token("in", "", 1),
                       Token('number', 2, 1), Token("to", "", 1), Token("number", 3, 1),
                       Token("by", "", 1), Token("plus", "", 1), Token("print", "", 1)]
        table = SymbolTable()
        table.entry("a", "int", "variable")
        table.entry("1", "int", "variable")
        table.entry("10", "int", "variable")

        self.__test_error_case(tokens_list, table=table)

    def test_for_statement_missing_no_errors(self):
        tokens_list = [Token("for", "", 1), Token("id", 1, 1), Token("in", "", 1),
                       Token('number', 2, 1), Token("to", "", 1), Token("number", 3, 1),
                       Token("by", "", 1), Token("plus", "", 1), Token("number", 4, 1)]
        table = SymbolTable()
        table.entry("a", "int", "variable")
        table.entry("1", "int", "variable")
        table.entry("10", "int", "variable")
        table.entry("2", "int", "variable")

        opcode, _, _ = for_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.assertEqual(opcode, OpCode('for', 'a&&&1&&&10&&&+&&&<&&&2', None))
    