
# This is the library to be included in Jupyter notebooks.
# David Leoni Sept 2017 

import sys
import unittest
import inspect
import os
import networkx as nx
import conf
from IPython.core.display import HTML


# taken from here: http://stackoverflow.com/a/961057
def get_class(meth):
    for cls in inspect.getmro(meth.im_class):
        if meth.__name__ in cls.__dict__: 
            return cls
    return None


def run(classOrMethod):    
    """ Runs test class or method. Doesn't show code nor output in html.
    
        todo look at test order here: http://stackoverflow.com/a/18499093        
    """ 
    
    if  inspect.isclass(classOrMethod) and issubclass(classOrMethod, unittest.TestCase):        
        testcase = classOrMethod
        suite = unittest.TestLoader().loadTestsFromTestCase(testcase)
        unittest.TextTestRunner(verbosity=1,stream=sys.stderr).run( suite )
    elif inspect.ismethod(classOrMethod):
        meth = classOrMethod
        suite = unittest.TestSuite()
        testcase = get_class(meth)
        suite.addTest(testcase(meth.__name__))
        unittest.TextTestRunner(verbosity=1,stream=sys.stderr).run( suite )
    else:
        raise Exception("Accepted parameters are a TestCase class or a TestCase method. Found instead: " + str(classOrMethod))


def show_run(classOrMethod):    
    """ Runs test class or method. Code is not shown, but output is
    
        @since 0.19
    """    
    run(classOrMethod)
        
def init():
    """ To be called at the beginning of Jupyter sheets
    """
    css = open("./css/jupman.css", "r").read()

    tocjs = open("./js/toc.js", "r").read()

    js = open("./js/jupman.js", "r").read()

    ret = "<style>\n" 
    ret += css
    ret += "\n </style>\n"
    
    ret +="\n"
    
    ret += "<script>\n"
    on_rtd = os.environ.get('READTHEDOCS') == 'True'
    if not on_rtd:
        ret += "\n"
        ret += tocjs
        ret += "\n"
    
    ret += js
    ret += "\n</script>\n"

    return  HTML(ret)

def init_exam(exam_date):
    """ To be called at the beginning of Jupyter exam sheets
        exam_date = exam date string in the format 'yyyy-mm-dd'
    """
    import sys
    sys.path.append('private/exams/' + exam_date + '/solutions')
    sys.path.append('private/exams/' + exam_date + '/' + conf.filename + '-' + exam_date+'-FIRSTNAME-LASTNAME-ID')
    sys.path.append('exams/' + exam_date + '/solutions')
    sys.path.append('exams/' + exam_date + '/exercises')
    return init()


def assertNotNone(ret, function_name):
    return function_name + " specs say nothing about returning objects! Instead you are returning " + str(ret)
