
# This is the library to be included in Jupyter notebooks.
# David Leoni Nov 2017 

import sys
import unittest
import inspect
import os
import networkx as nx
import conf
from IPython.core.display import HTML


def get_class(meth):
    """
        Taken from here: https://stackoverflow.com/a/25959545
    """

    if inspect.ismethod(meth):
        for cls in inspect.getmro(meth.__self__.__class__):
            if cls.__dict__.get(meth.__name__) is meth:
                 return cls
        meth = meth.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)  # handle special descriptor objects

def run(classOrMethodOrModule):    
    """ Runs test class or method or Module. Doesn't show code nor output in html.
    
        todo look at test order here: http://stackoverflow.com/a/18499093        
    """ 
    
    if  inspect.isclass(classOrMethodOrModule) and issubclass(classOrMethodOrModule, unittest.TestCase):        
        testcase = classOrMethodOrModule
        suite = unittest.TestLoader().loadTestsFromTestCase(testcase)
    elif inspect.isfunction(classOrMethodOrModule):
        meth = classOrMethodOrModule
        suite = unittest.TestSuite()
        testcase = get_class(meth)
        suite.addTest(testcase(meth.__name__))
    elif inspect.ismodule(classOrMethodOrModule):
        module = classOrMethodOrModule
        suite = unittest.TestLoader().loadTestsFromModule(module)
    else:
        raise Exception("Accepted parameters are either a TestCase class, a TestCase method or a test module. Found instead: " + str(classOrMethodOrModule))

    unittest.TextTestRunner(verbosity=1,stream=sys.stderr).run( suite )

def show_run(classOrMethod):    
    """ Runs test class or method. Code is not shown, but output is

        @since 0.19
        @deprecated Just use run()
    """    
    run(classOrMethod)
        
def init(root=''):
    """ To be called at the beginning of Jupyter sheets
    """
    on_rtd = os.environ.get('READTHEDOCS') == 'True'
    
    if on_rtd:
        # on RTD we don't inject anything, files are set in sphinx conf.py
        print("")
    else:
        # Hacky stuff, because Jupyter only allows to set a per user custom js, we want per project js
        
        css = open(root + "overlay/_static/css/jupman.css", "r").read()
        tocjs = open(root + "overlay/_static/js/toc.js", "r").read()
        js = open(root + "overlay/_static/js/jupman.js", "r").read()

        ret = "<style>\n" 
        ret += css
        ret += "\n </style>\n"

        ret +="\n"

        ret += "<script>\n"
        ret += "var JUPMAN_IN_JUPYTER = true;"  
        ret += "\n"
        ret += tocjs
        ret += "\n"    
        ret += js
        ret += "\n</script>\n"

    return  HTML(ret)

def init_exam(exam_date):
    """ To be called at the beginning of Jupyter exam sheets
        
        exam_date : exam date string in the format 'yyyy-mm-dd'
    """
    if exam_date != '_JM_(exam.date)':
        conf.parse_date(exam_date) # little hack so the template can work somewhat properly
    import sys
    sys.path.append('solutions/')
    sys.path.append('exercises/')
    return init('../../')


def assertNotNone(ret, function_name):
    return function_name + " specs say nothing about returning objects! Instead you are returning " + str(ret)
