import unittest
import io
import sys

from simc.parser.conditional_parser import *
from simc.token_class import Token
from simc.symbol_table import SymbolTable
from simc.op_code import OpCode


class TestConditionalParser(unittest.TestCase):

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
    def test_if_statement_missing_left_paren(self):
        tokens_list = [Token("if", "", 1), Token("left_brace", "", 1)]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _, _ = if_statement(
                tokens=tokens_list, i=1, table=table, func_ret_type={}
            )

        self.__release_print()

    def test_if_statement_missing_right_paren(self):
        tokens_list = [
            Token("if", "", 1),
            Token("left_paren", "", 1),
            Token("print", "", 1),
        ]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _, _ = if_statement(
                tokens=tokens_list, i=1, table=table, func_ret_type={}
            )

        self.__release_print()

    def test_if_statement_no_error(self):
        tokens_list = [
            Token("if", "", 1),
            Token("left_paren", "", 1),
            Token("number", 1, 1),
            Token("right_paren", "", 1),
            Token("call_end", "", 1),
            Token("newline", "", 1),
            Token("print", "", 1),
        ]
        table = SymbolTable()
        table.entry("true", "bool", "variable")

        opcode, _, _ = if_statement(
            tokens=tokens_list, i=1, table=table, func_ret_type={}
        )

        self.assertEqual(opcode, OpCode("if", "true"))

    def test_switch_statement_missing_left_paren(self):
        tokens_list = [Token("switch", "", 1), Token("left_brace", "", 1)]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _, _ = switch_statement(
                tokens=tokens_list, i=1, table=table, func_ret_type={}
            )

        self.__release_print()

    def test_switch_statement_missing_right_paren(self):
        tokens_list = [
            Token("switch", "", 1),
            Token("left_paren", "", 1),
            Token("print", "", 1),
        ]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _, _ = switch_statement(
                tokens=tokens_list, i=1, table=table, func_ret_type={}
            )

        self.__release_print()

    def test_switch_statement_missing_left_brace(self):
        tokens_list = [
            Token("switch", "", 1),
            Token("left_paren", "", 1),
            Token("number", 1, 1),
            Token("right_paren", "", 1),
            Token("call_end", "", 1),
            Token("newline", "", 1),
            Token("print", "", 1),
        ]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _, _ = switch_statement(
                tokens=tokens_list, i=1, table=table, func_ret_type={}
            )

        self.__release_print()

    def test_switch_statement_no_error(self):
        tokens_list = [
            Token("switch", "", 1),
            Token("left_paren", "", 1),
            Token("number", 1, 1),
            Token("right_paren", "", 1),
            Token("call_end", "", 1),
            Token("newline", "", 1),
            Token("left_brace", "", 1),
            Token("print", "", 1),
        ]
        table = SymbolTable()
        table.entry("true", "bool", "variable")

        opcode, _, _ = switch_statement(
            tokens=tokens_list, i=1, table=table, func_ret_type={}
        )

        self.assertEqual(opcode, OpCode("switch", "true", ""))

    def test_case_statement_missing_colon(self):
        tokens_list = [
            Token("case", "", 1),
            Token("number", "", 1),
            Token("print", "", 1),
        ]
        table = SymbolTable()
        table.entry("1", "int", "variable")

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _, _ = case_statement(
                tokens=tokens_list, i=1, table=table, func_ret_type={}
            )

        self.__release_print()

    def test_case_statement_no_error(self):
        tokens_list = [
            Token("case", "", 1),
            Token("number", 1, 1),
            Token("colon", "", 1),
            Token("newline", "", 1),
            Token("left_brace", "", 1),
            Token("print", "", 1),
        ]
        table = SymbolTable()
        table.entry("1", "bool", "variable")

        opcode, _, _ = case_statement(
            tokens=tokens_list, i=1, table=table, func_ret_type={}
        )

        self.assertEqual(opcode, OpCode("case", "1", ""))
