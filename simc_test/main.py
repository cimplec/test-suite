import unittest
import os

from .test_global_helpers import TestGlobalHelpers

def run():
    test_classes_to_run = [
        TestGlobalHelpers
    ]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(big_suite)

    if os.path.exists("testing.simc"):
        os.remove("testing.simc")