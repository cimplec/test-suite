import unittest

from simc.symbol_table import SymbolTable

class TestSymbolTable(unittest.TestCase):

    ####################################################################################################
    # TESTS
    ####################################################################################################
    def test_entry(self):
        symbol_table = SymbolTable()

        id = symbol_table.entry(value="my_var", type="int", typedata="variable")

        self.assertEqual(id, 1)
        self.assertEqual(symbol_table.symbol_table, {1: ["my_var", "int", "variable"]})

    def test_get_by_id_is_present(self):
        symbol_table = SymbolTable()

        _ = symbol_table.entry(value="my_var", type="int", typedata="variable")
        _ = symbol_table.entry(value="my_var_1", type="float", typedata="variable")

        entry = symbol_table.get_by_id(2)

        self.assertEqual(entry, ["my_var_1", "float", "variable"])

    def test_get_by_id_not_present(self):
        symbol_table = SymbolTable()

        _ = symbol_table.entry(value="my_var", type="int", typedata="variable")
        _ = symbol_table.entry(value="my_var_1", type="float", typedata="variable")

        entry = symbol_table.get_by_id(10)

        self.assertEqual(entry, [None, None, None])

    def test_get_by_symbol_is_present(self):
        symbol_table = SymbolTable()

        _ = symbol_table.entry(value="my_var", type="int", typedata="variable")
        _ = symbol_table.entry(value="my_var_1", type="float", typedata="variable")

        id = symbol_table.get_by_symbol("my_var")

        self.assertEqual(id, 1)

    def test_get_by_symbol_not_present(self):
        symbol_table = SymbolTable()

        _ = symbol_table.entry(value="my_var", type="int", typedata="variable")
        _ = symbol_table.entry(value="my_var_1", type="float", typedata="variable")

        id = symbol_table.get_by_symbol("my_variable")

        self.assertEqual(id, -1)