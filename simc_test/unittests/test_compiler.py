import unittest
import io
import sys

from simc.compiler import *
from simc.token_class import Token
from simc.symbol_table import SymbolTable


class TestCompiler(unittest.TestCase):

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
    def test_check_include(self):
        opcodes = [OpCode('print', '"Hello"', None), OpCode('var_assign', 'a---true', 'bool'),
                   OpCode('var_assign', 'b---M_PI', 'double')]

        includes = set(check_include(opcodes).split("\n"))
        should_be_includes = set(["#include <stdio.h>", "#include <stdbool.h>", "#include <math.h>"])
        
        self.assertEqual(includes, should_be_includes)

    def test_check_include_empty(self):
        opcodes = [OpCode('func_decl', 'hello---', ''), OpCode('scope_begin', '', ''), OpCode('return', '1', ''),
                   OpCode('scope_over', '', ''), OpCode('MAIN', '', ''), OpCode('var_assign', 'a---hello()', 'int'),
                   OpCode('END_MAIN', '', '')]

        includes = set(check_include(opcodes).split("\n"))
        should_be_includes = set([''])

        self.assertEqual(includes, should_be_includes)

    def test_compile_func_main_code_outside_main_true(self):
        outside_code = ""
        ccode = ""
        outside_main = True
        code = "printf('Hello World')"

        outside_code, ccode = compile_func_main_code(outside_code, ccode, outside_main, code)

        self.assertEqual(outside_code, code)
        self.assertEqual(ccode, "")

    def test_compile_func_main_code_outside_main_false(self):
        outside_code = ""
        ccode = ""
        outside_main = False
        code = "printf('Hello World')"

        outside_code, ccode = compile_func_main_code(outside_code, ccode, outside_main, code)

        self.assertEqual(outside_code, "")
        self.assertEqual(ccode, code)

    def test_compile_func_main_code_outside_main_false_indented_code(self):
        outside_code = ""
        ccode = ""
        outside_main = False
        code = "}\n"

        outside_code, ccode = compile_func_main_code(outside_code, ccode, outside_main, code)

        self.assertEqual(outside_code, "")
        self.assertEqual(ccode, "\t" + code)

    
