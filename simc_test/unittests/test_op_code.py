import unittest

from simc.op_code import OpCode

class TestOpCode(unittest.TestCase):
    
    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test___str__match_case(self):
        opcode = OpCode(opcode="print", val='"Hello World"')

        self.assertEqual(str(opcode), str(OpCode('print', '"Hello World"', None)))

    def test___str__no_match_case(self):
        opcode = OpCode(opcode="var_assign", val='a--1+2')

        self.assertNotEqual(str(opcode), str(OpCode('print', '"Hello World"', None)))