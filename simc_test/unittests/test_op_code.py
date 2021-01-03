import unittest
import os

from simc.op_code import OpCode

class TestOpCode(unittest.TestCase):
    
    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test___str__(self):
        opcode = OpCode(opcode="print", val='"Hello World"')

        self.assertEqual(str(opcode), str(OpCode('print', '"Hello World"', None)))