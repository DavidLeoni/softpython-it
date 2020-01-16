#NOTE: this test is meant to be run from jupman project root, not from _test folder

import jupman as jm
import pytest 

def test_init():
    jm.init()
    
    
class MyClass:
    def my_meth(self):
        pass
    
def test_get_class():
    mc = MyClass()
    
    assert jm.get_class(mc.my_meth) == MyClass
    
    with pytest.raises(ValueError):
        jm.get_class("ciao")
    
    