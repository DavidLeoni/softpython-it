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


#import exam
import shutil
