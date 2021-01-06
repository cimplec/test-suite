import unittest
import io
import sys

from simc.parser.struct_parser import *
from simc.token_class import Token
from simc.symbol_table import SymbolTable


class TestStructParser(unittest.TestCase):

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
    def test_struct_declaration_statement_expected_struct_name(self):
        tokens_list = [Token("struct", "", 1), Token("print", "", 1)]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = struct_declaration_statement(tokens=tokens_list, i=1, table=table)

        self.__release_print()

    def test_struct_declaration_statement_expected_left_brace(self):
        tokens_list = [Token("struct", "", 1), Token("id", 1, 1), Token("print", "", 1)]
        table = SymbolTable()
        table.entry("my_struct", "var", "variable")

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = struct_declaration_statement(tokens=tokens_list, i=1, table=table)

        self.__release_print()

    def test_structure_declaration_no_error(self):
        tokens_list = [
            Token("struct", "", 1),
            Token("id", 1, 1),
            Token("left_brace", "", 1),
            Token("newline", "", 1),
            Token("var", "", 2),
            Token("id", 2, 2),
            Token("assignment", "", 2),
            Token("number", 3, 2),
            Token("newline", "", 2),
            Token("right_brace", "", 3),
            Token("newline", "", 3),
        ]
        table = SymbolTable()
        table.entry("my_struct", "var", "variable")
        table.entry("a", "int", "variable")
        table.entry("a", "int", "constant")

        opcode, _, _ = struct_declaration_statement(
            tokens=tokens_list, i=1, table=table
        )

        self.assertEqual(opcode, OpCode("struct_decl", "my_struct", ""))
