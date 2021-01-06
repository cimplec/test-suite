import unittest
import os
import io
import sys

from simc.lexical_analyzer import LexicalAnalyzer
from simc.symbol_table import SymbolTable
from simc.token_class import Token

from .exceptions import NotATokenError


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

    def __assertListEquality(self, sources, matches):
        for source, match in zip(sources, matches):
            self.assertEqual(source, match)

    def __print_tokens(self, tokens):
        for token in tokens:
            if isinstance(token, Token):
                print(token)
            else:
                raise NotATokenError

    def __match_single_token(self, source_code, token_type):
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        self.__assertListEquality(tokens, [Token(token_type, "", 1)])

    def __setup(self, source_code):
        self.source_filename = "lexical-analysis-test.simc"

        self.__write_to_file(self.source_filename, source_code)

        self.symbol_table = SymbolTable()
        self.lexical_analyzer = LexicalAnalyzer(
            source_filename=self.source_filename, symbol_table=self.symbol_table
        )

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

        self.lexical_analyzer.source_code = (
            self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        )
        self.lexical_analyzer.tokens = []

        # True case - Match first character in list
        self.lexical_analyzer.current_source_index = 0
        self.lexical_analyzer._LexicalAnalyzer__check_next_token(
            ["+"], ["plus"], "minus"
        )
        self.assertEqual(
            self.lexical_analyzer.tokens[-1],
            Token("plus", "", self.lexical_analyzer.line_num),
        )

    def test___check_next_token_after_first_character(self):
        self.__setup(source_code="1+2")

        self.lexical_analyzer.source_code = (
            self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        )
        self.lexical_analyzer.tokens = []

        # True case - Match after first character in list
        self.lexical_analyzer.current_source_index = 0
        self.lexical_analyzer._LexicalAnalyzer__check_next_token(
            ["/", "+"], ["divide", "plus"], "minus"
        )
        self.assertEqual(
            self.lexical_analyzer.tokens[-1],
            Token("plus", "", self.lexical_analyzer.line_num),
        )

    def test___check_next_token_false_case(self):
        self.__setup(source_code="1+2")

        self.lexical_analyzer.source_code = (
            self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        )
        self.lexical_analyzer.tokens = []

        # False case
        self.lexical_analyzer.current_source_index = 0
        self.lexical_analyzer._LexicalAnalyzer__check_next_token(
            ["/"], ["divide"], "minus"
        )
        self.assertEqual(
            self.lexical_analyzer.tokens[-1],
            Token("minus", "", self.lexical_analyzer.line_num),
        )

    def test___is_keyword_true_case(self):
        self.__setup(source_code="")

        # True cases
        self.assertEqual(
            self.lexical_analyzer._LexicalAnalyzer__is_keyword("print"), True
        )
        self.assertEqual(
            self.lexical_analyzer._LexicalAnalyzer__is_keyword("true"), True
        )

    def test___is_keyword_false_case(self):
        self.__setup(source_code="")

        # False cases
        self.assertEqual(self.lexical_analyzer._LexicalAnalyzer__is_keyword("1"), False)
        self.assertEqual(
            self.lexical_analyzer._LexicalAnalyzer__is_keyword("id"), False
        )

    def test___numeric_val_integer(self):
        self.__setup(source_code="")

        # Integer numeric constant
        self.lexical_analyzer.source_code = "314\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__numeric_val()

        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ["314", "int", "constant"],
        )
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("number", 1, 0))

    def test___numeric_val_float(self):
        self.__setup(source_code="")

        # Float numeric constant
        self.lexical_analyzer.source_code = "3.14\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__numeric_val()
        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ["3.14", "float", "constant"],
        )
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("number", 1, 0))

    def test___numeric_val_double(self):
        self.__setup(source_code="")

        # Double numeric constant
        self.lexical_analyzer.source_code = "3.14159265\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__numeric_val()
        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ["3.14159265", "double", "constant"],
        )
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
        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ['"hello world"', "string", "constant"],
        )
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("string", 1, 0))

    def test___string_val_string_starting_with_single_quote(self):
        self.__setup(source_code="")

        # String constant with '
        self.lexical_analyzer.source_code = "'hello world'\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__string_val(start_char="'")
        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ['"hello world"', "string", "constant"],
        )
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("string", 1, 0))

    def test___string_val_char_starting_with_double_quote(self):
        self.__setup(source_code="")

        # Char constant with "
        self.lexical_analyzer.source_code = '"h"\0'
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__string_val()
        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ["'h'", "char", "constant"],
        )
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("string", 1, 0))

    def test___string_val_char_starting_with_single_quote(self):
        self.__setup(source_code="")

        # Char constant with '
        self.lexical_analyzer.source_code = "'h'\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__string_val(start_char="'")
        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ["'h'", "char", "constant"],
        )
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
        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ["true", "bool", "constant"],
        )
        self.assertEqual(self.lexical_analyzer.tokens[-1], Token("bool", 1, 0))

    def test___keyword_identifier_math_constant(self):
        self.__setup(source_code="")

        # Math constant
        self.lexical_analyzer.source_code = "PI\0"
        self.lexical_analyzer.tokens = []

        self.lexical_analyzer._LexicalAnalyzer__keyword_identifier()
        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ["PI", "double", "constant"],
        )
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
        self.assertEqual(
            self.lexical_analyzer.symbol_table.symbol_table[1],
            ["variable", "var", "variable"],
        )
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

        self.lexical_analyzer.source_code = (
            self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        )
        self.lexical_analyzer.tokens = []
        self.lexical_analyzer._LexicalAnalyzer__get_raw_tokens()

        tokens_to_match = [
            Token("RAW_C", "", 0),
            Token("RAW_C", "        BEGIN_C", 1),
            Token("RAW_C", "            int a = 10;", 2),
            Token("RAW_C", '            printf("%d", a);', 3),
        ]

        self.__assertListEquality(self.lexical_analyzer.tokens, tokens_to_match)

    def test___get_raw_tokens_empty_raw_c_code(self):
        raw_c_source_code = """
        BEGIN_C
        END_C
        """
        self.__setup(source_code=raw_c_source_code)

        self.lexical_analyzer.source_code = (
            self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        )
        self.lexical_analyzer.tokens = []
        self.lexical_analyzer._LexicalAnalyzer__get_raw_tokens()

        tokens_to_match = [Token("RAW_C", "", 0), Token("RAW_C", "        BEGIN_C", 1)]

        self.__assertListEquality(self.lexical_analyzer.tokens, tokens_to_match)

    def test___get_raw_tokens_error_no_end_c(self):
        raw_c_source_code = """
        BEGIN_C
        """
        self.__setup(source_code=raw_c_source_code)

        self.lexical_analyzer.source_code = (
            self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        )
        self.lexical_analyzer.tokens = []

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            self.lexical_analyzer._LexicalAnalyzer__get_raw_tokens()

        self.__release_print()

    def test_lexical_analyze_raw_c(self):
        source_code = """
        BEGIN_C
            printf("Hello World");
        END_C
        """
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [
            Token("newline", "", 1),
            Token("BEGIN_C", "", 2),
            Token("RAW_C", "", 2),
            Token("RAW_C", '            printf("Hello World");', 3),
        ]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_numeric_val(self):
        source_code = "3.14"
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [Token("number", 1, 1)]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_string_val_double_quotes(self):
        source_code = '"hello"'
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [Token("string", 1, 1)]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_string_val_single_quotes(self):
        source_code = "'hello'"
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [Token("string", 1, 1)]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_keyword_identifier(self):
        source_code = "var a"
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [Token("var", "", 1), Token("id", 1, 1)]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_parens(self):
        source_code = "()"
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [Token("left_paren", "", 1), Token("right_paren", "", 1)]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_too_many_closing_parantheses(self):
        source_code = "())"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()

    def test_lexical_analyze_unbalanced_parantheses(self):
        source_code = "([)]"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()

    def test_lexical_analyze_call_end_token(self):
        source_code = "()\n"
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [
            Token("left_paren", "", 1),
            Token("right_paren", "", 1),
            Token("call_end", "", 1),
        ]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_newline(self):
        source_code = "\n"
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [Token("newline", "", 1)]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_newline_parantheses_not_matching(self):
        source_code = "(\n"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()

    def test_lexical_analyze_braces(self):
        source_code = "{}"
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [Token("left_brace", "", 1), Token("right_brace", "", 1)]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_too_many_closing_braces(self):
        source_code = "{}}"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()

    def test_lexical_analyze_unbalanced_braces(self):
        source_code = "{(})"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()

    def test_lexical_analyze_brackets(self):
        source_code = "[]"
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [Token("left_bracket", "", 1), Token("right_bracket", "", 1)]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_too_many_closing_brackets(self):
        source_code = "[]]"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()

    def test_lexical_analyze_unbalanced_brackets(self):
        source_code = "[{]}"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()

    def test_lexical_analyze_equal(self):
        self.__match_single_token("==", "equal")

    def test_lexical_analyze_assignment(self):
        self.__match_single_token("=", "assignment")

    def test_lexical_analyze_plus_equal(self):
        self.__match_single_token("+=", "plus_equal")

    def test_lexical_analyze_increment(self):
        self.__match_single_token("++", "increment")

    def test_lexical_analyze_plus(self):
        self.__match_single_token("+", "plus")

    def test_lexical_analyze_minus_equal(self):
        self.__match_single_token("-=", "minus_equal")

    def test_lexical_analyze_decrement(self):
        self.__match_single_token("--", "decrement")

    def test_lexical_analyze_minus(self):
        self.__match_single_token("-", "minus")

    def test_lexical_analyze_multiply_equal(self):
        self.__match_single_token("*=", "multiply_equal")

    def test_lexical_analyze_power(self):
        self.__match_single_token("**", "power")

    def test_lexical_analyze_multiply(self):
        self.__match_single_token("*", "multiply")

    def test_lexical_analyze_bitwise_xor_equal(self):
        self.__match_single_token("^=", "bitwise_xor_equal")

    def test_lexical_analyze_bitwise_xor(self):
        self.__match_single_token("^", "bitwise_xor")

    def test_lexical_analyze_and(self):
        self.__match_single_token("&&", "and")

    def test_lexical_analyze_bitwise_and_equal(self):
        source_code = """
        var a
        a &= 1
        """
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [
            Token("newline", "", 1),
            Token("var", "", 2),
            Token("id", 1, 2),
            Token("newline", "", 2),
            Token("id", 1, 3),
            Token("bitwise_and_equal", "", 3),
            Token("number", 2, 3),
            Token("newline", "", 3),
        ]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_bitwise_and(self):
        source_code = "var a = 1 & 2"
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("assignment", "", 1),
            Token("number", 2, 1),
            Token("bitwise_and", "", 1),
            Token("number", 3, 1),
        ]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_address_of(self):
        self.__match_single_token("&", "address_of")

    def test_lexical_analyze_or(self):
        self.__match_single_token("||", "or")

    def test_lexical_analyze_bitwise_or_equal(self):
        self.__match_single_token("|=", "bitwise_or_equal")

    def test_lexical_analyze_bitwise_or(self):
        self.__match_single_token("|", "bitwise_or")

    def test_lexical_analyze_divide_equal(self):
        self.__match_single_token("/=", "divide_equal")

    def test_lexical_analyze_single_line_comment(self):
        source_code = """// This is a comment
        """
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [
            Token("single_line_comment", " This is a comment", 1),
            Token("newline", "", 1),
        ]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_multi_line_comment(self):
        source_code = """/*
        This is a multi-line comment
        */
        """
        self.__setup(source_code=source_code)

        tokens, _ = self.lexical_analyzer.lexical_analyze()

        tokens_to_match = [
            Token(
                "multi_line_comment",
                """
        This is a multi-line comment
        """,
                3,
            ),
            Token("newline", "", 3),
        ]

        self.__assertListEquality(tokens, tokens_to_match)

    def test_lexical_analyze_divide(self):
        self.__match_single_token("/", "divide")

    def test_lexical_analyze_modulus_equal(self):
        self.__match_single_token("%=", "modulus_equal")

    def test_lexical_analyze_modulus(self):
        self.__match_single_token("%", "modulus")

    def test_lexical_analyze_comma(self):
        self.__match_single_token(",", "comma")

    def test_lexical_analyze_not_equal(self):
        self.__match_single_token("!=", "not_equal")

    def test_lexical_analyze_right_shift(self):
        self.__match_single_token(">>", "right_shift")

    def test_lexical_analyze_greater_than_equal(self):
        self.__match_single_token(">=", "greater_than_equal")

    def test_lexical_analyze_greater_than(self):
        self.__match_single_token(">", "greater_than")

    def test_lexical_analyze_left_shift(self):
        self.__match_single_token("<<", "left_shift")

    def test_lexical_analyze_less_than_equal(self):
        self.__match_single_token("<=", "less_than_equal")

    def test_lexical_analyze_less_than(self):
        self.__match_single_token("<", "less_than")

    def test_lexical_analyze_colon(self):
        self.__match_single_token(":", "colon")

    def test_lexical_analyze_unbalanced_parantheses_end(self):
        source_code = "(()"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()

    def test_lexical_analyze_unbalanced_braces_end(self):
        source_code = "{{}"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()

    def test_lexical_analyze_unbalanced_brackets_end(self):
        source_code = "[[]"
        self.__setup(source_code=source_code)

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _, _ = self.lexical_analyzer.lexical_analyze()

        self.__release_print()
