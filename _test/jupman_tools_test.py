from hypothesis import given
from hypothesis.strategies import text
import sys
sys.path.append('../')
sys.path.append('.')  # good lord, without this debugging in VSCode doesn't work
import jupman_tools as jmt
from jupman_tools import ignore_spaces
from jupman_tools import Jupman
import pytest 
import re
from sphinx.application import Sphinx
import os
import nbformat

from common_test import * 
import datetime

def test_detect_release():
    res =  jmt.detect_release()
    assert res == 'dev' or len(res.split('.')) >= 2

def test_get_version():
    res =  jmt.get_version(jmt.detect_release())
    assert res == 'dev' or len(res.split('.')) == 2


def test_parse_date():
    assert jmt.parse_date('2000-12-31') == datetime.datetime(2000,12,31)

    with pytest.raises(Exception):
        jmt.parse_date('2000-31-12')

def test_parse_date_str():
    assert jmt.parse_date_str('2000-12-31') == '2000-12-31'
    
    with pytest.raises(Exception):
        jmt.parse_date_str('2000-31-12')


def test_jupman_constructor():
    jm = Jupman()
    # only testing the vital attrs
    assert jm.filename == 'jupman'
    #NOTE: putting '/' at the end causes exclude_patterns to not work !
    assert jm.build == '_build' 
    assert jm.generated == '_static/generated'

class MockSphinx:
    def add_config_value(self, a,b,c):
        pass
    def add_transform(self, a):
        pass
    def add_javascript(self, a):
        pass
    def add_stylesheet(self, a):
        pass


def test_uproot():
    assert jmt.uproot('jupman.py') == ''
    assert jmt.uproot('_test/') == '../'
    assert jmt.uproot('_test/test-chapter/data/pop.csv') == '../../../'
    # this is supposed to be a directory
    assert jmt.uproot('_test/non-existing') == '../../'
    assert jmt.uproot('_static/img') == '../../'
    assert jmt.uproot('_static/img/cc-by.png') == '../../'
    assert jmt.uproot('_static/img/non-existing') == '../../../'

def test_replace_sysrel():

    assert jmt.replace_py_rel("""import sys
sys.do_something()""", 'python-intro').strip() ==  """import sys
sys.do_something()"""


    assert jmt.replace_py_rel("""
import sys
sys.path.append('../')
import jupman

    """, 'python-intro').strip() ==  'import jupman'


    assert jmt.replace_py_rel("""
import sys
sys.path.append('../')
import jupman
sys.do_something()
    """, 'python-intro').strip() ==  """import sys
import jupman
sys.do_something()"""


def test_is_zip_ignored():
    jm = make_jm()
    assert jm.is_zip_ignored('.ipynb_checkpoints')
    assert jm.is_zip_ignored('prova/.ipynb_checkpoints')
    assert jm.is_zip_ignored('prova/__pycache__')
    assert not jm.is_zip_ignored('good')
    assert not jm.is_zip_ignored('very/good')
    


def test_copy_chapter():
    clean()
    
    jm = make_jm()
    os.makedirs(jm.build)
    dest_dir = os.path.join(jm.build, 'test-chapter')
    jm.copy_code('_test/test-chapter',
                 dest_dir,
                 copy_solutions=True)

    assert os.path.isdir(dest_dir)

    replacements_fn = os.path.join(dest_dir, 'replacements.ipynb')
    assert os.path.isfile(replacements_fn)

    nb_node = nbformat.read(replacements_fn, nbformat.NO_CONVERT)

    # markdown                             
    assert '[A markdown relative link](index.ipynb)' in nb_node.cells[1].source
    assert '![Another markdown link](_static/img/cc-by.png)' in nb_node.cells[2].source
    assert '[A local markdown link](data/pop.csv)' in nb_node.cells[3].source

    assert '<a href="index.ipynb" target="_blank">An html in markdown relative link</a>' in nb_node.cells[4].source

    assert '<img src="_static/img/cc-by.png">' in nb_node.cells[5].source
    assert '<a href="data/pop.csv">a html in markdown local link</a>' in nb_node.cells[6].source
    
    assert '<a href="index.ipynb">An html relative link</a>' in nb_node.cells[7].source

    assert '<img src="_static/img/cc-by.png">' in nb_node.cells[8].source

    assert '<a href="data/pop.csv">an html local link</a>' in nb_node.cells[9].source

    assert '# Python\nimport jupman' in nb_node.cells[10].source
    assert '#jupman-raise' in nb_node.cells[10].source

    py_fn = os.path.join(dest_dir, 'file.py')
    assert os.path.isfile(py_fn)

    with open(py_fn, encoding='utf-8') as py_f:
        py_code = py_f.read()
        assert '# Python\nimport jupman' in py_code
        assert '#jupman-raise' in py_code

    test_fn = os.path.join(dest_dir, 'some_test.py')
    assert os.path.isfile(test_fn)

    with open(test_fn, encoding='utf-8') as test_f:
        test_code = test_f.read()
        assert 'some_sol' not in test_code
        assert '# Python\nimport some\nimport jupman' in test_code
        assert '#jupman-raise' in test_code

    sol_fn = os.path.join(dest_dir, 'some_sol.py')
    assert os.path.isfile(sol_fn)

    with open(sol_fn, encoding='utf-8') as sol_f:
        sol_code = sol_f.read()
        assert '# Python\nimport jupman' in sol_code
        assert '#jupman-raise' not in sol_code
        assert "# work!\n\nprint('hi')" in sol_code

    ex_fn = os.path.join(dest_dir, 'some.py')
    assert os.path.isfile(ex_fn)

    with open(ex_fn, encoding='utf-8') as ex_f:
        ex_code = ex_f.read()
        assert '# Python\nimport jupman' in ex_code
        assert '#jupman-raise' not in ex_code
        assert '# work!\nraise' in ex_code

    nb_ex_fn = os.path.join(dest_dir, 'nb.ipynb')
    assert os.path.isfile(nb_ex_fn)

    nb_ex = nbformat.read(nb_ex_fn, nbformat.NO_CONVERT)
    assert "# Notebook EXERCISES" in nb_ex.cells[0].source
    assert "#before\nraise" in nb_ex.cells[1].source
    assert nb_ex.cells[2].source == ""   # SOLUTION strips everything
    assert nb_ex.cells[3].source.strip() == "# 3\n# write here"    # write here strips afterwards
    #4 question
    #5 answer: must begin with answer and strips everything after
    assert nb_ex.cells[5].source == '**ANSWER**:\n'

def test_setup(tconf):
    
    
    mockapp = MockSphinx()
    
    tconf.setup(mockapp)
    assert os.path.isfile(os.path.join(tconf.jm.generated, 'jupyter-intro.zip'))
    assert os.path.isfile(os.path.join(tconf.jm.generated, 'python-intro.zip'))
    assert os.path.isfile(os.path.join(tconf.jm.generated, 'tools-intro.zip'))

def test_ignore_spaces():
    
    with pytest.raises(ValueError):
        ignore_spaces("")

    p = re.compile(ignore_spaces(" a    b"))
    assert p.match(" a b")
    assert p.match(" a  b")
    assert p.match(" a  b ")
    assert p.match(" a  b  ")
    assert p.match(" a  b\n")
    assert p.match("   a  b\n")
    assert not p.match(" ab")
    assert not p.match("c b")
    


def test_validate_code_tags():
    jm = make_jm()
    assert jm.validate_code_tags('# SOLUTION\nbla', 'some_file') == 1
    assert jm.validate_code_tags('  # SOLUTION\nbla', 'some_file') == 1
    assert jm.validate_code_tags('something before  # SOLUTION\nbla', 'some_file') == 0
    # pairs count as one
    assert jm.validate_code_tags('#jupman-raise\nsomething#/jupman-raise', 'some_file') == 1
    assert jm.validate_code_tags("""
    hello
    #jupman-raise
    something
    #/jupman-raise
    #jupman-raise
    bla
    #/jupman-raise""", 'some_file') == 2

def test_validate_markdown_tags():
    jm = make_jm()

    assert jm.validate_markdown_tags('**ANSWER**: hello', 'some_file') == 1
    assert jm.validate_markdown_tags('  **ANSWER**: hello', 'some_file') == 1
    assert jm.validate_markdown_tags('bla  **ANSWER**: hello', 'some_file') == 0