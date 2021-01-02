import unittest
import os
import io
import sys

from simc.lexical_analyzer import LexicalAnalyzer
from simc.symbol_table import SymbolTable
from simc.token_class import Token

class TestLexicalAnalyzer(unittest.TestCase):

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

    def __write_to_file(self, filename, string):
        with open(filename, "w") as file:
            file.write(string)

    def __setup(self, source_code):
        self.source_filename = "lexical-analysis-test.simc"

        self.__write_to_file(self.source_filename, source_code)

        self.symbol_table = SymbolTable()
        self.lexical_analyzer = LexicalAnalyzer(source_filename=self.source_filename, symbol_table=self.symbol_table)

        # Set initial index
        self.lexical_analyzer.current_source_index = 0
        self.lexical_analyzer.line_num = 0

    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test___read_source_code_non_empty_source_code(self):
        # Test with original source code
        test_source_code = """
        print("Hello World")
        """

        self.__setup(source_code=test_source_code)

        source_code = self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        self.assertEqual(source_code, test_source_code + "\0")

    def test___read_source_code_empty_source_code(self):
        # Test with empty source code
        empty_source_code = ""

        self.__setup(source_code=empty_source_code)

        self.__write_to_file(self.source_filename, empty_source_code)
        
        source_code = self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        self.assertEqual(source_code, empty_source_code + "\0")

    def test_update_filename(self):
        self.__setup(source_code="")

        # Update filename
        test_source_filename = "test.simc"
        self.lexical_analyzer.update_filename(source_filename=test_source_filename)

        self.assertEqual(self.lexical_analyzer.source_filename, test_source_filename)

    def test___update_source_index_default_parameter(self):
        self.__setup(source_code="print('Hello')")

        # Default parameter (by=1)
        self.lexical_analyzer._LexicalAnalyzer__update_source_index()
        self.assertEqual(self.lexical_analyzer.current_source_index, 1)

    def test___update_source_index_by_positive_number(self):
        self.__setup(source_code="print('Hello')")

        # Positive by (=11)
        self.lexical_analyzer._LexicalAnalyzer__update_source_index(by=10)
        self.assertEqual(self.lexical_analyzer.current_source_index, 10)

    def test___update_source_index_by_negative_number(self):
        self.__setup(source_code="print('Hello')")

        # Negative by (=-5)
        self.lexical_analyzer._LexicalAnalyzer__update_source_index(by=-5)
        self.assertEqual(self.lexical_analyzer.current_source_index, -5)

    def test___check_next_token_first_character(self):
        self.__setup(source_code="1+2")

        self.lexical_analyzer.source_code = self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        self.lexical_analyzer.tokens = []

        # True case - Match first character in list
        self.lexical_analyzer.current_source_index = 0
        self.lexical_analyzer._LexicalAnalyzer__check_next_token(['+'], ["plus"], "minus")
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("plus", "", self.lexical_analyzer.line_num))

    def test___check_next_token_after_first_character(self):
        self.__setup(source_code="1+2")

        self.lexical_analyzer.source_code = self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        self.lexical_analyzer.tokens = []

        # True case - Match after first character in list
        self.lexical_analyzer.current_source_index = 0
        self.lexical_analyzer._LexicalAnalyzer__check_next_token(['/', '+'], ["divide", "plus"], "minus")
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("plus", "", self.lexical_analyzer.line_num))

    def test___check_next_token_false_case(self):
        self.__setup(source_code="1+2")

        self.lexical_analyzer.source_code = self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        self.lexical_analyzer.tokens = []

        # False case 
        self.lexical_analyzer.current_source_index = 0
        self.lexical_analyzer._LexicalAnalyzer__check_next_token(["/"], ["divide"], "minus")
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("minus", "", self.lexical_analyzer.line_num))

    def test___is_keyword_true_case(self):
        self.__setup(source_code="")

        # True cases
        self.assertEqual(self.lexical_analyzer._LexicalAnalyzer__is_keyword("print"), True)
        self.assertEqual(self.lexical_analyzer._LexicalAnalyzer__is_keyword("true"), True)

    def test___is_keyword_false_case(self):
        self.__setup(source_code="")

        # False cases
        self.assertEqual(self.lexical_analyzer._LexicalAnalyzer__is_keyword("1"), False)
        self.assertEqual(self.lexical_analyzer._LexicalAnalyzer__is_keyword("id"), False)

    def test___numeric_val_integer(self):
        self.__setup(source_code="")

        # Integer numeric constant
        self.lexical_analyzer.source_code = "314\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__numeric_val()

        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ['314', 'int', 'constant'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("number", 1, 0))

    def test___numeric_val_float(self):
        self.__setup(source_code="")

        # Float numeric constant
        self.lexical_analyzer.source_code = "3.14\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__numeric_val()
        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ['3.14', 'float', 'constant'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("number", 1, 0))

    def test___numeric_val_double(self):
        self.__setup(source_code="")

        # Double numeric constant
        self.lexical_analyzer.source_code = "3.14159265\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__numeric_val()
        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ['3.14159265', 'double', 'constant'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("number", 1, 0))

    def test___numeric_val_error(self):
        self.__setup(source_code="")
        self.__suppress_print()

        # Multiple decimal points error
        self.lexical_analyzer.source_code = "3.14.159\0"
        self.lexical_analyzer.tokens = []

        with self.assertRaises(SystemExit):
            self.lexical_analyzer._LexicalAnalyzer__numeric_val()

        self.__release_print()

    def test___string_val_string_starting_with_double_quote(self):
        self.__setup(source_code="")

        # String constant with "
        self.lexical_analyzer.source_code = '"hello world"\0'
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__string_val()
        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ['"hello world"', 'string', 'constant'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("string", 1, 0))

    def test___string_val_string_starting_with_single_quote(self):
        self.__setup(source_code="")

        # String constant with '
        self.lexical_analyzer.source_code = "'hello world'\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__string_val(start_char="'")
        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ['"hello world"', 'string', 'constant'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("string", 1, 0))

    def test___string_val_char_starting_with_double_quote(self):
        self.__setup(source_code="")

        # Char constant with "
        self.lexical_analyzer.source_code = '"h"\0'
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__string_val()
        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ["'h'", 'char', 'constant'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("string", 1, 0))

    def test___string_val_char_starting_with_single_quote(self):
        self.__setup(source_code="")

        # Char constant with '
        self.lexical_analyzer.source_code = "'h'\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__string_val(start_char="'")
        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ["'h'", 'char', 'constant'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("string", 1, 0))

    def test___string_val_string_untertminated_string(self):
        self.__setup(source_code="")
        self.__suppress_print()

        # Unterminated string
        self.lexical_analyzer.source_code = '"he\0'
        self.lexical_analyzer.tokens = []

        with self.assertRaises(SystemExit):
            self.lexical_analyzer._LexicalAnalyzer__string_val(start_char="'")

        self.__release_print()

    def test___keyword_identifier_bool_constant(self):
        self.__setup(source_code="")

        # Bool constant
        self.lexical_analyzer.source_code = "true\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__keyword_identifier()
        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ["true", 'bool', 'constant'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("bool", 1, 0))

    def test___keyword_identifier_math_constant(self):
        self.__setup(source_code="")

        # Math constant
        self.lexical_analyzer.source_code = "PI\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__keyword_identifier()
        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ["PI", 'double', 'constant'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("number", 1, 0))

    def test___keyword_identifier_keyword(self):
        self.__setup(source_code="")

        # Keyword
        self.lexical_analyzer.source_code = "print\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__keyword_identifier()
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("print", "", 0))

    def test___keyword_identifier_identifier(self):
        self.__setup(source_code="")

        # Identifier
        self.lexical_analyzer.source_code = "variable\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__keyword_identifier()
        self.assertEqual(self.lexical_analyzer.symbol_table.symbol_table[1], ["variable", 'var', 'variable'])
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("id", 1, 0))

    def test___keyword_identifier_c_keyword_error(self):
        self.__setup(source_code="")
        self.__suppress_print()

        # C Keyword as identifier - Error
        self.lexical_analyzer.source_code = "const\0"
        self.lexical_analyzer.tokens = []

        with self.assertRaises(SystemExit):
            self.lexical_analyzer._LexicalAnalyzer__keyword_identifier()

        self.__release_print()

    def test___get_raw_tokens_with_raw_c_code(self):
        raw_c_source_code = """
        BEGIN_C
            int a = 10;
            printf("%d", a);
        END_C
        """
        self.__setup(source_code=raw_c_source_code)

        self.lexical_analyzer.source_code = self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        self.lexical_analyzer.tokens = []
        self.lexical_analyzer._LexicalAnalyzer__get_raw_tokens()

        tokens_to_match = [Token('RAW_C', '', 0), Token('RAW_C', '        BEGIN_C', 1),
                           Token('RAW_C', '            int a = 10;', 2), 
                           Token('RAW_C', '            printf("%d", a);', 3)]

        for token, token_to_match in zip(self.lexical_analyzer.tokens, tokens_to_match):
            self.assertEqual(token, token_to_match)

    def test___get_raw_tokens_empty_raw_c_code(self):
        raw_c_source_code = """
        BEGIN_C
        END_C
        """
        self.__setup(source_code=raw_c_source_code)

        self.lexical_analyzer.source_code = self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        self.lexical_analyzer.tokens = []
        self.lexical_analyzer._LexicalAnalyzer__get_raw_tokens()

        tokens_to_match = [Token('RAW_C', '', 0), Token('RAW_C', '        BEGIN_C', 1)]

        for token, token_to_match in zip(self.lexical_analyzer.tokens, tokens_to_match):
            self.assertEqual(token, token_to_match)

    def test___get_raw_tokens_error_no_end_c(self):
        raw_c_source_code = """
        BEGIN_C
        """
        self.__setup(source_code=raw_c_source_code)

        self.lexical_analyzer.source_code = self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        self.lexical_analyzer.tokens = []

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            self.lexical_analyzer._LexicalAnalyzer__get_raw_tokens()

        self.__release_print()

    