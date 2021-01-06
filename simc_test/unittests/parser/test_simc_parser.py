import unittest
import io
import sys

from simc.parser.simc_parser import *
from simc.token_class import Token
from simc.symbol_table import SymbolTable

class TestSimcParser(unittest.TestCase):

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
    def test_expression_unknown_variable_error(self):
        tokens_list = [Token('var', '', 1), Token('id', 1, 1), Token('assignment', '', 1),
                       Token('number', 2, 1), Token('newline', '', 1), Token('print', '', 2),
                       Token('left_paren', '', 2), Token('string', 3, 2), Token('right_paren', '', 2),
                       Token('call_end', '', 2),  Token('newline', '', 2)]
        table = SymbolTable()
        table.symbol_table = {1: ['a', 'var', 'variable'], 2: ['1', 'int', 'constant'], 
                              3: ['"value = {a}"', 'string', 'constant']}

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = expression(tokens=tokens_list, i=7, table=table, msg="")

        self.__release_print()

    def test_expression_cannot_find_type_error(self):
        tokens_list = [Token('var', '', 1), Token('id', 1, 1), Token('newline', '', 2),
                       Token('print', '', 2), Token('left_paren', '', 2), Token('id', 1, 2),
                       Token('right_paren', '', 2), Token('newline', '', 2)]
        table = SymbolTable()
        table.symbol_table = {1: ['a', 'var', 'variable']}

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = parse(tokens=tokens_list, table=table)

        self.__release_print()

    def test_print_statement_expected_left_paren_error(self):
        tokens_list = [Token('print', '', 1), Token('var', '', 1)]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = print_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_print_statement_no_error(self):
        tokens_list = [Token('print', '', 1), Token('left_paren', '', 1), Token('string', 1, 1),
                       Token('right_paren', '', 1), Token('newline', '', 1)]
        table = SymbolTable()
        table.entry('"hello world"', "string", "constant")

        opcode, _, _ = print_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})
        
        self.assertEqual(opcode, OpCode('print', '"hello world"', None))

    def test_unary_statement_pre_increment(self):
        tokens_list = [Token('var', '', 1), Token('id', 1, 1), Token('assignment', '', 1),
                       Token('number', 2, 1), Token('newline', '', 1), Token('increment', '', 2),
                       Token('id', 1, 2), Token('newline', '', 2)]
        table = SymbolTable()
        table.symbol_table = {1: ['a', 'var', 'variable'], 2: ['1', 'int', 'constant']}

        opcodes = parse(tokens=tokens_list, table=table)
        
        self.assertEqual(opcodes[1], OpCode('unary', '++ a', None))

    def test_unary_statement_post_decrement(self):
        tokens_list = [Token('var', '', 1), Token('id', 1, 1), Token('assignment', '', 1),
                       Token('number', 2, 1), Token('newline', '', 1), Token('id', 1, 2),
                       Token('decrement', '', 2), Token('newline', '', 2)]
        table = SymbolTable()
        table.symbol_table = {1: ['a', 'var', 'variable'], 2: ['1', 'int', 'constant']}

        opcodes = parse(tokens=tokens_list, table=table)
       
        self.assertEqual(opcodes[1], OpCode('unary', 'a -- ', None))

    def test_exit_statement_expected_left_paren_error(self):
        tokens_list = [Token('exit', '', 1), Token('print', '', 1)]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = exit_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_exit_statement_expected_number_error(self):
        tokens_list = [Token('exit', '', 1), Token('left_paren', '', 1), Token('print', '', 1)]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = exit_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_exit_no_error(self):
        tokens_list = [Token('exit', '', 1), Token('left_paren', '', 1), Token('number', 1, 1),
                       Token('right_paren', '', 1)]
        table = SymbolTable()
        table.entry("0", "int", "constant")

        opcode, _, _ = exit_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})
        
        self.assertEqual(opcode, OpCode('exit', '0', None))

    def test_skip_all_nextlines_no_nextline(self):
        tokens_list = [Token('print', '', 1), Token('var', '', 1)]

        i = 0
        i = skip_all_nextlines(tokens=tokens_list, i=0)

        self.assertEqual(i, 1)

    def test_skip_all_nextlines_some_nextline(self):
        tokens_list = [Token('newline', '', 1), Token('newline', '', 1), Token('print', '', 1)]

        i = 0
        i = skip_all_nextlines(tokens=tokens_list, i=0)

        self.assertEqual(i, 2)

    def test_parse_empty_function_body_error(self):
        tokens_list = [Token('fun', '', 1), Token('id', 1, 1), Token('left_paren', '', 1), Token('right_paren', '', 1)]
        table = SymbolTable()
        table.entry("func", "var", "variable")

        # self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = parse(tokens=tokens_list, table=table)

        self.__release_print()
    