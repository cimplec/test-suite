import unittest
import io
import sys

from simc.parser.variable_parser import *
from simc.token_class import Token
from simc.symbol_table import SymbolTable
from simc.parser.simc_parser import *


class TestVariableParser(unittest.TestCase):

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
    def test_check_ptr_true_case(self):
        tokens_list = [
            Token("multiply", "", 1),
            Token("multiply", "", 1),
            Token("newline", "", 1),
        ]

        is_ptr, asterisk_count, _ = check_ptr(tokens=tokens_list, i=0)

        self.assertEqual(is_ptr, True)
        self.assertEqual(asterisk_count, 2)

    def test_check_ptr_false_case(self):
        tokens_list = [Token("print", "", 1), Token("newline", "", 1)]

        is_ptr, asterisk_count, _ = check_ptr(tokens=tokens_list, i=0)

        self.assertEqual(is_ptr, False)
        self.assertEqual(asterisk_count, 0)

    def test_var_statement_general_expected_id(self):
        tokens_list = [Token("var", "", 1), Token("print", "", 1)]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = var_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_var_statement_array_expected_integer_size_of_array(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("left_bracket", "", 1),
            Token("number", 2, 1),
            Token("right_bracket", "", 1),
            Token("assignment", "", 1),
            Token("left_brace", "", 1),
            Token("number", 3, 1),
            Token("comma", "", 1),
        ]
        table = SymbolTable()
        table.entry("a", "var", "variable")
        table.entry("3.14", "float", "constant")

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = var_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_var_statement_array_assign_no_error(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("left_bracket", "", 1),
            Token("number", 2, 1),
            Token("right_bracket", "", 1),
            Token("assignment", "", 1),
            Token("left_brace", "", 1),
            Token("number", 3, 1),
            Token("comma", "", 1),
            Token("number", 4, 1),
            Token("right_brace", "", 1),
            Token("newline", "", 1),
        ]
        table = SymbolTable()
        table.entry("a", "var", "variable")
        table.entry("2", "int", "constant")
        table.entry("1", "int", "constant")
        table.entry("2", "int", "constant")

        opcode, _, _ = var_statement(
            tokens=tokens_list, i=1, table=table, func_ret_type={}
        )

        self.assertEqual(opcode, OpCode("array_assign", "a---2---{1,2}", "int"))

    def test_var_statement_array_invalid_syntax_for_declaration(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("left_bracket", "", 1),
            Token("number", 2, 1),
            Token("right_bracket", "", 1),
            Token("plus_equal", "", 1),
            Token("newline", "", 1),
        ]
        table = SymbolTable()
        table.entry("a", "var", "variable")
        table.entry("2", "int", "constant")

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = var_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_var_statement_array_size_of_array_needs_to_be_known_if_no_assign(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("left_bracket", "", 1),
            Token("right_bracket", "", 1),
        ]
        table = SymbolTable()
        table.entry("a", "var", "variable")
        table.entry("3", "int", "constant")

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = var_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_var_statement_array_no_assign(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("left_bracket", "", 1),
            Token("number", 2, 1),
            Token("right_bracket", "", 1),
        ]
        table = SymbolTable()
        table.entry("a", "var", "variable")
        table.entry("2", "int", "constant")

        opcode, _, _ = var_statement(
            tokens=tokens_list, i=1, table=table, func_ret_type={}
        )
        
        self.assertEqual(opcode, OpCode('array_no_assign', 'a---2', None))

    def test_var_statement_ptr_assign(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("assignment", "", 1),
            Token("number", 2, 1),
            Token("newline", "", 1),
            Token("var", "", 2),
            Token("multiply", "", 2),
            Token("id", 3, 2),
            Token("assignment", "", 2),
            Token("id", 1, 2),
            Token("newline", "", 2),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["b", "var", "variable", ''],
            2: ["1", "int", "constant", ''],
            3: ["a", "var", "variable", ''],
        }

        opcodes = parse(tokens_list, table)

        self.assertEqual(opcodes[1], OpCode("ptr_assign", "a---b---1", "int"))

    def test_var_statement_var_assign(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("assignment", "", 1),
            Token("number", 2, 1),
            Token("newline", "", 1),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["b", "var", "variable", ''],
            2: ["1", "int", "constant", ''],
            3: ["a", "var", "variable", ''],
        }

        opcodes = parse(tokens_list, table)

        self.assertEqual(opcodes[0], OpCode("var_assign", "b---1", "int"))

    def test_var_statement_ptr_no_assign(self):
        tokens_list = [
            Token("var", "", 1),
            Token("multiply", "", 1),
            Token("id", 1, 1),
            Token("newline", "", 1),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["b", "var", "variable", ''],
            2: ["1", "int", "constant", ''],
            3: ["a", "var", "variable", ''],
        }

        opcodes = parse(tokens_list, table)

        self.assertEqual(opcodes[0], OpCode("ptr_no_assign", "b", None))

    def test_var_statement_var_no_assign(self):
        tokens_list = [Token("var", "", 1), Token("id", 1, 1), Token("newline", "", 1)]
        table = SymbolTable()
        table.symbol_table = {
            1: ["b", "var", "variable", ''],
            2: ["1", "int", "constant", ''],
            3: ["a", "var", "variable", ''],
        }

        opcodes = parse(tokens_list, table)

        self.assertEqual(opcodes[0], OpCode("var_no_assign", "b", None))

    def test_assign_statement_variable_used_before_declaration(self):
        tokens_list = [
            Token("id", 1, 1),
            Token("assignment", "", 1),
            Token("number", 2, 1),
            Token("newline", "", 1),
        ]
        table = SymbolTable()
        table.entry("a", "var", "variable")
        table.entry("2", "int", "constant")

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = parse(tokens_list, table)

        self.__release_print()

    def test_assign_statement_ptr_only_assign_no_error(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("assignment", "", 1),
            Token("number", 2, 1),
            Token("newline", "", 1),
            Token("var", "", 2),
            Token("multiply", "", 2),
            Token("id", 3, 2),
            Token("assignment", "", 2),
            Token("bitwise_and", "", 2),
            Token("id", 1, 2),
            Token("newline", "", 2),
            Token("multiply", "", 3),
            Token("id", 3, 3),
            Token("assignment", "", 3),
            Token("number", 4, 3),
            Token("newline", "", 3),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["b", "var", "variable", ''],
            2: ["1", "int", "constant", ''],
            3: ["a", "var", "variable", ''],
            4: ["1", "int", "constant", ''],
        }

        opcodes = parse(tokens_list, table)

        self.assertEqual(opcodes[2], OpCode("ptr_only_assign", "a---=---1---1", ""))

    def test_assign_statement_assign_no_error(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("newline", "", 1),
            Token("id", 1, 2),
            Token("assignment", "", 2),
            Token("number", 2, 2),
            Token("newline", "", 2),
        ]
        table = SymbolTable()
        table.symbol_table = {1: ["b", "var", "variable", ''], 2: ["1", "int", "constant", '']}

        opcodes = parse(tokens_list, table)

        self.assertEqual(opcodes[1], OpCode("assign", "b---=---1", ""))
