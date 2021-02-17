import unittest
import io
import sys
import subprocess

from simc.parser.simc_parser import *
from simc.token_class import Token
from simc.symbol_table import SymbolTable
from simc.lexical_analyzer import LexicalAnalyzer


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

    def __write_to_file(self, source_code):
        with open("simc-parser-test.simc", "w") as file:
            file.write(source_code)

    def __get_opcodes(self, source_code):
        self.__write_to_file(source_code)

        table = SymbolTable()
        lexer = LexicalAnalyzer("simc-parser-test.simc", table)
        tokens, _ = lexer.lexical_analyze()

        opcodes = parse(tokens, table)

        return opcodes

    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test_expression_index_out_bounds_array_indexing(self):
        source_code = """
        MAIN
            var a[2] = {1, 2}
            var b = a[10]
        END_MAIN
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_expression_index_is_not_integer(self):
        source_code = """
        MAIN
            var a[2] = {1, 2}
            var b = a[3.14]
        END_MAIN
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_expression_array_indexing(self):
        source_code = """
        MAIN
            var a[2] = {1, 2}
            var b = a[1]
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)
        self.assertEqual(opcodes[-2], OpCode("var_assign", "b---a[1]", "int"))

    def test_expression_type_casting(self):
        source_code = """
        MAIN
            var a[2] = {1, 2}
            var b = int(3.14) + 2
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)
        self.assertEqual(
            opcodes[-2], OpCode("var_assign", "b---(int)(3.14) + 2", "int")
        )

    def test_expression_size_operator(self):
        source_code = """
        MAIN
            var a = 3.14
            var b = size(a)
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)
        self.assertEqual(opcodes[-2], OpCode("var_assign", "b---sizeof(a)", "int"))

    def test_expression_type_operator(self):
        source_code = """
        MAIN
            var a = 3.14
            var b = type(a)
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)
        self.assertEqual(opcodes[-2], OpCode("var_assign", 'b---"float"', "string"))

    def test_expression_unknown_variable_error(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("assignment", "", 1),
            Token("number", 2, 1),
            Token("newline", "", 1),
            Token("print", "", 2),
            Token("left_paren", "", 2),
            Token("string", 3, 2),
            Token("right_paren", "", 2),
            Token("call_end", "", 2),
            Token("newline", "", 2),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["a", "var", "variable", "", ""],
            2: ["1", "int", "constant", "", ""],
            3: ['"value = {a}"', "string", "constant", "", ""],
        }

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = expression(tokens=tokens_list, i=7, table=table, msg="")

        self.__release_print()

    # def test_expression_cannot_find_type_error(self):
    #     tokens_list = [
    #         Token("var", "", 1),
    #         Token("id", 1, 1),
    #         Token("newline", "", 2),
    #         Token("print", "", 2),
    #         Token("left_paren", "", 2),
    #         Token("id", 1, 2),
    #         Token("right_paren", "", 2),
    #         Token("newline", "", 2),
    #     ]
    #     table = SymbolTable()
    #     table.symbol_table = {1: ["a", "var", "variable", ""]}

    #     self.__suppress_print()

    #     with self.assertRaises(SystemExit):
    #         _ = parse(tokens=tokens_list, table=table)

    #     self.__release_print()

    def test_print_statement_expected_left_paren_error(self):
        tokens_list = [Token("print", "", 1), Token("var", "", 1)]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = print_statement(
                tokens=tokens_list, i=1, table=table, func_ret_type={}, num_opcodes=-1
            )

        self.__release_print()

    def test_print_statement_no_error(self):
        tokens_list = [
            Token("print", "", 1),
            Token("left_paren", "", 1),
            Token("string", 1, 1),
            Token("right_paren", "", 1),
            Token("newline", "", 1),
        ]
        table = SymbolTable()
        table.entry('"hello world"', "string", "constant")

        opcode, _, _ = print_statement(
            tokens=tokens_list, i=1, table=table, func_ret_type={}, num_opcodes=-1
        )

        self.assertEqual(opcode, OpCode("print", '"hello world"', None))

    def test_unary_statement_pre_increment(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("assignment", "", 1),
            Token("number", 2, 1),
            Token("newline", "", 1),
            Token("increment", "", 2),
            Token("id", 1, 2),
            Token("newline", "", 2),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["a", "var", "variable", "", ""],
            2: ["1", "int", "constant", "", ""],
        }

        opcodes = parse(tokens=tokens_list, table=table)

        self.assertEqual(opcodes[1], OpCode("unary", "++ a", None))

    def test_unary_statement_post_decrement(self):
        tokens_list = [
            Token("var", "", 1),
            Token("id", 1, 1),
            Token("assignment", "", 1),
            Token("number", 2, 1),
            Token("newline", "", 1),
            Token("id", 1, 2),
            Token("decrement", "", 2),
            Token("newline", "", 2),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["a", "var", "variable", "", ""],
            2: ["1", "int", "constant", "", ""],
        }

        opcodes = parse(tokens=tokens_list, table=table)

        self.assertEqual(opcodes[1], OpCode("unary", "a -- ", None))

    def test_exit_statement_expected_left_paren_error(self):
        tokens_list = [Token("exit", "", 1), Token("print", "", 1)]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = exit_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_exit_statement_expected_number_error(self):
        tokens_list = [
            Token("exit", "", 1),
            Token("left_paren", "", 1),
            Token("print", "", 1),
        ]
        table = SymbolTable()

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = exit_statement(tokens=tokens_list, i=1, table=table, func_ret_type={})

        self.__release_print()

    def test_exit_no_error(self):
        tokens_list = [
            Token("exit", "", 1),
            Token("left_paren", "", 1),
            Token("number", 1, 1),
            Token("right_paren", "", 1),
        ]
        table = SymbolTable()
        table.entry("0", "int", "constant")

        opcode, _, _ = exit_statement(
            tokens=tokens_list, i=1, table=table, func_ret_type={}
        )

        self.assertEqual(opcode, OpCode("exit", "0", None))

    def test_skip_all_nextlines_no_nextline(self):
        tokens_list = [Token("print", "", 1), Token("var", "", 1)]

        i = 0
        i = skip_all_nextlines(tokens=tokens_list, i=0)

        self.assertEqual(i, 1)

    def test_skip_all_nextlines_some_nextline(self):
        tokens_list = [
            Token("newline", "", 1),
            Token("newline", "", 1),
            Token("print", "", 1),
        ]

        i = 0
        i = skip_all_nextlines(tokens=tokens_list, i=0)

        self.assertEqual(i, 2)

    def test_parse_empty_function_body_error(self):
        tokens_list = [
            Token("fun", "", 1),
            Token("id", 1, 1),
            Token("left_paren", "", 1),
            Token("right_paren", "", 1),
            Token("newline", "", 1),
            Token("newline", "", 1),
            Token("MAIN", "", 2),
        ]
        table = SymbolTable()
        table.entry("func", "var", "variable")

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = parse(tokens=tokens_list, table=table)

        self.__release_print()

    def test_parse_scope_begin_scope_over_opcodes(self):
        source_code = """
        fun hello() {
            return 1
        }

        MAIN
            var a = hello()
        END_MAIN
        """
        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[1], OpCode("scope_begin", "", ""))
        self.assertEqual(opcodes[3], OpCode("scope_over", "", ""))

    def test_parse_print_cannot_be_called_from_struct_scope_error(self):
        source_code = """
        struct hello {
            print("Hello")
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_import_cannot_be_called_from_struct_scope_error(self):
        source_code = """
        struct hello {
            import geometry
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_import_expected_module_name_error(self):
        source_code = """
        import 
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_import_no_error(self):
        source_code = """
        import geometry
        """

        self.__suppress_print()

        try:
            opcodes = self.__get_opcodes(source_code)
        except:
            _ = subprocess.getoutput("simpack --name geometry")
            opcodes = self.__get_opcodes(source_code)

        self.__release_print()

        self.assertEqual(opcodes[0], OpCode("import", "geometry"))

    def test_parse_func_call_opcode(self):
        source_code = """
        fun hello()
            print("Hello")

        MAIN
            hello()
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[5], OpCode("func_call", "hello---", ""))

    def test_parse_struct_cannot_be_called_from_struct_scope_error(self):
        source_code = """
        struct hello {
            variable vary
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_struct_not_declared_error(self):
        source_code = """
        MAIN
            hello h
        END_MAIN
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_struct_instantiate_opcode(self):
        source_code = """
        struct hello {
            var a = 1
        }
        MAIN
            hello h
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[-2], OpCode("struct_instantiate", "hello---h", None))

    def test_parse_cannot_define_function_inside_struct_scope(self):
        source_code = """
        struct hello {
            fun hello()
                print("Hello")
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_struct_cannot_be_declared_inside_struct_scope(self):
        source_code = """
        struct hello {
            struct variable {
                var a = 1
            }
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_struct_cannot_be_declared_inside_function_scope(self):
        source_code = """
        fun hello() {
            struct variable {
                var a = 1
            }
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_define_function_inside_another_function(self):
        source_code = """
        MAIN
            fun hello()
                print("Hello")
        END_MAIN
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_struct_scope_over_opcode(self):
        source_code = """
        struct hello {
            var a = 1
        }
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[-1], OpCode("struct_scope_over", "", ""))

    def test_parse_cannot_have_more_than_one_main_error(self):
        source_code = """
        MAIN
        MAIN
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_main_end_main_opcodes(self):
        source_code = """
        MAIN

        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[0], OpCode("MAIN", "", ""))
        self.assertEqual(opcodes[1], OpCode("END_MAIN", "", ""))

    def test_parse_no_matching_end_main_for_main(self):
        source_code = """
        END_MAIN
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_do_inside_struct_scope(self):
        source_code = """
        struct hello {
            do {}
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_do_inside_global_scope(self):
        source_code = """
        do {}
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_do_opcode(self):
        source_code = """
        MAIN
            do {}
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[1], OpCode("do", "", ""))

    def test_parse_cannot_call_while_inside_struct_scope(self):
        source_code = """
        struct hello {
            while()
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_while_inside_global_scope(self):
        source_code = """
        while()
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_if_inside_struct_scope(self):
        source_code = """
        struct hello {
            if()
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_if_inside_global_scope(self):
        source_code = """
        if()
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_else_inside_struct_scope(self):
        source_code = """
        struct hello {
            else
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_else_inside_global_scope(self):
        source_code = """
        else
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_else_if_else_opcodes(self):
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

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[3], OpCode("else_if", "2", None))
        self.assertEqual(opcodes[5], OpCode("else", "", ""))

    def test_parse_no_matching_if_for_else_error(self):
        source_code = """
        else
            print('World')
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_exit_inside_struct_scope(self):
        source_code = """
        struct hello {
            exit(0)
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_exit_inside_global_scope(self):
        source_code = """
        exit(0)
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_return_inside_struct_scope(self):
        source_code = """
        struct hello {
            return 0
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_return_inside_global_scope(self):
        source_code = """
        return 0
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_return_outside_any_function_error(self):
        source_code = """
        return 1
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_return_opcode(self):
        source_code = """
        fun hello()
            return 1+2

        MAIN
            var a = hello()
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[2], OpCode("return", "1 + 2", ""))

    def test_parse_cannot_call_break_inside_struct_scope(self):
        source_code = """
        struct hello {
            break
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_break_inside_global_scope(self):
        source_code = """
        break
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_break_opcode(self):
        source_code = """
        MAIN
            break
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[1], OpCode("break", "", ""))

    def test_parse_cannot_call_continue_inside_struct_scope(self):
        source_code = """
        struct hello {
            continue
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_continue_inside_global_scope(self):
        source_code = """
        continue
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_continue_opcode(self):
        source_code = """
        MAIN
            continue
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[1], OpCode("continue", "", ""))

    def test_parse_single_line_comment_opcode(self):
        source_code = """
        // This is a comment
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(
            opcodes[0], OpCode("single_line_comment", " This is a comment", "")
        )

    def test_parse_multi_line_comment_opcode(self):
        source_code = """
        /* This is a comment
        Spanning multiple lines */
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(
            opcodes[0],
            OpCode(
                "multi_line_comment",
                """ This is a comment
        Spanning multiple lines """,
                "",
            ),
        )

    def test_parse_cannot_call_switch_inside_struct_scope(self):
        source_code = """
        struct hello {
            switch
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_switch_inside_global_scope(self):
        source_code = """
        switch
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_default_inside_struct_scope(self):
        source_code = """
        struct hello {
            default
        }
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_cannot_call_default_inside_global_scope(self):
        source_code = """
        default
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_missing_colon_after_default_error(self):
        source_code = """
        default print
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_default_opcode(self):
        source_code = """
        MAIN
            default:
        END_MAIN
        """

        opcodes = self.__get_opcodes(source_code)

        self.assertEqual(opcodes[1], OpCode("default", "", ""))

    def test_parse_more_than_one_main_error(self):
        source_code = """
        MAIN
        MAIN
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()

    def test_parse_no_matching_end_main_for_main_error(self):
        source_code = """
        MAIN
        """

        self.__suppress_print()

        with self.assertRaises(SystemExit):
            _ = self.__get_opcodes(source_code)

        self.__release_print()
