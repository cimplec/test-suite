import unittest
import io
import sys

from simc.parser.function_parser import *
from simc.parser.simc_parser import parse
from simc.token_class import Token
from simc.symbol_table import SymbolTable
from simc.lexical_analyzer import LexicalAnalyzer

class TestFunctionParser(unittest.TestCase):

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

    def __return_tokens_and_table(self, source_code):
        filename = "function-parse-test.simc"
        with open(filename, "w") as file:
            file.write(source_code)

        table = SymbolTable()
        lexer = LexicalAnalyzer(filename, table)
        tokens, _ = lexer.lexical_analyze()

        return tokens, table

    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test_function_call_statement_more_params_than_expected(self):
        source_code = """
        fun sum(a, b)
            return a + b

        MAIN
            var a = sum(1)
        END_MAIN
        """

        tokens, table = self.__return_tokens_and_table(source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _, _ = function_call_statement(tokens=tokens, i=21, table=table, func_ret_type={})

        self.__release_print()

    def test_function_call_statement_no_error(self):
        source_code = """
        fun sum(a, b)
            return a + b

        MAIN
            sum(1, 2)
        END_MAIN
        """

        tokens, table = self.__return_tokens_and_table(source_code)

        opcodes = parse(tokens, table)

        self.assertEqual(opcodes[5], OpCode('func_call', 'sum---1&&&2', ''))

    def test_extract_func_typedata(self):
        table = SymbolTable()

        typedata = "sum---a---b"

        params, _ = extract_func_typedata(typedata, table)
        
        self.assertEqual(params, ['a', 'b'])

    def test_fill_missing_args_with_defaults(self):
        op_value_list = ["1", "2", "3", "4"]
        default_values = ["5", "6"]
        num_actual_params = 4
        num_formal_params = 6

        args = fill_missing_args_with_defaults(op_value_list, default_values, num_actual_params, num_formal_params)
        
        self.assertEqual(args, ['1', '2', '3', '4', '5', '6)'])

    def test_function_definition_statement_func_name_missing(self):
        tokens_list = [Token("fun", "", 1), Token("left_paren", "", 1)]
        table = SymbolTable()

        self.__suppress_print()
        
        with self.assertRaises(SystemExit):
            _, _, _, _ = function_definition_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_function_definition_statement_left_paren_missing(self):
        tokens_list = [Token("fun", "", 1), Token("id", 1, 1), Token("id", 2, 1)]
        table = SymbolTable()

        self.__suppress_print()
        
        with self.assertRaises(SystemExit):
            _, _, _, _ = function_definition_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()


    def test_function_call_statement_no_error(self):
        source_code = """
        fun sum(a, b)
            return a + b

        MAIN
            sum(1, 2)
        END_MAIN
        """

        tokens, table = self.__return_tokens_and_table(source_code)

        opcodes = parse(tokens, table)

        self.assertEqual(opcodes[0], OpCode('func_decl', 'sum---a&&&b', ''))