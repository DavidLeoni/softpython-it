
from lists_sol import *

import unittest


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


