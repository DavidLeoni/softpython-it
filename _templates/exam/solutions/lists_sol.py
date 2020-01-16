

class MyClass:

    """ 
        This class does... stuff
    """
    def do_something(self):
        #jupman-raise
        print("Doing something")
        #/jupman-raise

 
    def do_something_else(self):
        #jupman-raise
        print("Doing something else")
        helper(5)
        #/jupman-raise
        
#jupman-strip
def helper(x):
    return x + 1
#/jupman-strip
