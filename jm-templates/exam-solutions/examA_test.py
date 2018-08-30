from exercise1_solution import *

import unittest

def is_env_working():
    """ Don't modify this function"""
    return "yes"


class EnvWorkingTest(unittest.TestCase):
    """ Just to test you can run tests.  """
    
    def test_env_working(self):
        """ This sest should always pass."""
        self.assertEqual(is_env_working(), "yes")

class DoSomethingTest(unittest.TestCase):
    
    def test_empty(self):
	
        d = MyClass()
        d.do_something()
        self.assertEqual(1,1) # second is the expected one

class DoSomethingElseTest(unittest.TestCase):
    
    def test_empty(self):

        d = MyClass()
        d.do_something_else()
        self.assertEqual(1,1) # second is the expected one


