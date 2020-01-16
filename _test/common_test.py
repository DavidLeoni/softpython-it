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

def clean():
    if os.path.isdir('_build/test'):
        jmt.delete_tree('_build/test', '_build/test')
    if os.path.isdir('_build/test-generated'):
        jmt.delete_tree('_build/test-generated', '_build/test-generated')

def prep_jm(jm : Jupman):
    jm.build = '_build/test'
    jm.generated = '_build/test-generated'

def make_jm() -> Jupman:
    jm = Jupman()
    prep_jm(jm)
    return jm

@pytest.fixture
def tconf():
    clean()

    import conf

    prep_jm(conf.jm)
    return conf

