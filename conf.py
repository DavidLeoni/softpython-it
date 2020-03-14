#!/usr/bin/env python3# -*- coding: utf-8 -*-

# This is the configuration file of Sphynx, edit it as needed.

import recommonmark
from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser
import datetime
import glob
import re
import os
import sys
sys.path.append('.') # for rtd 
import jupman_tools as jmt

on_rtd = os.environ.get('READTHEDOCS') == 'True'

###################   TODO EDIT AS NEEDED !!  ####################

jm = jmt.Jupman()

jm.subtitle = "Guida introduttiva alla pulizia e analisi dati con Python 3"
jm.course = "SoftPython" 
jm.degree = "DISI @ Università di Trento"
author = 'David Leoni, Alessio Zamboni, Marco Caresia' 
copyright = '# CC-BY 2017 - %s, %s' % (datetime.datetime.now().year, author)

#####    'jm_filename' IS *VERY* IMPORTANT !!!!
#####     IT IS PREPENDED IN MANY GENERATED FILES
#####     AND IT SHOULD ALSO BE THE SAME NAME ON READTHEDOCS 
#####     (like i.e. jupman.readthedocs.org)

jm.filename = 'softpython'   # The filename without the extension

# common files for exercise and exams as paths. Paths are intended relative to the project root. Globs like /**/* are allowed.

jm.chapter_files = ['jupman.py', 'img/cc-by.png', 
                         
                    '_static/js/jupman.js',  # these files are injected when you call jupman.init()
                    '_static/css/jupman.css', 
                    '_static/js/toc.js']

jm.chapter_patterns =  ['*/']
jm.chapter_exclude_patterns =  ['[^_]*/','^exams/', '^project/', '^challenges/']

# words used in ipynb files - you might want to translate these in your language. Use plural.
jm.ipynb_solutions = "SOLUZIONI"
jm.ipynb_exercises = "ESERCIZI"

#NOTE: the following string is not just a translation, it's also a command that   when building the exercises
#      removes the content after it in the Python cell it is contained in
#      If the user inserts extra spaces the phrase will be recognized anyway
jm.write_solution_here = jmt.ignore_spaces("# scrivi qui", must_begin=False)

#NOTE: the following string is not just a translation, it's also a command that  when building the exercises  completely removes the content of the python cell it is contained in (solution comment included). If the user inserts extra spaces the phrase will be recognized anyway

jm.solution = jmt.ignore_spaces("# SOLUZIONE")

#NOTE: the following string is not just a translation, it's also a command that 
#   when building the exercises removes the content after it in the markdown cell
#   it is contained in

jm.markdown_answer = jmt.ignore_spaces('**RISPOSTA**:')
#################################################################

jm.zip_ignored = ['__pycache__', '**.ipynb_checkpoints', '.pyc', '.cache', '.pytest_cache', '.vscode']

jm.formats = ["html", "epub", "latex"]


jm.build = "_build"


jm.manuals = {
    "student": {
        "name" : "SoftPython",  # TODO put manual name, like "Scientific Programming"
        "audience" : "studenti",
        "args" : "",
        "output" : ""
    }
}
jm.manual = 'student'


project = jm.manuals[jm.manual]['name']



jm.raise_exc = "jupman-raise"
jm.strip = "jupman-strip"


#WARNING: this string can end end up in a .ipynb json, so it must be a valid JSON string  !
#         Be careful with the double quotes and \n  !!
jm.raise_exc_code = "raise Exception('TODO IMPLEMENT ME !')"


jm.tags = [jm.raise_exc, jm.strip]
    

# Use sphinx-quickstart to create your own conf.py file!
# After that, you have to edit a few things.  See below.

# Select nbsphinx and, if needed, add a math extension (mathjax or pngmath):
extensions = [
    'nbsphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.ifconfig',
    'recommonmark'
    #, 'rst2pdf.pdfbuilder'
]

# Exclude build directory and Jupyter backup files:
exclude_patterns = [jm.build,
                    jm.generated, 
                    "_templates/exam-server",
                     "_private",
                     "_test",                     
                     'README.md',
                     'readme.md',
                     'gui/esempi-bqplot']  # was giving weird notebook version 2 errors on RTD

exclude_patterns.extend(jm.zip_ignored)

# Default language for syntax highlighting in reST and Markdown cells
highlight_language = 'none'

# Don't add .txt suffix to source files (available for Sphinx >= 1.5):
html_sourcelink_suffix = ''

# Execute notebooks before conversion: 'always', 'never', 'auto' (default)
nbsphinx_execute = 'never'   
    
# Use this kernel instead of the one stored in the notebook metadata:
nbsphinx_kernel_name = 'python3'

# List of arguments to be passed to the kernel that executes the notebooks:
#nbsphinx_execute_arguments = ['--InlineBackend.figure_formats={"png", "pdf"}']

# If True, the build process is continued even if an exception occurs:
#nbsphinx_allow_errors = True

# Controls when a cell will time out (defaults to 30; use -1 for no timeout):
#nbsphinx_timeout = 60

# Default Pygments lexer for syntax highlighting in code cells:
nbsphinx_codecell_lexer = 'ipython3'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Width of input/output prompts used in CSS:
#nbsphinx_prompt_width = '8ex'

# If window is narrower than this, input/output prompts are on separate lines:
#nbsphinx_responsive_width = '700px'

# -- The settings below this line are not specific to nbsphinx ------------

master_doc = 'toc-page'



linkcheck_ignore = [r'http://localhost:\d+/']

# -- Get version information from Git -------------------------------------

release = jmt.detect_release()
version  = jmt.get_version(release)


# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None


# -- Options for HTML output ----------------------------------------------

html_title = project # + ' version ' + release
# canonical url for documentation
# since sphinx 1.8
html_baseurl = 'https://softpython.readthedocs.io'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    # fix for https://github.com/DavidLeoni/jupman/issues/38
    'collapse_navigation': False,
}

# NOTE: in order to have complete collapsible menu, 
#       IT IS *FUNDAMENTAL* FOR html_theme to be defined
#       see https://github.com/DavidLeoni/jupman/issues/38
html_theme = 'sphinx_rtd_theme'    
if not on_rtd:
    import sphinx_rtd_theme
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]  

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

html_static_path = ['_static/'] 
#html_extra_path = [] 


html_js_files = [
    'js/jupman.js',  # shared among jupyter and ReadTheDocs
]

html_css_files = [
    'css/jupman.css',      # shared among jupyter and ReadTheDocs
    'css/jupman-rtd.css',  # only for ReadTheDocs
]


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = project + 'doc'


#JUPMAN: NOTE: THESE ARE *ONLY* FOR HTML TEMPLATES, WHICH IS DIFFERENT FROM jm-templates
# see https://github.com/DavidLeoni/jupman/issues/10
templates_path = ['_templates']

#JUPMAN: you can use html_additional_pages for directly copying html files from _templates to the project root

# For example, it could be useful for copying Google Search Console files. 
# Just put the google file in the _templates directory, 
# and add the following code. Note that afterwards you would still need to 
# go to readthethedocs and in Redirects section add an absolute redirect 
# like /google3dea3b29336ca0e5.html -> /it/latest/google3dea3b29336ca0e5.html 

# NOTE: don't put the extension on the left  !

html_additional_pages = {
    'google3dea3b29336ca0e5': 'google3dea3b29336ca0e5.html',
}



latex_engine='xelatex'

# allow utf8 characters
latex_elements = {
    'preamble' : r'''
\usepackage{newunicodechar}
\usepackage{amsmath}
\usepackage{wasysym}
\usepackage{graphicx}

\makeatletter
% Actually APLlog is a a thin star against white circle, could't find anything better
\newunicodechar{✪}{\APLlog}    
\newunicodechar{✓}{\checkmark}    

    ''',
    'maketitle': jm.latex_maketitle(html_baseurl),
}



latex_show_urls = 'footnote'


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, jm.filename + '.tex', project,
     author, 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, jm.filename, project,
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, jm.filename, project,
     author, project, '',
     'Miscellaneous'),
]



# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_basename = jm.filename
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']



# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}


# -- Options for PDF output --------------------------------------------------
# Grouping the document tree into PDF files. List of tuples
# (source start file, target name, title, author, options).
#
# If there is more than one author, separate them with \\.
# For example: r'Guido van Rossum\\Fred L. Drake, Jr., editor'
#
# The options element is a dictionary that lets you override
# this config per-document.
# For example,
# ('index', u'MyProject', u'My Project', u'Author Name',
#  dict(pdf_compressed = True))
# would mean that specific document would be compressed
# regardless of the global pdf_compressed setting.


pdf_documents = [
   ('index', jm.filename, project, author.replace(",","\\"))
]
# A comma-separated list of custom stylesheets. Example:
pdf_stylesheets = ['sphinx','kerning','a4']
# A list of folders to search for stylesheets. Example:
pdf_style_path = ['.', '_styles']
# Create a compressed PDF
# Use True/False or 1/0
# Example: compressed=True
#pdf_compressed = False
# A colon-separated list of folders to search for fonts. Example:
# pdf_font_path = ['/usr/share/fonts', '/usr/share/texmf-dist/fonts/']
# Language to be used for hyphenation support
#pdf_language = "en_US"
# Mode for literal blocks wider than the frame. Can be
# overflow, shrink or truncate
#pdf_fit_mode = "shrink"
# Section level that forces a break page.
# For example: 1 means top-level sections start in a new page
# 0 means disabled
#pdf_break_level = 0
# When a section starts in a new page, force it to be 'even', 'odd',
# or just use 'any'
#pdf_breakside = 'any'
# Insert footnotes where they are defined instead of
# at the end.
#pdf_inline_footnotes = True
# verbosity level. 0 1 or 2
#pdf_verbosity = 0
# If false, no index is generated.
#pdf_use_index = True
# If false, no modindex is generated.
#pdf_use_modindex = True
# If false, no coverpage is generated.
#pdf_use_coverpage = True
# Name of the cover page template to use
#pdf_cover_template = 'sphinxcover.tmpl'
# Documents to append as an appendix to all manuals.
#pdf_appendices = []
# Enable experimental feature to split table cells. Use it
# if you get "DelayedTable too big" errors
#pdf_splittables = False
# Set the default DPI for images
#pdf_default_dpi = 72
# Enable rst2pdf extension modules (default is only vectorpdf)
# you need vectorpdf if you want to use sphinx's graphviz support
#pdf_extensions = ['vectorpdf']
# Page template name for "regular" pages
#pdf_page_template = 'cutePage'
# Show Table Of Contents at the beginning?
#pdf_use_toc = True
# How many levels deep should the table of contents be
pdf_toc_depth = 9999
# Add section number to section references
pdf_use_numbered_links = False
# Background images fitting mode
pdf_fit_background_mode = 'scale'

def setup(app):    

        app.add_config_value(   'recommonmark_config', {
                                    'auto_toc_tree_section': 'Contents',
                                    'enable_eval_rst':True
                                }, True)
        app.add_transform(AutoStructify)
        for folder in jm.get_exercise_folders():
            jm.zip_folder(folder)
        jm.zip_folders('exams/*/solutions', 
                        lambda x:  '%s-%s-exam' % (jm.filename, x.split('/')[-2]))
        jm.zip_folders('challenges/*/', renamer = lambda x: '%s-challenge' % x.split('/')[1])
        jm.zip_paths(['project'], '_static/generated/project-template')

        def sub(x):
            if x == 'requirements.txt':
                return 'NAME-SURNAME-ID/requirements.txt'
            elif x.startswith('project/'):
                return 'NAME-SURNAME-ID/%s' % x[len('project/'):]
            else:
                return x

        jm.zip_paths(['project', 'requirements.txt'], 
                     '_static/generated/project-template',
                     patterns = sub)

        


source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
    
}
