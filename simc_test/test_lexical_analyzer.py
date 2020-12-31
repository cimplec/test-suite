import unittest
import os

from simc.lexical_analyzer import LexicalAnalyzer
from simc.symbol_table import SymbolTable

class TestLexicalAnalyzer(unittest.TestCase):

    ####################################################################################################
    # SETUP
    ####################################################################################################
    def setUp(self):
        # Write some sample code in a file
        

        self.lexical_analyzer = LexicalAnalyzer()

    ####################################################################################################
    # TESTS
    ####################################################################################################
