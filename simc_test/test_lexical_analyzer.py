import unittest
import os

from simc.lexical_analyzer import LexicalAnalyzer
from simc.symbol_table import SymbolTable

class TestLexicalAnalyzer(unittest.TestCase):

    ####################################################################################################
    # HELPERS
    ####################################################################################################
    def __write_to_file(self, filename, string):
        with open(filename, "w") as file:
            file.write(string)

    def __setup(self, source_code):
        self.source_filename = "lexical-analysis-test.simc"

        self.__write_to_file(self.source_filename, source_code)

        self.symbol_table = SymbolTable()
        self.lexical_analyzer = LexicalAnalyzer(source_filename=self.source_filename, symbol_table=self.symbol_table)

    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test___read_source_code(self):
        # Test with original source code
        test_source_code = """
        print("Hello World")
        """

        self.__setup(source_code=test_source_code)

        source_code = self.lexical_analyzer._LexicalAnalyzer__read_source_code()
        self.assertEqual(source_code, test_source_code + "\0")

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

    def test___update_source_index(self):
        self.__setup(source_code="print('Hello')")

        # Set initial index
        self.lexical_analyzer.current_source_index = 0

        # Default parameter (by=1)
        self.lexical_analyzer._LexicalAnalyzer__update_source_index()
        self.assertEqual(self.lexical_analyzer.current_source_index, 1)

        # Positive by (=11)
        self.lexical_analyzer._LexicalAnalyzer__update_source_index(by=10)
        self.assertEqual(self.lexical_analyzer.current_source_index, 11)

        # Negative by (=-5)
        self.lexical_analyzer._LexicalAnalyzer__update_source_index(by=-5)
        self.assertEqual(self.lexical_analyzer.current_source_index, 6)
