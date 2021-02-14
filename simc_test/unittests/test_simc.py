import unittest
import os
import subprocess


class TestSimc(unittest.TestCase):

    ####################################################################################################
    # HELPERS
    ####################################################################################################
    def __write_to_file(self, filename, string):
        with open(filename, "w") as file:
            file.write(string)

    def __assertListEquality(self, sources, matches):
        for source, match in zip(sources, matches):
            self.assertEqual(source, match)

    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test_display_tokens(self):
        source_code = "print('Hello World')"

        self.__write_to_file("test-simc.simc", source_code)

        output = subprocess.getoutput("simc test-simc.simc token").split("\n")

        compare_list = [
            "Token(print, , 1)",
            "Token(left_paren, , 1)",
            "Token(string, 1, 1)",
            "Token(right_paren, , 1)",
            "\x1b[92mC code generated at test-simc.c! \x1b[m",
        ]

        self.__assertListEquality(output, compare_list)

    def test_display_opcodes(self):
        source_code = "print('Hello World')"

        self.__write_to_file("test-simc.simc", source_code)

        output = subprocess.getoutput("simc test-simc.simc opcode").split("\n")

        compare_list = [
            "OpCode('print', '\"Hello World\"', 'None')",
            "\x1b[92mC code generated at test-simc.c! \x1b[m",
        ]

        self.__assertListEquality(output, compare_list)
