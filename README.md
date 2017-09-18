

Jupyter Python worksheets build system. Uses NbSphinx and ReadTheDocs


## Building the manual

### Installation instructions

Instructions are for Ubuntu, on Windows they may differ:

1. Install Python 2.7
2. [Install Jupyter](http://jupyter.org/install.html)
3. Install Python modules:

From the root of the project, run:

```bash
 sudo python -m pip install -r requirements.txt
```

### Building

To build the website, while in the console, from the root of the directory run:

```bash
python jubuild.py
```

Site will be created in `_build/` folder.

**NOTE: to also generate PDF you will need to install Latex environment**


For help: 

```bash
python jub.py -h
```

For quick build that only produces html:


```bash
python jub.py -q
```


### Publishing

For publishing, we use ReadTheDocs at address <a href="http://jubuild.readthedocs.io" target="_blank">softpython.readthedocs.io</a>, 
so it is enough to push to master and ReadTheDocs will do the rest.

**NOTE: ReadTheDocs WILL _NOT_ execute Jupyter notebooks because of [this bug](https://github.com/DavidLeoni/softpython/issues/2)**

### Editing the worksheets

First of all, run Jupyter from the root of the directory


```bash
    jupyter notebook
```

* Python code common to all worksheets is in [jub.py](jub.py)
* Javascript code common to all worksheets is in [js/jublib.js](js/jub.js)
* CSS common to all worksheets is in [css/jublib.css](css/jub.css)

Each worksheet must start with this Python code:

```python
import jublib
jub.init()
```

Running it will create the sidebar even when editing in Jupyter. If you want to refresh the sidebar, just run again the cell.
Usually, cells with algolab stuff should be hidden in the built manual.

### Source code for exercises

To avoid import problems ([see related issue](https://github.com/DavidLeoni/softpython/issues/3)), 
currently it is best to put all python files in the root of the project.


#### Launch unit tests

Inside worksheets you can run `unittest` tests. 

To run all the tests of a test class, write like this

```python
jub.run(NameOfTheTestClass)
```

To run a single method, write like this:

```python
jub.run(NameOfTheTestClass.nameOfTheMethod)
```

