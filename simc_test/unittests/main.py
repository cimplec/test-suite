import unittest
import os
import subprocess

from .test_global_helpers import TestGlobalHelpers
from .test_lexical_analyzer import TestLexicalAnalyzer
from .test_op_code import TestOpCode
from .test_symbol_table import TestSymbolTable
from .test_token_class import TestTokenClass
from .test_simc import TestSimc
from .test_compiler import TestCompiler
from .parser.test_array_parser import TestArrayParser
from .parser.test_conditional_parser import TestConditionalParser
from .parser.test_function_parser import TestFunctionParser
from .parser.test_loop_parser import TestLoopParser
from .parser.test_struct_parser import TestStructParser
from .parser.test_variable_parser import TestVariableParser
from .parser.test_simc_parser import TestSimcParser

from simc_test.helpers import make_dir, remove_dir


def unit_test():
    test_dir_path = ".simc-test-suite"
    make_dir(test_dir_path)
    os.chdir(test_dir_path)

    # List of test classes to run
    test_classes_to_run = [
        TestGlobalHelpers,
        TestLexicalAnalyzer,
        TestOpCode,
        TestSymbolTable,
        TestTokenClass,
        TestSimc,
        TestCompiler,
        TestArrayParser,
        TestConditionalParser,
        TestFunctionParser,
        TestLoopParser,
        TestStructParser,
        TestVariableParser,
        TestSimcParser,
    ]

    loader = unittest.TestLoader()

    # Load all test cases into suites_list
    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    # Collection of all the suites
    big_suite = unittest.TestSuite(suites_list)

    # Run the tests
    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)

    os.chdir("../")
    remove_dir(test_dir_path)
