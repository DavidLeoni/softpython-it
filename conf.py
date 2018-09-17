#!/usr/bin/env python3# -*- coding: utf-8 -*-

# This is the configuration file of Sphynx, edit it as needed.

import recommonmark
from recommonmark.transform import AutoStructify
from recommonmark.parser import CommonMarkParser
import datetime
import glob
import os
import inspect
import zipfile
import sys
import re
import types
import shutil
from enum import Enum


on_rtd = os.environ.get('READTHEDOCS') == 'True'

###################   TODO EDIT AS NEEDED !!  ####################

course = "SoftPython" 
degree = "DISI @ Università di Trento"
author = 'David Leoni, Alessio Zamboni, Marco Caresia' 
copyright = '# CC-BY 2017 - %s, %s' % (datetime.datetime.now().year, author)

#####    'filename' IS *VERY* IMPORTANT !!!!
#####     IT IS PREPENDED IN MANY GENERATED FILES
#####     AND IT SHOULD ALSO BE THE SAME NAME ON READTHEDOCS 
#####     (like i.e. jupman.readthedocs.org)

filename = 'softpython'   # The filename without the extension

# common files for exercise and exams as paths. Paths are intended relative to the project root. Globs are allowed.
# note 'overlay/_static/css','overlay/_static/js' are automatically injected when you call jupman.init()
exercise_common_files = ['jupman.py', 'img/cc-by.png' ]


# words used in ipynb files - you might want to translate these in your language. Use plural.
IPYNB_SOLUTION = "soluzioni"
IPYNB_EXERCISE = "esercizi"

#NOTE: the following string is not just a translation, it's also a command that removes the cell it is contained in 
#      when building the exercises. If the user inserts extra spaces the phrase will be recognized anyway
WRITE_SOLUTION_HERE = "# scrivi qui"

SOLUTION = "# SOLUZIONE"
MARKDOWN_ANSWER = "**RISPOSTA**:"
#################################################################

#pattern as in ipynb json file - note markdown has no output in ipynb
IPYNB_TITLE_PATTERN = re.compile(r"(\s*#.*)(" + IPYNB_SOLUTION + r")")


zip_ignored = ['__pycache__', '.ipynb_checkpoints', '.pyc']

FORMATS = ["html", "epub", "latex"]
SYSTEMS = {
    "default" : {
        "name" : "Default system",
        "outdir":"_build/",
        "exclude_patterns": ["_build/*", "jm-templates/exam/server/*", "private/*",  '**.ipynb_checkpoints']
    }
}
MANUALS = {
    "student": {
        "name" : course,  # TODO put manual name, like "Scientific Programming"
        "audience" : "studenti",
        "args" : "",
        "output" : "",
        "exclude_patterns" : []
    }
}
manual = 'student'
system = 'default'

project = MANUALS[manual]['name']



JUPMAN_RAISE = "jupman-raise"
JUPMAN_STRIP = "jupman-strip"


#WARNING: this string can end end up in a .ipynb json, so it must be a valid JSON string  !
#         Be careful with the double quotes and \n  !!
RAISE_STRING = "raise Exception('TODO IMPLEMENT ME !')"


jupman_tags = [JUPMAN_RAISE, JUPMAN_STRIP]


def jupman_tag_start(tag):
    return '#' + tag

def jupman_tag_end(tag):
    return '#/' + tag



RAISE_PATTERN = re.compile(jupman_tag_start(JUPMAN_RAISE) + '.*?' + jupman_tag_end(JUPMAN_RAISE), flags=re.DOTALL)

STRIP_PATTERN = re.compile(jupman_tag_start(JUPMAN_STRIP) + '.*?' + jupman_tag_end(JUPMAN_STRIP), flags=re.DOTALL)

def make_write_solution_here_pattern():
    removed_spaces = " ".join(WRITE_SOLUTION_HERE.split()).replace(' ', '\s+')
    return re.compile("(" + removed_spaces + ")(.*)", flags=re.DOTALL )

WRITE_SOLUTION_HERE_PATTERN = make_write_solution_here_pattern()


def fatal(msg, ex=None):
    """ Prints error and exits (halts program execution immediatly)
    """
    if ex == None:
        exMsg = ""
    else:
        exMsg = " \n  " + repr(ex)
    info("\n\n    FATAL ERROR! %s%s\n\n" % (msg,exMsg))
    exit(1)

def error(msg, ex=None):
    """ Prints error and reraises exception (printing is useful as sphinx puts exception errors in a separate log)
    """
    if ex == None:
        exMsg = ""
        the_ex = Exception(msg)
    else:
        exMsg = " \n  " + repr(ex)
        the_ex = ex 
    info("\n\n    FATAL ERROR! %s%s\n\n" % (msg,exMsg))
    raise the_ex
    
def info(msg=""):
    print("  %s" % msg)

def warn(msg):
    print("\n\n   WARNING: %s" % msg)


def debug(msg=""):
    print("  DEBUG=%s" % msg) 
    
# note if I include the project name I can't reference it from index.rst for very silly reasons, see  http://stackoverflow.com/a/23855541

#debug("WRITE_SOLUTION_HERE_PATTERN = %s" % WRITE_SOLUTION_HERE_PATTERN)

def parse_date(ld):
    try:
        return datetime.datetime.strptime( str(ld), "%Y-%m-%d")
    except:
        raise Exception("NEED FORMAT 'yyyy-mm-dd', GOT INSTEAD: '" + str(ld))

    
def parse_date_str(ld):
    """
        NOTE: returns a string 
    """
    return str(parse_date(ld)).replace(' 00:00:00','')
    

def get_exam_student_folder(ld):
    parse_date(ld)
    return filename + '-' + ld + '-FIRSTNAME-LASTNAME-ID'    

    
def super_doc_dir():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


def get_version(release):
    """ Given x.y.z-something, return x.y  """

    sl = release.split(".")
    return sl[0] + '.' + sl[1]

def zip_ignored_file(fname):
    
    for i in zip_ignored:
        if fname.find(i) != -1:
            return True


SUPPORTED_DISTRIB_EXT = ['py', 'ipynb']
    

class FileKinds(Enum):
    SOLUTION = 1
    EXERCISE = 2
    TEST = 3
    OTHER = 4

    @staticmethod
    def sep(ext):
        if ext == 'py':
            return '_'
        else:
            return '-'
    
    @staticmethod
    def is_supported_ext(fname):
        for ext in SUPPORTED_DISTRIB_EXT:
            if fname.endswith('.' + ext):
                return True
        return False
    
    @staticmethod
    def detect(fname):
        l = fname.split(".")
        if len(l) > 0:
            ext = l[-1]
        else:
            ext = ''
        if fname.endswith(FileKinds.sep(ext) + "solution" + '.' + ext):
            return FileKinds.SOLUTION            
        elif fname.endswith(FileKinds.sep(ext) + "exercise" + '.' + ext):
            return FileKinds.EXERCISE 
        elif fname.endswith("_test.py") :
            return FileKinds.TEST        
        else:
            return FileKinds.OTHER

    @staticmethod
    def check_ext(fname):
        if not FileKinds.is_supported_ext(fname):
            raise Exception("%s extension is not supported. Valid values are: %s" % (fname, SUPPORTED_DISTRIB_EXT))
        
    @staticmethod        
    def exercise(radix, ext):      
        FileKinds.check_ext(ext)
        return radix + FileKinds.sep(ext) + 'exercise.' + ext

    @staticmethod
    def exercise_from_solution(fname):
        FileKinds.check_ext(fname)
        ext = fname.split(".")[-1]
               
        return fname.replace(FileKinds.sep(ext) + "solution." + ext, FileKinds.sep(ext) + "exercise." + ext)
        
    @staticmethod
    def solution(radix, ext):
        FileKinds.check_ext(ext)
        return radix + FileKinds.sep(ext) + 'solution.' + ext

    @staticmethod
    def test(radix):
        return radix + '_test.py'

    
    

def check_paths(path, path_check):
    if not isinstance(path, str):
        raise Exception("Path to delete must be a string! Found instead: " + str(type(path)))
    if len(path.strip()) == 0:
        raise Exception("Provided an empty path !")
    if not isinstance(path_check, str):
        raise Exception("Path check to delete must be a string! Found instead: " + str(type(path_check)))
    if len(path_check.strip()) == 0:
        raise Exception("Provided an empty path check!")


def delete_file(path, path_check):
    """ Deletes a file, checking you are deleting what you really want

        path: the path to delete as a string
        path_check: the end of the path to delete, as a string
    """
    check_paths(path, path_check)

    if path.endswith(path_check):
        os.remove(path)
    else:
        fatal("FAILED SAFETY CHECK FOR DELETING DIRECTORY " + path + " ! \n REASON: PATH DOES NOT END IN " + path_check)

def delete_tree(path, path_check):
    """ Deletes a directory, checking you are deleting what you really want

        path: the path to delete as a string
        path_check: the end of the path to delete, as a string
    """
    check_paths(path, path_check)

    if not os.path.isdir(path):
        raise Exception("Provided path is not a directory: %s" % path)

    if path.endswith(path_check):
        shutil.rmtree(path)
    else:
        fatal("FAILED SAFETY CHECK FOR DELETING DIRECTORY " + path + " ! \n REASON: PATH DOES NOT END IN " + path_check)

def delete_file(path, path_check):
    """ Deletes a file, checking you are deleting what you really want

        path: the path to delete as a string
        path_check: the end of the path to delete, as a string
    """
    check_paths(path, path_check)

    if not os.path.isfile(path):
        raise Exception("Provided path is not a file: %s" % path)
    
    
    if path.endswith(path_check):
        os.remove(path)
    else:
        fatal("FAILED SAFETY CHECK FOR DELETING FILE " + path + " ! \n REASON: PATH DOES NOT END IN " + path_check)

    
def validate_tags(text, fname):
    tag_starts = {}
    tag_ends = {}

    for tag in jupman_tags:
        tag_starts[tag] = text.count(jupman_tag_start(tag))                                           
        tag_ends[tag] = text.count(jupman_tag_end(tag))

    for tag in tag_starts:
        if tag not in tag_ends or tag_starts[tag] != tag_ends[tag] :
            raise Exception("Missing final tag %s in %s" % (jupman_tag_end(tag), fname) )

    for tag in tag_ends:
        if tag not in tag_starts or tag_starts[tag] != tag_ends[tag] :
            raise Exception("Missing initial tag %s in %s" % (jupman_tag_start(tag), fname) )
    
    write_solution_here_count = len(WRITE_SOLUTION_HERE_PATTERN.findall(text))
    
    return sum(tag_starts.values()) + write_solution_here_count > 0



def copy_sols(source_filename, source_abs_filename, dest_filename):
    if FileKinds.is_supported_ext(source_filename):
        info("Stripping jupman tags from %s " % source_filename)
        with open(source_abs_filename) as sol_source_f:
            text = sol_source_f.read()
            stripped_text = text
            for tag in jupman_tags:

                stripped_text = stripped_text \
                                .replace(jupman_tag_start(tag), '') \
                                .replace(jupman_tag_end(tag), '')

            with open(dest_filename, 'w') as solution_dest_f:
                solution_dest_f.write(stripped_text)

    else: # solution format not supported                           
        info("Writing " + source_filename)
        shutil.copy(source_abs_filename, dest_filename)
          
def solution_to_exercise_text(solution_text):
                        
    formatted_text = re.sub(RAISE_PATTERN, RAISE_STRING, solution_text)                    
    formatted_text = re.sub(STRIP_PATTERN, '', formatted_text)
    formatted_text = re.sub(WRITE_SOLUTION_HERE_PATTERN, r'\1\n\n', formatted_text)
    
    return formatted_text            

def generate_exercise(source_filename, source_abs_filename, dirpath, structure):
    exercise_fname = FileKinds.exercise_from_solution(source_filename)
    exercise_abs_filename = dirpath + '/' + exercise_fname
    exercise_dest_filename = structure + '/' + exercise_fname


    if FileKinds.is_supported_ext(source_filename):

        with open(source_abs_filename) as sol_source_f:
            solution_text = sol_source_f.read()                                

            found_tag = validate_tags(solution_text, source_abs_filename)                                                                                

            if found_tag:

                if os.path.isfile(exercise_abs_filename) :
                    raise Exception("Found jupman tags in solution file but an exercise file exists already !\n  solution: %s\n  exercise: %s" % (source_abs_filename, exercise_abs_filename))

                info('Found jupman tags in solution file, going to derive from solution exercise file %s' % exercise_fname )                                    

                                                        
                with open(exercise_dest_filename, 'w') as exercise_dest_f:
                    
                    
                    if source_abs_filename.endswith('.ipynb'):
                        
                        import nbformat
                        # note: for weird reasons nbformat does not like the sol_source_f 
                        nb_ex = nbformat.read(source_abs_filename, nbformat.NO_CONVERT)
                                                                        

                        # look for title
                        found_title = False                        
                        for cell in nb_ex.cells:
                            if cell.cell_type == "markdown":
                                if IPYNB_TITLE_PATTERN.search(cell.source):
                                    found_title = True
                                    cell.source = re.sub(IPYNB_TITLE_PATTERN, 
                                                   r"\1" + IPYNB_EXERCISE, cell.source) 
                                    break
                        
                        if not found_title:
                            error("Couldn't find title in file: \n   %s\nThere should be a markdown cell beginning with text (note string '%s' is mandatory)\n# bla bla %s" % (source_abs_filename, IPYNB_SOLUTION, IPYNB_SOLUTION))
    
    
                        # look for tags
                        for cell in nb_ex.cells:
                            if cell.cell_type == "code":
                                if cell.source.strip().startswith(SOLUTION):
                                    cell.source = " " 
                                else:
                                    cell.source = solution_to_exercise_text(cell.source)
                            if cell.cell_type == "markdown":
                                if cell.source.strip().startswith(MARKDOWN_ANSWER):                                    
                                    cell.source = " "  # space, otherwise it shows 'Type markdown or latex'
                                
                        nbformat.write(nb_ex, exercise_dest_f)
                    
                    else:
                        
                        exercise_text = solution_to_exercise_text(solution_text)
                        #debug("FORMATTED TEXT=\n%s" % exercise_text)
                        exercise_dest_f.write(exercise_text)                    
                                                                
            else:
                if not os.path.isfile(exercise_abs_filename) :
                    error("There is no exercise file and couldn't find any jupman tag in solution file for generating exercise !"
                          +"\n  solution: %s\n  exercise: %s" % (source_abs_filename, exercise_abs_filename))
                    
def copy_code(source_dir, dest_dir, copy_test=True, copy_solutions=False):
    
    
    info("  Copying exercises %s \n      from  %s \n      to    %s" % ('and solutions' if copy_solutions else '', source_dir, dest_dir))
    # creating folders
    for dirpath, dirnames, filenames in os.walk(source_dir):
        structure = dest_dir + dirpath[len(source_dir):]
        #print("structure = " + structure)
        #print("  FOUND DIR " + dirpath) 
        
        if not zip_ignored_file(structure):
            if not os.path.isdir(structure) :
                print("Creating dir %s" % structure)
                os.makedirs(structure)

            for source_filename in filenames:
                                
                if not zip_ignored_file(source_filename):
                    
                    source_abs_filename = dirpath + '/' + source_filename
                    dest_filename = structure + '/' + source_filename                    

                    #print("source_abs_filename = " + source_abs_filename)
                    #print("dest_filename = " + dest_filename)

                    fileKind = FileKinds.detect(source_filename)
                    
                    if fileKind == FileKinds.SOLUTION:                  
                        
                        if copy_solutions:                                           
                            copy_sols(source_filename, source_abs_filename, dest_filename)
                        
                        if FileKinds.is_supported_ext(source_filename):
                            generate_exercise(source_filename, source_abs_filename, dirpath, structure)    
                                        
                            
                    elif fileKind == FileKinds.TEST:
                        with open(source_abs_filename, encoding='utf-8') as source_f:
                            data=source_f.read().replace('_solution ', ' ')
                            info('Writing patched test %s' % source_filename) 
                            with open(dest_filename, 'w', encoding='utf-8') as dest_f:
                                writer = dest_f.write(data)                         
                    else:  # EXERCISE and OTHER
                        print("  Writing " + source_filename)
                        shutil.copy(source_abs_filename, dest_filename)


def zip_paths(rel_paths, zip_path, patterns=[]):
    """ zips provided rel_folder to file zip_path (WITHOUT .zip) !
        rel_folder MUST be relative to project root
        
        This function was needed as default python zipping machinery created weird zips 
        people couldn't open in Windows
        
        patterns can be:
         - a list of tuples source regexes to dest 
         - a function that takes a string and returns a string
        
    """
    
    
    if zip_path.endswith('.zip'):
        raise Exception("zip_path must not end with .zip ! Found instead: " + zip_path)

    for rel_path in rel_paths:
        abs_path = super_doc_dir() + '/' + rel_path

        if not(os.path.exists(abs_path)):
            raise Exception("Expected an existing file or folder relative to project root ! Found instead: " + rel_path)

      
    def write_file(fname):
        
        
        if not zip_ignored_file(fname) :
            #info('Zipping: %s' % fname)            
            
            
            if isinstance(patterns, (list,)):
                if len(patterns) > 0:
                    to_name = fname
                    for pattern, to in patterns:    
                        try:
                            to_name = re.sub(pattern, to, to_name)
                        except Exception as ex:
                            error("Couldn't substitute pattern \n  %s\nto\n  %s\nin string\n  %s\n\n" % (pattern, to, to_name) , ex)
                else:
                    to_name = '/' + fname
                    
            elif isinstance(patterns, types.FunctionType):
                to_name = patterns(fname)
            else:
                error('Unknown patterns type %s' % type(patterns))

            #info('to_name = %s' % to_name)                    
                
            archive.write(fname, to_name, zipfile.ZIP_DEFLATED)

    archive = zipfile.ZipFile(zip_path + '.zip', "w")
    
    for rel_path in rel_paths:

        if os.path.isdir(rel_path):            
            for dirname, dirs, files in os.walk(rel_path):
                #info("dirname=" + dirname)
                dirNamePrefix = dirname + "/*"
                #info("dirNamePrefix=" + dirNamePrefix)
                filenames = glob.glob(dirNamePrefix)
                #info("filenames=" + str(filenames))
                for fname in filenames:
                    if os.path.isfile(fname):
                        write_file(fname)
        elif os.path.isfile(rel_path):
            info('Writing %s' % rel_path)
            write_file(rel_path)
        else:
            raise Exception("Don't know how to handle " + rel_path)
    archive.close()
        
    info("Wrote " + zip_path)
            
def zip_folders(folder, prefix='', suffix=''):
    global exercise_common_files
    source_folders =  glob.glob(folder + "/*/")
    
    if folder.startswith('..'):
        fatal("BAD FOLDER TO ZIP ! IT STARTS WITH '..'")
    if len(folder.strip()) == 0:
        fatal("BAD FOLDER TO ZIP ! BLANK STRING")

    build_jupman = '_build/jupman/'
    build_folder = build_jupman + folder
    if os.path.exists(build_folder):
        info('Cleaning %s' % build_folder)
        delete_tree(build_folder, '_build/jupman/' + folder)
    
    copy_code(folder, build_folder, copy_test=True, copy_solutions=True)
    
    build_folders =   glob.glob(build_folder + "/*/")
    
    if len(source_folders) > 0:
        outdir = 'overlay/_static/'
        info("Found stuff in %s , zipping them to %s" % (folder, outdir))
        for d in build_folders:
            dir_name= d[len(build_folder + '/'):].strip('/')
            #info("dir_name = " + dir_name)
            zip_name = prefix + dir_name + suffix
            zip_path = outdir + zip_name
            zip_paths(exercise_common_files + [d], zip_path, patterns= [("^(%s)" % build_jupman,"")])
        info("Done zipping " + folder ) 


# Use sphinx-quickstart to create your own conf.py file!
# After that, you have to edit a few things.  See below.

# Select nbsphinx and, if needed, add a math extension (mathjax or pngmath):
extensions = [
    'nbsphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.ifconfig'
    #, 'rst2pdf.pdfbuilder'
]

# Exclude build directory and Jupyter backup files:
exclude_patterns = ['_build', '**.ipynb_checkpoints', '/README.md', '/readme.md']

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

master_doc = 'index'



linkcheck_ignore = [r'http://localhost:\d+/']

# -- Get version information from Git -------------------------------------

try:
    from subprocess import check_output
    release = check_output(['git', 'describe', '--tags', '--always'])
    release = release.decode().strip()
    if not '.' in release:
        release = '0.1.0'
        info("Couldn't find git tag, defaulting to: " + release)
    else:    
        info("Detected release from git: " + str(release))
except Exception:
    release = '0.1.0'
    info("Couldn't find git version, defaulting to: " + release)

version  = get_version(release)
info("Setting version to %s" % version)


# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None


# -- Options for HTML output ----------------------------------------------

html_title = project 


# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

if not on_rtd:


    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]    

    
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# DAVID: THE html_static_path SETTING WITH '_static' IS CRAP, IT JUST MARGES INSIDE _STATIC ALL THE FILES IGNORING THE SUBDIRECTORIES ! THE 'html_extra_path' IS MUCH BETTER.

html_static_path = [] 
html_extra_path = ['overlay'] 


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = project + 'doc'


#DAVID: NOTE: THESE ARE *ONLY* FOR HTML TEMPLATES, WHICH IS DIFFERENT FROM jm-templates
# see https://github.com/DavidLeoni/jupman/issues/10
templates_path = ['_templates']


html_additional_pages = {
    'google3dea3b29336ca0e5.html': 'google3dea3b29336ca0e5.html',
}



# -- Options for LaTeX output ---------------------------------------------# -- Options for LaTeX output ---------------------------------------------

#latex_elements = {
#    'papersize': 'a4paper',
#    'preamble': r"""
#\usepackage[sc,osf]{mathpazo}
#\linespread{1.05}  % see http://www.tug.dk/FontCatalogue/urwpalladio/
#\renewcommand{\sfdefault}{pplj}  % Palatino instead of sans serif
#\IfFileExists{zlmtt.sty}{
#    \usepackage[light,scaled=1.05]{zlmtt}  % light typewriter font from lmodern
#}{
#    \renewcommand{\ttdefault}{lmtt}  % typewriter font from lmodern
#}
#""",
#}


latex_show_urls = 'footnote'


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, filename + '.tex', project,
     author, 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, filename, project,
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, filename, project,
     author, project, '',
     'Miscellaneous'),
]



# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_basename = filename
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
   ('index', filename, project, author.replace(",","\\"))
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

        app.add_config_value('recommonmark_config', {
            'auto_toc_tree_section': 'Contents',
            'enable_eval_rst':True
        }, True)
        app.add_transform(AutoStructify)
        app.add_javascript('js/jupman.js')
        app.add_stylesheet('css/jupman.css')
        zip_folders('exercises', suffix='-exercises')
        zip_folders('exams', prefix=filename + '-', suffix='-exam')
        zip_folders('challenges', prefix=filename + '-', suffix='-challenge')
        zip_paths(['jm-templates/project-NAME-SURNAME-ID'], 
                    'overlay/_static/project-template',
                    patterns=[(r"^(jm-templates)/project-(.*)", "/\\2")])
        
        # check home.ipynb 
        from pathlib import Path
        ref = "https://github.com/DavidLeoni/jupman/issues/11"
        if not Path('home.ipynb').exists():  # the file pointed to
            raise Exception("MISSING home.ipynb ! For more info about Jupman layout, see %s" % ref)         


exclude_patterns.extend(MANUALS[manual]['exclude_patterns'])
exclude_patterns.extend(SYSTEMS[system]['exclude_patterns'])



source_parsers = {
    '.md': CommonMarkParser,
}

source_suffix = ['.rst', '.md']


