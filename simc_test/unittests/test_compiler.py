import unittest
import io
import sys
import subprocess

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
        opcodes = [
            OpCode("print", '"Hello"', None),
            OpCode("var_assign", "a---true", "bool"),
            OpCode("var_assign", "b---M_PI", "double"),
        ]

        includes = set(check_include(opcodes).split("\n"))
        should_be_includes = set(
            ["#include <stdio.h>", "#include <stdbool.h>", "#include <math.h>"]
        )

        self.assertEqual(includes, should_be_includes)

    def test_check_include_empty(self):
        opcodes = [
            OpCode("func_decl", "hello---", ""),
            OpCode("scope_begin", "", ""),
            OpCode("return", "1", ""),
            OpCode("scope_over", "", ""),
            OpCode("MAIN", "", ""),
            OpCode("var_assign", "a---hello()", "int"),
            OpCode("END_MAIN", "", ""),
        ]

        includes = set(check_include(opcodes).split("\n"))
        should_be_includes = set([""])

        self.assertEqual(includes, should_be_includes)

    def test_compile_func_main_code_outside_main_true(self):
        outside_code = ""
        ccode = ""
        outside_main = True
        code = "printf('Hello World')"

        outside_code, ccode = compile_func_main_code(
            outside_code, ccode, outside_main, code
        )

        self.assertEqual(outside_code, code)
        self.assertEqual(ccode, "")

    def test_compile_func_main_code_outside_main_false(self):
        outside_code = ""
        ccode = ""
        outside_main = False
        code = "printf('Hello World')"

        outside_code, ccode = compile_func_main_code(
            outside_code, ccode, outside_main, code
        )

        self.assertEqual(outside_code, "")
        self.assertEqual(ccode, code)

    def test_compile_func_main_code_outside_main_false_indented_code(self):
        outside_code = ""
        ccode = ""
        outside_main = False
        code = "}\n"

        outside_code, ccode = compile_func_main_code(
            outside_code, ccode, outside_main, code
        )

        self.assertEqual(outside_code, "")
        self.assertEqual(ccode, "\t" + code)

    def test_compile_print_statement(self):
        source_code = """
        print('Hello World')
        """

        c_source_code = '#include <stdio.h>\n\tprintf("Hello World");\n'

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_print_statement_string_var(self):
        source_code = """
        var a = "Hello World"
        print(a)
        """

        c_source_code = (
            '#include <stdio.h>\n\tchar* a = "Hello World";\n\tprintf("%s", a);\n'
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_import_statement(self):
        source_code = """
        import geometry
        """

        c_source_code = '\n#include "geometry.h"\n'

        self.__suppress_print()

        try:
            c_compiled_code = self.__compile(source_code)
        except:
            _ = subprocess.getoutput("simpack --name geometry")
            c_compiled_code = self.__compile(source_code)

        self.__release_print()

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_var_assign_statement_without_input(self):
        source_code = """
        var a = 1
        """

        c_source_code = "\n\tint a = 1;\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_var_assign_statement_with_input(self):
        source_code = """
        var a = input("Enter an integer:", "i")
        """

        c_source_code = (
            '#include <stdio.h>\n\tint a;\n\tprintf("Enter an'
            ' integer:");\n\tscanf("%d", &a);\n'
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_ptr_assign_statement(self):
        source_code = """
        var *a = 1
        """

        c_source_code = "#include <stdio.h>\n\tint *a = 1;\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_var_no_assign_statement(self):
        source_code = """
        var a
        """

        c_source_code = "\n\tdeclared a;\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_array_no_assign_statement(self):
        source_code = """
        var a[2]
        """

        c_source_code = "\n\tarr_declared *a;\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_array_assign_statement(self):
        source_code = """
        var a[2] = {1, 2}
        """

        c_source_code = "#include <stdio.h>\n\tint a[2] = {1,2};\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_array_only_assign_statement(self):
        source_code = """
        var a[2]
        a = {1, 2}
        """

        c_source_code = "\n\tint *a;\n\ta = (int [2]){1,2};\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_ptr_no_assign_statement(self):
        source_code = """
        var *a
        """

        c_source_code = "\n\tdeclared *a;\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_assign_statement_without_input(self):
        source_code = """
        var a
        a = 1
        """

        c_source_code = "#include <stdio.h>\n\tint a;\n\ta = 1;\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_assign_statement_with_input(self):
        source_code = """
        var a
        a = input("Enter something:", "f")
        """

        c_source_code = (
            '#include <stdio.h>\n\tfloat a;\n\tprintf("Enter'
            ' something:");\n\tscanf("%f", &a);\n'
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_ptr_only_assign_statement(self):
        source_code = """
        var a = 1
        var *ptr = &a
        *ptr = 2
        """

        c_source_code = (
            "#include <stdio.h>\n\tint a = 1;\n\tint *ptr =  & a;\n\t*ptr = 2;\n"
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_unary_statement(self):
        source_code = """
        var a = 1
        ++a
        """

        c_source_code = "\n\tint a = 1;\n\t++a;\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_func_decl_statement_with_params(self):
        source_code = """
        fun sum(a, b)
            return a + b

        MAIN
            var value = sum(1, 2)
        END_MAIN
        """

        c_source_code = (
            "\n\nint sum(int a, int b) \t{\n\n\treturn a + b;\n}\n\nint main() {\n\tint"
            " value = sum(1, 2);\n\n\treturn 0;\n}\n"
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_func_decl_statement_without_params(self):
        source_code = """
        fun sum()
            return 1 + 2

        MAIN
            var value = sum()
        END_MAIN
        """

        c_source_code = (
            "\n\nint sum(void) \t{\n\n\treturn 1 + 2;\n}\n\nint main() {\n\tint value ="
            " sum();\n\n\treturn 0;\n}\n"
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_func_call_statement_with_params(self):
        source_code = """
        fun hello(a)
            return a

        MAIN
            var a = hello(1)
        END_MAIN
        """

        c_source_code = (
            "\n\nint hello(int a) \t{\n\n\treturn a;\n}\n\nint main() {\n\tint a ="
            " hello(1);\n\n\treturn 0;\n}\n"
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_func_call_statement_without_params(self):
        source_code = """
        fun hello()
            print("Hello")

        MAIN
            hello()
        END_MAIN
        """

        c_source_code = (
            '#include <stdio.h>\n\nvoid hello(void) \t{\n\tprintf("Hello");\n}\n\nint'
            " main() {\n\thello();\n\n\treturn 0;\n}\n"
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_struct_decl_statement(self):
        source_code = """
        struct hello {
            var a = 1
        }
        """

        c_source_code = "\n\nstruct hello \t{\n\tint a = 1;\n} ;\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_struct_instantiate_statement(self):
        source_code = """
        struct hello {
            var a = 1
        }

        MAIN
            hello h
        END_MAIN
        """

        c_source_code = (
            "\n\nstruct hello \t{\n\tint a = 1;\n} ;\n\nint main() {\n\tstruct hello"
            " h;\n\n\treturn 0;\n}\n"
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_scope_begin_scope_over_statements(self):
        source_code = """
        fun hello() {
            print("Hello World")
        }
        """

        c_source_code = (
            '#include <stdio.h>\n\nvoid hello(void) \t{\n\tprintf("Hello World");\n}\n'
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_struct_decl_struct_scope_over_statements(self):
        source_code = """
        struct hello {
            var a = 1
        }
        """

        c_source_code = "\n\nstruct hello \t{\n\tint a = 1;\n} ;\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_main_end_main_statements(self):
        source_code = """
        MAIN
        END_MAIN
        """

        c_source_code = "\n\nint main() {\n\n\treturn 0;\n}\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_for_statement(self):
        source_code = """
        for i in 1 to 10 by +1
        """

        c_source_code = "\n\tfor(int i = 1; i < 10; i+=1) "

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_while_statement(self):
        source_code = """
        MAIN
            while(1) {
                print("Hello")
            }
        END_MAIN
        """

        c_source_code = (
            "#include <stdio.h>\n\nint main() {\n\twhile(1)"
            ' \t{\n\tprintf("Hello");\n\t}\n\n\treturn 0;\n}\n'
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_do_while_do_statements(self):
        source_code = """
        MAIN
            do {
                print("Hello")
            } 
            while(1 == 2)
        END_MAIN
        """

        c_source_code = (
            "#include <stdio.h>\n\nint main() {\n\tdo"
            ' \t{\n\tprintf("Hello");\n\t}\n\twhile(1 == 2);\n\treturn 0;\n}\n'
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_if_else_if_else_statements(self):
        source_code = """
        MAIN
            if(1)
                print("Hello")
            else if(2)
                print("Bye")
            else
                print("World")
        END_MAIN
        """

        c_source_code = (
            '#include <stdio.h>\n\nint main() {\n\tif(1) \tprintf("Hello");\n\telse'
            ' if(2) \tprintf("Bye");\n\telse \tprintf("World");\n\n\treturn 0;\n}\n'
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_exit_statement(self):
        source_code = """
        MAIN
            exit(0)
        END_MAIN
        """

        c_source_code = "\n\nint main() {\n\texit(0);\n\n\treturn 0;\n}\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_return_statement(self):
        source_code = """
        MAIN
            return 1
        END_MAIN
        """

        c_source_code = "\n\nint main() {\n\n\treturn 1;\n\n}\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_break_statement(self):
        source_code = """
        MAIN
            break
        END_MAIN
        """

        c_source_code = "\n\nint main() {\n\tbreak;\n\n\treturn 0;\n}\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_continue_statement(self):
        source_code = """
        MAIN
            continue
        END_MAIN
        """

        c_source_code = "\n\nint main() {\n\tcontinue;\n\n\treturn 0;\n}\n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_single_line_comment_statement(self):
        source_code = """
        // This is a single line comment
        """

        c_source_code = "\n\t//  This is a single line comment \n"

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_multi_line_comment_statement(self):
        source_code = """
        /* This is a multi-line comment
        And it spans multiple lines */
        """

        c_source_code = (
            "\n/*  This is a multi-line comment\n        And it spans multiple lines"
            " */\n"
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_switch_case_default_statements(self):
        source_code = """
        MAIN
            switch(1) {
                case 1: {
                    print("Hello")
                    break
                }
                default: {
                    print("World")
                    break
                }
            }
        END_MAIN
        """

        c_source_code = (
            "#include <stdio.h>\n\nint main() {\n\tswitch(1) \t{\n\tcase"
            ' 1:\n\t{\n\tprintf("Hello");\n\tbreak;\n\t}\n\tdefault:\n\t{\n\tprintf("World");\n\tbreak;\n\t}\n\t}\n\n\treturn'
            " 0;\n}\n"
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)

    def test_compile_raw_c_statements(self):
        source_code = """
        BEGIN_C
            int a = 1;
            printf("%d", a);
        END_C
        print("Hello")
        """

        c_source_code = (
            '#include <stdio.h>\n\n            int a = 1;\n            printf("%d",'
            ' a);\n\tprintf("Hello");\n'
        )

        c_compiled_code = self.__compile(source_code)

        self.assertEqual(c_source_code, c_compiled_code)
