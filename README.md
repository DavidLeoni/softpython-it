
# Jupman

Jupyter Python worksheets build system. Uses NbSphinx and ReadTheDocs

## Installation instructions

(Instructions are for Ubuntu, on Windows they may differ)

1. On Github, fork [jupman project](https://github.com/DavidLeoni/jupman) to create yours, for example `my-project`.
**IMPORTANT: choose a name which is NOT already on [ReadTheDocs](http://readthedocs.org)**
2. Create a [ReadTheDocs account](http://readthedocs.org) **using the same name as in Github**
so the address in readthedocs will be something like _my-project.readthedocs.org_.
Use ReadTheDocs panels to link the project to your Github repository.
3. Clone the `my-project` on your computer
4. Install Python 2.7
5. [Install Jupyter](http://jupyter.org/install.html)
6. Install Python modules,from the root of the project, run:
    ```bash
    sudo python -m pip install -r requirements.txt
    ```
7. Edit as needed `conf.py`, which is the configuration file for Sphinx. In particular, you *MUST** edit the sections marked with `TODO`
8. Try to [launch a build](#building-the-manual)
9. If everything works fine on your computer, push changes back to Github
10. Go back to ReadTheDocs and try to run a build. Hopefully your project will become available on something like _my-project.readthedocs.org_

## Building the manual

To build the website, go to console and from the root of the directory run:

```bash
python build.py
```

Site will be created in `_build/` folder.

**NOTE: to also generate PDF you will need to install Latex environment**


For help: 

```bash
python build.py -h
```

For quick build that only produces html:


```bash
python build.py -q
```


## Publishing

For publishing, the system uses ReadTheDocs so it is enough to push to master and ReadTheDocs will do the rest (for example, for jupman it is at address [jupman.readthedocs.io](jupman.readthedocs.io) 

**IMPORTANT: ReadTheDocs WILL _NOT_ execute Jupyter notebooks because of [this bug](https://github.com/DavidLeoni/softpython/issues/2)**

## Editing the worksheets

Here we give an overview of how to edit worksheets. More info can be found in [Jupman tests notebook](jupman-tests.ipynb)

### Running jupyter

First of all, run Jupyter from the root of the directory


```bash
    jupyter notebook
```

* Python code common to all worksheets is in [jupman.py](jupman.py)
* Javascript code common to all worksheets is in [js/jupman.js](js/jupman.js)
* CSS common to all worksheets is in [css/jupman.css](css/jupman.css)

Each worksheet must start with this Python code:

```python
import jupman
jupman.init()
```

Running it will create the sidebar even when editing in Jupyter. If you want to refresh the sidebar, just run again the cell.

### Hiding cells

To hide cells (like for example the `import jupman` code), click `View->Cell toolbar -> Edit metadata`
and add `"nbsphinx": "hidden"` to the JSON (see also original [NBSphinx docs](
https://nbsphinx.readthedocs.io/en/0.2.14/hidden-cells.html#Hidden-Cells
)).

(Before porting to NBSphinx some cell hiding for Jupman stuff was automated using Javascript, maybe we will reintroduce the automation in the future)

### Source code for exercises

To avoid import problems ([see related issue](https://github.com/DavidLeoni/softpython/issues/3)), 
currently it is best to put all python files in the root of the project.

### Launch unit tests

Inside worksheets you can run `unittest` tests. 

To run all the tests of a test class, write like this

```python
jupman.run(NameOfTheTestClass)
```

To run a single method, write like this:

```python
jupman.run(NameOfTheTestClass.nameOfTheMethod)
```

## Exams

Jupman comes with a script to manage exams called `exam.py`, which allows to manage the full cycle of an exam.

### What is an exam

**Exam text** is represented as Jupyter notebooks, which are taken from [templates/exam/exam-yyyy-mm-dd.ipynb](templates/exam/exam-yyyy-mm-dd.ipynb)

**exercises for students**: they are supposed to be plain python files plus unittests and relative solutions. 

**Marks spreadsheet**: By default there is also an OpenOffice spreadsheet to give marks, in case you need it. 

When you initialize an exam with the `init` command, for example for date `2017-12-31`, all the presets in `templates/exam/` are copied to `private/2017-12-31`. Presets can be changed at will to suit your needs.

System is flexible enough so you can privately work on next exams in `private/` folder and still being able to publish modifications to main website. After an exam, you can copy the private exam to the public folders in `past-exams/`.    

### Exam commands

To see the help:

```bash
python exam.py -h
```

To see help for a particular subcommand, like i.e. `init`, type the subcommand followed by `-h` :

```bash
python exam.py init -h
```

Running commands should be quite self-explanatory.

NOTE: as of today (Sept 2017) software may contain bugs, but at least we check for major misuses 
(like trying to overwrite exeisting exams). 

In the file [create-exam-example.sh](create-exam-example.sh) there is a typical run of the 
script, which creates the example exam for date `2000-12-31`. Here is the output:


```bash

```

