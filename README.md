
# Jupman

Jupyter Python 3 worksheets build system and exam manager. See Jupman manual at http://jupman.readthedocs.io

Jupman uses [NbSphinx](http://nbsphinx.readthedocs.io/) and [ReadTheDocs](https://readthedocs.org). 

## Installation

(Instructions are for Ubuntu, on Windows may differ)

1. On Github, fork [jupman project](https://github.com/DavidLeoni/jupman) to create yours, for example `my-project`.
**IMPORTANT: choose a name which is NOT already on [ReadTheDocs](http://readthedocs.org)**
2. Create a [ReadTheDocs account](http://readthedocs.org) **using the same name as in Github**
so the address in readthedocs will be something like _my-project.readthedocs.org_.
Use ReadTheDocs panels to link the project to your Github repository.
3. On your computer, clone the `my-project` from Github 
4. Install Python 3.5+
5. [Install Jupyter](http://jupyter.org/install.html)
6. Install Python modules,from the root of the project, run:
    ```bash
    sudo python3 -m pip install -r requirements.txt
    ```
## Getting Started
1. Edit as needed `conf.py`, which is the configuration file for Sphinx. In particular, you *MUST** edit the sections marked with `TODO`
2. Try to launch a build
```bash
python3 build.py
```
For more info, see [related section](#building-the-manual)
3. If everything works fine on your computer, push changes back to Github
4. Go back to ReadTheDocs and try to run a build. Hopefully your project will become available on something like _my-project.readthedocs.org_
5. If you want to grade exams, see [Exams](#exams) section.

You should now be ready to create your notebooks by launching from the project root:

```bash
 jupyter notebook
```

If you wish the notebooks to appear in the generated manual, you have to add them in the `index.rst` file.

## Building the manual

To build the website, go to console and from the root of the directory run:

```bash
python3 build.py
```

Site will be created in `_build/` folder.

**NOTE: to also generate PDF you will need to install Latex environment**


For help: 

```bash
python3 build.py -h
```

For quick build that only produces html:


```bash
python3 build.py -q
```


## Publishing

For publishing, the system uses ReadTheDocs so it is enough to push to master and ReadTheDocs will do the rest (for example, for jupman it is at address [jupman.readthedocs.io](jupman.readthedocs.io) 

**IMPORTANT: ReadTheDocs WILL _NOT_ execute Jupyter notebooks because of [this bug](https://github.com/DavidLeoni/softpython/issues/2)**

## Editing the worksheets

Here we give an overview of how to edit worksheets. More info can be found in [Jupman tests notebook](jupman-tests.ipynb)

### Running jupyter

First of all, run Jupyter from the root of the directory:


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
python3 exam.py -h
```

To see help for a particular subcommand, like i.e. `init`, type the subcommand followed by `-h` :

```bash
python3 exam.py init -h
```

Running commands should be quite self-explanatory.

NOTE: as of today (Sept 2017) software may contain bugs, but at least we check for major misuses 
(like trying to overwrite exeisting exams). 

In the file [create-exam-example.sh](create-exam-example.sh) there is a typical run of the 
script, which creates the example exam for date `2000-12-31`. Notice it might ask
you to delete the existing 2000-12-31 exam, if it does just follow the instructions.
Here is the output:


```bash

~/Da/prj/jupman/prj(master)$ ./create-exam-example.sh

> python3 exam.py init 2000-12-31
  Following material is now ready to edit: 

     Python exercises and tests : private/2000-12-31/exercises
     Python solutions           : private/2000-12-31/solutions
     Exam notebook              : private/2000-12-31private/2000-12-31/exam-2000-12-31.ipynb

  DONE.

> python3 exam.py package 2000-12-31
  Cleaning private/2000-12-31/server/jupman ...
  Copying built website ...
  Copying exercises to private/2000-12-31/server/jupman-2000-12-31/FIRSTNAME-LASTNAME-ID
  Creating student exercises zip:  private/2000-12-31/server/jupman-2000-12-31.zip
  Creating server zip: private/2000-12-31/jupman-2000-12-31-server.zip

  You can now browse the website at:  /home/da/Da/prj/jupman/prj/private/2000-12-31/server/jupman/html/index.html


  DONE.

------- Simulating some shipped exams...
> mkdir -p private/2000-12-31/shipped/john-doe-112233
> cp templates/exam/exercises/ private/2000-12-31/shipped/john-doe-112233
> mkdir -p private/2000-12-31/shipped/jane-doe-445566
> cp templates/exam/exercises/ private/2000-12-31/shipped/jane-doe-445566
------- Done with shipped exams simulation, time to grade ...

> python3 exam.py grade 2000-12-31
  Copying Python files to execute and eventually correct in private/2000-12-31/graded/john-doe-112233/corrected
  Copying original shipped files (don't touch them!) in private/2000-12-31/graded/john-doe-112233/shipped
  Copying Python files to execute and eventually correct in private/2000-12-31/graded/jane-doe-445566/corrected
  Copying original shipped files (don't touch them!) in private/2000-12-31/graded/jane-doe-445566/shipped

  DONE.

> python3 exam.py zip-grades 2000-12-31

  You can now find zips to send to students in private/2000-12-31/graded


  DONE.

> python3 exam.py publish 2000-12-31
  Copying exercises to past-exams/2000-12-31/exercises
  Copying solutions to past-exams/2000-12-31/solutions
  Copying notebook to past-exams/2000-12-31/exam-2000-12-31.ipynb
  Creating zip past-exams/2000-12-31.zip
  
  Exam python files copied.
  
  You can now manually run the following git instructions to publish the exam,
  ReadTheDocs will automatically build the website.
  
    git status  # just to check everything is ok
    git add .
    git commit -m 'published 2000-12-31 exam'
    git push
  

  DONE.


  Finished example exam run !!

```

