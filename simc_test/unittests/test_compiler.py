import unittest
import io
import sys

from simc.compiler import *
from simc.symbol_table import SymbolTable
from simc.lexical_analyzer import LexicalAnalyzer
from simc.parser.simc_parser import parse


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

    def __compile(self, source_code):
        with open("simc-compiler-test.simc", "w") as file:
            file.write(source_code)

        table = SymbolTable()

        lexer = LexicalAnalyzer("simc-compiler-test.simc", table)
        tokens, _ = lexer.lexical_analyze()

        opcodes = parse(tokens, table)

        compile(opcodes, "simc-compiler-test.c", table)

        with open("simc-compiler-test.c", "r") as file:
            return file.read()

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

    def test_compile_print_statement(self):
        source_code = """
        print('Hello World')
        """

        c_source_code = '#include <stdio.h>\n\tprintf("Hello World");\n'

        c_compiled_code = self.__compile(source_code)
        
        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_import_statement(self):
        source_code = """
        import geometry
        """

        c_source_code = '\n#include "geometry.h"\n'

        c_compiled_code = self.__compile(source_code)
        
        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_ptr_assign_statement(self):
        source_code = """
        var *a = 1
        """

        c_source_code = '#include <stdio.h>\n\tint *a = 1;\n'

        c_compiled_code = self.__compile(source_code)
        
        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_var_no_assign_statement(self):
        source_code = """
        var a
        """

        c_source_code = '\n\tdeclared a;\n'

        c_compiled_code = self.__compile(source_code)
        
        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_ptr_no_assign_statement(self):
        source_code = """
        var *a
        """

        c_source_code = '\n\tdeclared *a;\n'

        c_compiled_code = self.__compile(source_code)
        
        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_array_no_assign_statement(self):
        source_code = """
        var a[2]
        """

        c_source_code = '\n\tdeclared a[2];\n'

        c_compiled_code = self.__compile(source_code)
        
        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_array_assign_statement(self):
        source_code = """
        var a[2] = {1, 2}
        """

        c_source_code = '#include <stdio.h>\n\tint a[2] = {1,2};\n'

        c_compiled_code = self.__compile(source_code)
        
        self.assertEqual(c_source_code, c_compiled_code)