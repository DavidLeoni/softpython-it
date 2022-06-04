import logging
# this way we don't get warning of other libs in pytest, see https://stackoverflow.com/a/63946841
logging.captureWarnings(True)  

import zipfile
from pylatexenc.latexencode import unicode_to_latex
from enum import Enum
import re
import os
import shutil
import inspect
import types
import glob
import stat
import datetime 
from nbconvert.preprocessors import Preprocessor  


class JupmanFormatter(logging.Formatter):

    def format(self, record):
        if record.levelno == logging.INFO:
            self._style._fmt = "  %(message)s"
        else:
            self._style._fmt = "\n\n  %(levelname)s: %(message)s"
        return super().format(record)


logger = logging.getLogger('jupman')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(JupmanFormatter())
logger.addHandler(console_handler)





def fatal(msg, ex=None):
    """ Prints error and exits (halts program execution immediatly)
    """
    if ex == None:
        exMsg = ""
    else:
        exMsg = " \n  %s" % repr(ex)
    logger.critical("\n\n    FATAL ERROR! %s%s\n\n" % (msg,exMsg))
    exit(1)

def error(msg, ex=None):
    """ Prints error and reraises exception (printing is useful as sphinx puts exception errors in a separate log)
    """
    if ex == None:
        exMsg = ""
        the_ex = Exception(msg)
    else:
        exMsg = " \n  %s" % repr(ex)
        the_ex = ex 
    logger.error("\n\n    FATAL ERROR! %s%s\n\n" % (msg,exMsg))
    raise the_ex
    
def info(msg=""):
    logger.info("  %s" % msg)    

def warn(msg, ex=None):
    logger.warning("\n\n   WARNING: %s" % msg)    

def debug(msg=""):
    logger.debug("  DEBUG=%s" % msg)        
    
def parse_date(ld):
    try:
        return datetime.datetime.strptime( str(ld), "%Y-%m-%d")
    except Exception as e:
        raise Exception("NEED FORMAT 'yyyy-mm-dd', GOT INSTEAD: '%s'" % ld, e)

    
def parse_date_str(ld) -> str:
    """
        NOTE: returns a string 
    """
    return str(parse_date(ld)).replace(' 00:00:00','')
    

    
def super_doc_dir():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def detect_release():
    """ Return a release string, calling git to find tags.
        If unsuccessful return 'dev'.
    """
    try:
        from subprocess import check_output
        release = check_output(['git', 'describe', '--tags', '--always'])
        release = release.decode().strip()        
        if not '.' in release:
            raise Exception                    
    except Exception:
        release = 'dev'

    return release

def get_version(release):
    """ Given x.y.z-something, return x.y
        On ill-formed return verbatim.
    """
    if '.' in release:
        sl = release.split(".")
        return  '%s.%s' % (sl[0], sl[1])
    else:
        return release


def expand_JM(source, target, exam_date, conf):
    d = parse_date(exam_date)
    sourcef = open(source, "r")
    s = sourcef.read()
    s = s.replace('_JM_{exam.date}', exam_date )
    s = s.replace('_JM_{exam.date_human}', d.strftime('%a %d, %b %Y') )
    for k in conf.__dict__:
        s = s.replace('_JM_{conf.' + k + '}', str(conf.__dict__[k]))
    for k in conf.jm.__dict__:
        s = s.replace('_JM_{conf.jm.' + k + '}', str(conf.jm.__dict__[k]))
    p = re.compile(r'_JM_\{[a-zA-Z][\w\.]*\}')
    if p.search(s):
        warn("FOUND _JM_ macros which couldn't be expanded!")
        warn("               file: %s" % source)
        warn("\n                 ".join(p.findall(s)))
        warn("")
    destf = open(target, 'w')    
    destf.write(s)




def _replace_title( nb_node, source_abs_fn, replacement, title_pat=r'(.*)') -> str:
        """ Finds the title of a notebook and replaces it with replacement
            Returns the old title.
        """
        
        # look for title

        pat = re.compile(r'^(\s*#\s+)'+ title_pat)
        for cell in nb_node.cells:
            if cell.cell_type == "markdown":
                ma = pat.search(cell.source)
                
                if ma:
                    found_title = ma.group(0)
                    cell.source = re.sub(pat, 
                                         replacement,
                                         cell.source) 
                    break
        
        if not ma:            
            error("Couldn't find title in file: \n   %s\nThere should be a markdown cell beginning with text # bla bla    Complete pattern: %s" % (source_abs_fn,pat.pattern)) 
        return found_title

class FileKinds(Enum):
    SOLUTION = 1
    EXERCISE = 2
    TEST = 3
    OTHER = 4
    CHALLENGE_SOLUTION = 5

    @staticmethod
    def sep(ext):
        if ext == 'py':
            return '_'
        else:
            return '-'
    
    @staticmethod
    def is_supported_ext(fname, supp_ext):
        for ext in supp_ext:
            if fname.endswith('.%s' % ext):
                return True
        return False
    
    @staticmethod
    def detect(fname):
        """ TODO can't detect EXERCISE 
        """
        l = fname.split(".")
        if len(l) > 0:
            ext = l[-1]
        else:
            ext = ''
        sp = FileKinds.sep(ext)
        if fname.endswith('%schal%ssol.%s' % (sp, sp, ext)):
            return FileKinds.CHALLENGE_SOLUTION
        elif fname.endswith('%ssol.%s' % (FileKinds.sep(ext), ext)):
            return FileKinds.SOLUTION            
        elif fname.endswith("_test.py") :
            return FileKinds.TEST        
        else:
            return FileKinds.OTHER

    @staticmethod
    def check_ext(fname, supp_ext):
        if not FileKinds.is_supported_ext(fname, supp_ext):
            raise Exception("%s extension is not supported. Valid values are: %s" % (fname, supp_ext))
        
    @staticmethod        
    def exercise(radix, ext, supp_ext):      
        FileKinds.check_ext(ext,supp_ext)
        return radix + "." + ext

    @staticmethod
    def exercise_from_solution(fname, supp_ext):
        FileKinds.check_ext(fname, supp_ext)
        ext = fname.split(".")[-1]
               
        return fname.replace(FileKinds.sep(ext) + "sol." + ext, "." + ext)
        
    @staticmethod
    def solution(radix, ext, supp_ext):
        FileKinds.check_ext(ext, supp_ext)
        return radix + FileKinds.sep(ext) + 'sol.' + ext

    @staticmethod
    def test(radix):
        return radix + '_test.py'

    
    

def check_paths(path, path_check):
    if not isinstance(path, str):
        raise ValueError("Path to delete must be a string! Found instead: %s " % type(path))
    if len(path.strip()) == 0:
        raise ValueError("Provided an empty path !")
    if not isinstance(path_check, str):
        raise ValueError("Path check to delete must be a string! Found instead: %s" % type(path_check))
    if len(path_check.strip()) == 0:
        raise ValueError("Provided an empty path check!")
    if not path.startswith(path_check):        
        fatal("FAILED SAFETY CHECK FOR DELETING DIRECTORY %s ! \n REASON: PATH DOES NOT BEGIN WITH %s" % (path, path_check) )

def uproot(path):
    """ Returns a relative path from input path to root.
        
        NOTE: IT IS SUPPOSED TO BE RUN FROM A PYTHON FILE RESIDING *AT ROOT LEVEL*

        Example:
        >>> uproot('_static/img/cc-by.png')
        >>>  '../../'
        >>> uproot('_static')
        >>>  '../'
    """
    if not path:
        raise ValueError('Invalid filepath=%s' % path)

    ret = os.path.relpath(os.path.abspath(os.getcwd()),
                              os.path.abspath(path))
    if os.path.isfile(path) and ret.endswith('..'):
        ret = ret[:-2]
    if ret.endswith('..'):
        ret = ret + '/'
    return ret


def delete_tree(path, path_check):
    """ Deletes a directory, checking you are deleting what you really want

        path: the path to delete as a string
        path_check: the beginning of the path to delete, as a string
    """
    info("Cleaning %s  ..." % path)
    check_paths(path, path_check)

    if not os.path.isdir(path):
        raise Exception("Provided path is not a directory: %s" % path)

    #duplicated check (it's already in check_paths, but just to be sure)
    if path.startswith(path_check):
        shutil.rmtree(path)
    else:
        fatal("FAILED SAFETY CHECK FOR DELETING DIRECTORY %s ! \n REASON: PATH DOES NOT START WITH %s" % (path, path_check) )


def delete_file(path, path_check):
    """ Deletes a file, checking you are deleting what you really want

        path: the path to delete as a string
        path_check: the beginning of the path to delete, as a string
    """
    info("Cleaning %s  ..." % path)
    check_paths(path, path_check)

    if not os.path.isfile(path):
        raise Exception("Provided path is not a file: %s" % path)

    #duplicated check (it's already in check_paths, but just to be sure)
    if path.startswith(path_check):
        os.remove(path)
    else:
        fatal("FAILED SAFETY CHECK FOR DELETING FILE %s ! \n REASON: PATH DOES NOT START WITH %s" % (path, path_check) )


def tag_start(tag):
    return '#' + tag

def tag_end(tag):
    return '#/' + tag

def tag_regex(string, must_begin=True, preserve_line=False):
    """ Takes a non-regex string and return a regex string which ignores extra
        spaces in s and newline after 

        must_begin : if True, provided string must be at the beginning of code / cell
        preserve_line : if True, characters following the tag until the end of the line are ignored

        @since 3.3
    """
    if len(string) == 0:
            raise ValueError("Expect a non-empty string !")
    # so we do not get spaces escaped, which I find horrible default behaviour: 
    # https://stackoverflow.com/questions/32419837/why-re-escape-escapes-space
    escaped = [re.escape(x) for x in string.split()] 
    removed_spaces = r'\s+'.join(escaped)
    begin_char= r'^' if must_begin else ''
    if preserve_line:
        preservel = r'(.*?)\n'
    else:
        preservel = r'()'
    return r"(?s)(%s\s*%s)%s(.*)" % (begin_char, removed_spaces, preservel)

def ignore_spaces(string, must_begin=True):
    """ Takes a non-regex string and return a regex string which ignores extra
        spaces in s and newline after 

        must_begin : if True, provided string must be at the beginning of code / cell
        
        @deprecated: use tag_regex instead
    """
    warn("DEPRECATED: jupman_tools.ignore_spaces is deprecated, use tag_regex instead")
    return tag_regex(string, must_begin)

def multi_replace(text, d):
    """ Takes a dictionary pattern -> substitution and applies all substitutions to text
    """
    s = text
    for key in d:
        s = re.sub(key, d[key], s) 
    return s

def span_pattern(tag):
    """ NOTE: Doesn't eat the blank afterwards, has lookahead
    
        @since 3.3
    """
    s = r"%s(.*?)%s" % (start_tag_pattern(tag).pattern, end_tag_pattern(tag).pattern)
    
    return re.compile(s, flags=re.DOTALL)

def start_tag_pattern(tag):
    """ NOTE: start tag always eats the blank afterwards, end tag doesn't (has lookahead)
    
        @since 3.3
    """    
    return re.compile(r"#%s\s" % tag, flags=re.DOTALL)

def end_tag_pattern(tag):
    """ NOTE: start tag always eats the blank afterwards, end tag doesn't (has lookahead)
    
        @since 3.3
    """
    ec = tag_end(tag)[-1]
    s = r"%s((%s$)|(%s(?=\s)))" % (tag_end(tag)[:-1], ec, ec)
    return re.compile(s, flags=re.DOTALL)

def single_tag_pattern(tag):
    """ NOTE: Doesn't eat the blank afterwards, has lookahead
        @since 3.3
    """
    
    ec = tag_start(tag)[-1]
    s = r"%s((%s$)|(%s(?=\s)))" % (tag_start(tag)[:-1], ec, ec)
    return re.compile(s, flags=re.DOTALL)


def init(jupman, conf={}):    
    """Initializes the system, does patching, etc

        Should be called in conf.py at the beginning of setup() 
    
        @since 3.2
    """
    logging.getLogger().setLevel(logging.INFO)
    if not conf:
        warn("globals() not passed to jmt.init call, please add it!")
    else:
        info("release: %s" % conf['release'])

        if os.environ.get('GOOGLE_ANALYTICS'):
            info("Found GOOGLE_ANALYTICS environment variable")
            conf['html_theme_options']['analytics_id'] = os.environ.get('GOOGLE_ANALYTICS')        
        else:
            info('No GOOGLE_ANALYTICS environment variable was found, skipping it')
    
    # hooks into ExecutePreprocessor.preprocess to execute our own filters.
    # Method as in https://github.com/spatialaudio/nbsphinx/issues/305#issuecomment-506748814

    def _from_notebook_node(self, nb, resources, **kwargs):
        debug('patched nbsphinx from_notebook_node')
                                
        for f in jupman.preprocessors:
            nb, resources = f.preprocess(nb, resources=resources)

        return nbsphinx_from_notebook_node(self, nb, resources=resources, **kwargs)        
    
    import nbsphinx
    nbsphinx_from_notebook_node = nbsphinx.Exporter.from_notebook_node                

    
    nbsphinx.Exporter.from_notebook_node = _from_notebook_node

def make_stripped_cell_id(cid):
    """ Given a solution id, creates a predictable new one 
            
        @since 3.3
    """
    
    #See https://nbformat.readthedocs.io/en/latest/format_description.html#cell-ids
    
    mx = 64    
    postfix = "-stripped"  # note: - is legal
        
    cand = cid + postfix
    if len(cand) > mx:
        return cid[:len(cid)-len(postfix)] + postfix
    else:
        return cand


class JupmanPreprocessor(Preprocessor):
    """ @since 3.2 """

    def __init__(self, jupman):
        """ @since 3.2 """
        super().__init__()
        self.jupman = jupman
    
    def preprocess(self, nb, resources):
        """ @since 3.2 """

        
        
        """Careful path *includes* part of docname:
        resources:
        {   
            'metadata': {
                            'path': '/home/da/Da/prj/jupman/prj/jupyter-example'
                        },
            'nbsphinx_docname': 'jupyter-example/jupyter-example-sol',
            'nbsphinx_save_notebook': '/home/da/Da/prj/jupman/prj/_build/html/.doctrees/nbsphinx/jupyter-example/jupyter-example-sol.ipynb',
            'output_files_dir': '../_build/html/.doctrees/nbsphinx',
            'unique_key': 'jupyter-example_jupyter-example-sol'
        }
        """
        rel_dir, partial_fn = os.path.split(resources['nbsphinx_docname'])                
        source_abs_fn = os.path.join(resources['metadata']['path'], partial_fn + '.ipynb')     

        if self.jupman._is_to_preprocess(nb, source_abs_fn):
            relpath = os.path.relpath(source_abs_fn, os.path.abspath(os.getcwd()))
            info("JupmanPreprocessor: parsing %s" % relpath )
            try:
                self.jupman.validate_tags(source_abs_fn)
            except Exception as ex:
                logger.warning("Failed Jupman tags validation! %s", ex)
                
            return self.jupman._sol_nb_to_ex(nb, source_abs_fn,website=True), resources
        else:
            return nb, resources


def replace_py_rel(code, filepath):
    """ Takes code to be copied into zips and removes unneeded relative imports
    """
    upr = uproot(filepath).replace('.',r'\.')     
    if len(re.findall(r'sys\..+', code)) > 1:
        repl = r'import sys\n'
    else:
        repl = ''
    
    ret =  re.sub(r'import\s+sys\s*;?\s*\nsys\.path.append\([\'\"]((%s))[\'\"]\)\s*;?\s*' % upr,   
                repl,
                code)
    return ret

def replace_md_rel(code, filepath):
    """ Takes markdown to be copied into zips and removes relative paths
    """
    upr = uproot(filepath).replace('.',r'\.')     
    
    ret =  re.sub(r'(\[.*?\]\()(%s)(.*?\))' % upr,               
                  r"\1\3",
                  code)
    
    ret = replace_html_rel(ret, filepath)
    return ret

def replace_html_rel(code, filepath):
    
    upr = uproot(filepath).replace('.',r'\.')

    ret =  re.sub(r'(<a\s+href=\")(%s)(.*?\"(\s+.*?=\".*?\")*>)' % upr,               
                  r"\1\3",
                  code)

    ret =  re.sub(r'(<img\s+src=\")(%s)(.*?\"(\s+.*?=\".*?\")*>)' % upr,
                  r"\1\3",
                  ret)    
    return ret

def replace_ipynb_rel(nb_node, filepath, website=False):
    """ MODIFIES nb_node without returning it !
    """

    for cell in nb_node.cells:
            
        if cell.cell_type == "code":    
            cell.source = replace_py_rel(cell.source, filepath)
        elif cell.cell_type == "markdown":
            # markdown cells: fix rel urls
            if not website:
                cell.source = replace_md_rel(cell.source, filepath)
        elif cell.cell_type == "raw" and \
                'raw_mimetype' in cell.metadata and cell.metadata['raw_mimetype'] == 'text/html':
            if not website:
                cell.source = replace_html_rel(cell.source, filepath)             
        else:
            #TODO latex ?
            pass
    
class Jupman:
    """ Holds Jupman-specific configuration for Sphinx build
    """

    def __init__(self):

        self.subtitle = "TODO CHANGE jm.subtitle"""
        self.course = "TODO CHANGE jm.course" 
        self.degree = "TODO CHANGE jm,degree"

        self.filename = 'jupman'   # The filename without the extension
        """ 'filename' IS *VERY* IMPORTANT !!!!
            IT IS PREPENDED IN MANY GENERATED FILES
            AND IT SHOULD ALSO BE THE SAME NAME ON READTHEDOCS 
            (like i.e. jupman.readthedocs.org) """

        self.chapter_files = ['jupman.py', 'my_lib.py', '_static/img/cc-by.png', 
                                
                            '_static/js/jupman.js',  # these files are injected when you call jupman.init()
                            '_static/css/jupman.css', 
                            '_static/js/toc.js',
                            
                            '_static/js/pytutor-embed.bundle.min.js.zip' ]
        """ Common files for exercise and exams as paths. Paths are intended relative to the project root. Globs like /**/* are allowed."""

        self.chapter_patterns =  ['*/']
        self.chapter_exclude_patterns =  ['[^_]*/','exams/', 'project/']

        self.ipynb_show_solution = "Show solution"
        self.ipynb_hide_solution = "Hide solution"
        self.ipynb_show_answer = "Show answer"
        self.ipynb_hide_answer = "Hide answer"

        self.ipynb_solutions = "SOLUTIONS"
        self.ipynb_exercises = "EXERCISES"
        """ words used in ipynb files - you might want to translate these in your language. Use plurals."""        

        self.write_solution_here = tag_regex("# write here", must_begin=False, preserve_line=True)
        """ the string is not just a translation, it's also a command that when 
        building the exercises removes the content after it in the code cell it is 
        contained in. """

        self.solution = tag_regex("# SOLUTION")
        """ #NOTE: the string is not just a translation, it's also a command
            that  when building the exercises completely removes the content of the cell 
            it is contained in (solution comment included)."""


        self.markdown_answer = tag_regex('**ANSWER**:')
        """NOTE: the string is not just a translation, it's also a command 
                 that  when building the exercises removes the content after it in
                 the markdown cell it is contained in.
        """

        self.zip_ignored = ['__pycache__', '**.ipynb_checkpoints', '.pyc', '.cache', '.pytest_cache', '.vscode',]

        self.formats = ["html", "epub", "latex"]


        self.build = "_build"
        # Output directory. Not versioned.
        
        self.generated='_static/generated'
        # Directory where to put zips. Versioned. 
        # NOTE: this is *outside* build directory

        self.manuals = {
            "student": {
                "name" : "Jupman",  # TODO put manual name, like "Scientific Programming"
                "audience" : "studenti",
                "args" : "",
                "output" : ""
            }
        }
        self.manual = 'student'

        self.raise_exc = "jupman-raise"
        self.strip = "jupman-strip"
        self.preprocess = "jupman-preprocess"
        self.purge = "jupman-purge"
        self.purge_io = "jupman-purge-io"
        self.purge_input = "jupman-purge-input"
        self.purge_output = "jupman-purge-output"
        


        self.raise_exc_code = "raise Exception('TODO IMPLEMENT ME !')"
        """ WARNING: this string can end end up in a .ipynb json, so it must be a valid JSON string  ! Be careful with the double quotes and \n  !!
        """


        self.solution_tags = [self.raise_exc, self.strip]
        """ Code cells containing these tags are considered solutions        
            @since 3.3
        """


        self.span_tags = [self.raise_exc, self.strip, self.purge]
        """ Tags which enclose a span of text
            @since 3.3
        """

        self.directive_tags = [self.preprocess, self.purge, self.purge_input, self.purge_output, self.purge_io]
        """ Code cells containing these tags are not considered a solution.
            @since 3.3
        """

        self.distrib_ext = ['py', 'ipynb']
        """ Supported distribution extensions
        """


        self.preprocessors = [JupmanPreprocessor(self)]
        """ Notebook preprocessors. Default one is JupmanPreprocessor.

            @since 3.2
        """

    def _purge_tags(self, text):
        """ Purges text according to directives, and removes all other Jupman tags. Only the tags, not their content!
            
            WARNING: in other words, this function IS *NOT* SUFFICIENT 
                    to completely clean exercises from solutions !!!
            
            @since 3.3
        """
        ret = text
        if self.purge_input in text or self.purge_io in text:
            return ''
        #NOTE: span_pattern doesn't eat the blank afterwards (has lookahead)
        ret = re.sub(span_pattern(self.purge), '', ret)
                    
        # so longer come first
        all_tags = sorted(set(self.solution_tags + self.directive_tags), reverse=True)
            
        
        for tag in all_tags:
            if tag in self.span_tags:
                #NOTE: start tag always eats the blank afterwards, end tag doesn't (has lookahead)
                ret = re.sub(start_tag_pattern(tag), '\n', ret)                
                ret = re.sub(end_tag_pattern(tag), '', ret)
                
            else:
                #NOTE: single_tag_pattern doesn't eat the blank afterwards (has lookahead)
                ret = re.sub(single_tag_pattern(tag), '', ret)            
        
        return ret


    def is_zip_ignored(self, fname):
        import pathspec
        spec = pathspec.PathSpec.from_lines('gitwildmatch', self.zip_ignored)
        return spec.match_file(fname)
                

    def get_exercise_folders(self):
        ret = []
        for p in self.chapter_patterns:
            for r in glob.glob(p):
                if r not in ret:
                    ret.append(r)
        for p in self.chapter_exclude_patterns:
            for r in glob.glob(p):
                if r in ret:
                    ret.remove(r)
        return ret

    def get_exam_student_folder(self, ld):
        parse_date(ld)
        return '%s-%s-FIRSTNAME-LASTNAME-ID' % (self.filename,ld)    


    def is_code_sol(self, solution_text):
        """ Returns True if a cell contains any elements to be stripped in a solution           
        """
        return self.sol_to_ex_code(solution_text, parse_directives=False).strip() != solution_text.strip()


    def is_to_strip(self, solution_text):
        """ Returns True if a cell contains any elements to strip

           @since 3.3
        """
        return self.sol_to_ex_code(solution_text, parse_directives=True).strip() != solution_text.strip()

    def sol_to_ex_code(self, solution_text, filepath=None, parse_directives=True):
        
        ret = solution_text
        
        if parse_directives:
            if self.purge_input in solution_text or self.purge_io in solution_text:
                return ''
            ret = re.sub(span_pattern(self.purge), '', ret)
            for tag in sorted(self.directive_tags, reverse=True):
                ret = re.sub(single_tag_pattern(tag), '', ret)

        if re.match(self.solution, ret.strip()):
            return ''

        ret = re.sub(span_pattern(self.raise_exc), 
                     self.raise_exc_code, 
                     ret)
        
        ret = re.sub(span_pattern(self.strip), '', ret)
                    
        ret = re.sub(self.write_solution_here, r'\1\2\n\n', ret)
        
        if filepath:
            ret = replace_py_rel(ret, filepath)
            
        return ret            

    def validate_tags(self, fname):
        """ Validates jupman tags in file fname and return the number of solution tags found.
        """
        ret = 0
        if fname.endswith('.ipynb'):
            import nbformat        
            nb_node = nbformat.read(fname, nbformat.NO_CONVERT)        
            for cell in nb_node.cells:            
                if cell.cell_type == "code":    
                    ret += self.validate_code_tags(cell.source, fname)
                elif cell.cell_type == "markdown":
                    ret += self.validate_markdown_tags(cell.source, fname)                

        elif fname.endswith('.py'):
            with open(fname) as f:
                ret += self.validate_code_tags(f.read(), f)
        else:
            raise ValueError('File format not supported for %s' % fname)
        return ret

    def validate_code_tags(self, text, fname):
        """ Validates text which was read from file fname:

            - raises ValueError on mismatched tags
            - returns the number of solution tags found
        """
                
        tag_starts = {}
        tag_ends = {}
        ret = 0

        for tag in self.span_tags:
            tag_starts[tag] = len(re.compile(tag_start(tag) + r'\s').findall(text))
            tag_ends[tag] = len(re.compile(end_tag_pattern(tag)).findall(text))
            
            if tag in self.solution_tags:
                ret += tag_starts[tag]

        for tag in tag_starts:
            if tag not in tag_ends or tag_starts[tag] != tag_ends[tag] :
                raise ValueError("Missing final tag %s in %s" % (tag_end(tag), fname) )

        for tag in tag_ends:
            if tag not in tag_starts or tag_starts[tag] != tag_ends[tag] :
                raise ValueError("Missing initial tag %s in %s" % (tag_start(tag), fname) )
        
        ret += len(re.compile(self.write_solution_here).findall(text))
        ret += len(re.compile(self.solution).findall(text))
        
        return ret

    def validate_markdown_tags(self, text, fname):
        return len(re.compile(self.markdown_answer).findall(text))


    def _copy_test(self, source_abs_fn, source_fn,  dest_fn):
        with open(source_abs_fn, encoding='utf-8') as source_f:
                                                          
            data= multi_replace(source_f.read(), {
                r'from\s+(.+)_sol\s+import\s+(.*)' : r'from \1 import \2',
                r'import\s+(.+)_sol((\s*)|,)':r'import \1\2', 
                
            })
            data = replace_py_rel(data, source_abs_fn)
            
            info('  Writing (patched) %s' % dest_fn) 
            with open(dest_fn, 'w', encoding='utf-8') as dest_f:
                dest_f.write(data)        
    
    def _copy_other(self, source_abs_fn, source_fn, dest_fn, new_root = ''):
        
        if source_abs_fn.endswith('.py') :
            with open(source_abs_fn, encoding='utf-8') as source_f:
                data = source_f.read()
                data = replace_py_rel(data, source_abs_fn)
                info('  Writing (patched) %s' % dest_fn) 
            with open(dest_fn, 'w', encoding='utf-8') as dest_f:
                dest_f.write(data)             
        elif source_abs_fn.endswith('.ipynb') :
            import nbformat
            # note: for weird reasons nbformat does not like the sol_source_f 
            nb_node = nbformat.read(source_abs_fn, nbformat.NO_CONVERT)
                                                        
            replace_ipynb_rel(nb_node, source_abs_fn)
            info('  Writing (patched) %s' % dest_fn) 
            nbformat.write(nb_node, dest_fn)
        else:
            info("  Writing %s " % dest_fn)
            shutil.copy(source_abs_fn, dest_fn)        
                 
    def _copy_sols(self, source_fn, source_abs_fn, dest_fn):
        if source_fn.endswith('.py'):
            
            with open(source_abs_fn) as sol_source_f:
                text = sol_source_f.read()
                found_total_purge = self.purge_input in text or self.purge_output in text or self.purge_io in text or ''
                if found_total_purge:
                    raise ValueError("Found %s in python file %s, but it is only allowed in notebooks!" % (found_total_purge, source_fn))
                
                text = replace_py_rel(text, source_abs_fn)                
                text = self._purge_tags(text)
                with open(dest_fn, 'w') as solution_dest_f:
                    info("  Writing (patched) %s " % dest_fn)
                    solution_dest_f.write(text)
        elif source_fn.endswith('.ipynb'):
            # py cells: strip jupman tags, fix rel urls
            import nbformat
            # note: for weird reasons nbformat does not like the sol_source_f 
            nb_node = nbformat.read(source_abs_fn, nbformat.NO_CONVERT)
            replace_ipynb_rel(nb_node, source_abs_fn)
            for cell in nb_node.cells:            
                if cell.cell_type == "code":                                            
                    if self.purge_output in cell.source or self.purge_io in cell.source:
                        cell.outputs = []                        
                    if (self.purge_input in cell.source and self.purge_output in cell.source) \
                        or self.purge_io in cell.source:
                        cell.metadata['nbsphinx'] = 'hidden'
                        
                    cell.source = self._purge_tags(cell.source)

            nbformat.write(nb_node, dest_fn)
            
        else: # solution format not supported                           
            info("Writing %s" % source_fn)
            shutil.copy(source_abs_fn, dest_fn)
            
    
    def _sol_nb_to_ex(self, nb, source_abs_fn, website=False ):
        """ Takes a solution notebook object and modifies it to strip solutions            

            @since 3.2
        """    
        from nbformat.v4 import new_raw_cell

        def before_cell(n, cell_type):            
            
            if cell_type == 'code': 
                show = self.ipynb_show_solution
                hide = self.ipynb_hide_solution
                sol_class = 'jupman-sol-code'
            elif cell_type == 'markdown':
                show = self.ipynb_show_answer
                hide = self.ipynb_hide_answer
                sol_class = 'jupman-sol-question'
            else:
                warn("NO LABEL FOUND FOR cell_type %s, using default ones!" % cell_type)
                show = self.ipynb_show_solution
                hide = self.ipynb_hide_solution
                sol_class = 'jupman-sol-code'

            
            s = """<a  class="jupman-sol jupman-sol-toggler" """
            s += """\n onclick="jupman.toggleSolution(this);" """
            s += """\n data-jupman-show="%s" data-jupman-hide="%s">%s</a>""" % (show, hide, show)
            s += """<div class="jupman-sol %s" style="display:none">  """ % sol_class
            
            ret = new_raw_cell()
            ret.metadata.format = "text/html"
            ret.source = s
            return ret
            

        def after_cell():
            ret = new_raw_cell()
            ret.metadata.format = "text/html"
            ret.source = """</div>"""
            return ret            


        import copy
        
        replace_ipynb_rel(nb, source_abs_fn, website)                                                
        
        
        if not website:            
            if FileKinds.detect(source_abs_fn) == FileKinds.CHALLENGE_SOLUTION:
                _replace_title(nb, 
                                source_abs_fn, 
                                r"# \2", 
                                title_pat=r'(.*?)\s+(%s)' % self.ipynb_solutions)
            else:
                _replace_title(nb, 
                            source_abs_fn, 
                            r"# \2 %s" % self.ipynb_exercises)
        
        # look for tags
        sh_cells = nb.cells[:]
        nb.cells = []      

        cell_counter = 0

        for cell in sh_cells:
            stripped_cell = copy.deepcopy(cell)
            if "id" in cell:
                stripped_cell["id"] = make_stripped_cell_id(cell["id"])

            if cell.cell_type == "code":
                if self.is_to_strip(cell.source):                            
                                                            
                    if self.purge_output in cell.source or self.purge_io in cell.source:
                        stripped_cell.outputs = []
                        
                    if (self.purge_input in cell.source and self.purge_output in cell.source) \
                        or self.purge_io in cell.source:
                        stripped_cell.metadata['nbsphinx'] = 'hidden'
                        
                    
                    
                    stripped_cell.source = self.sol_to_ex_code(cell.source,source_abs_fn)
                    if website:
                        
                        
                        if self.purge_input in cell.source or self.purge_io in cell.source:
                            #weird stuff: https://github.com/jupyter/nbconvert/blob/42cfece9ed07232c3c440ad0768b6a76f667fe47/nbconvert/preprocessors/tagremove.py#L98
                            #NOTE: this MUST be ONLY for website as transient is not even an nbformat valid field !
                            if getattr(stripped_cell, 'transient', None):
                                stripped_cell.transient['remove_source'] = True
                            else:
                                stripped_cell.transient = {
                                    'remove_source': True
                                }
                        
                        if self.is_code_sol(cell.source) \
                           and not (self.purge_input in cell.source or self.purge_io in cell.source):
                            nb.cells.append(before_cell(cell_counter, cell.cell_type))
                                                        
                            cell.source = self._purge_tags(cell.source)
                            nb.cells.append(cell)
                            nb.cells.append(after_cell())
                    nb.cells.append(stripped_cell)
                else:
                    nb.cells.append(cell)
            elif cell.cell_type == "markdown":                    
                if re.match(self.markdown_answer, cell.source.strip()):
                    if website:
                        nb.cells.append(before_cell(cell_counter, cell.cell_type))
                        nb.cells.append(cell)
                        nb.cells.append(after_cell()) 
                    else:
                         # substitutes with newline, otherwise it shows 'Type markdown or latex'   
                        stripped_cell.source = re.sub( self.markdown_answer, 
                                                       r"\1\n",  
                                                       cell.source.strip())
                        
                        nb.cells.append(stripped_cell)                   
                else:
                    nb.cells.append(cell)
            else:
                nb.cells.append(cell)

            cell_counter += 1
        return nb                    


    def _is_to_preprocess(self, nb, source_abs_fn):
        """
            @since 3.3
        """
                                    
        if source_abs_fn.endswith('.ipynb'):
            
            fileKind = FileKinds.detect(source_abs_fn)
                                                    
            if fileKind == FileKinds.SOLUTION:
                return True
            
            if fileKind == FileKinds.CHALLENGE_SOLUTION:  # weird case, only really for jupman documentation itself
                return True
            
            if len(nb.cells) > 0:
                cell = nb.cells[0]
                if cell.cell_type == 'code' and ('#' + self.preprocess) in cell.source :
                    return True
            
        return False
    
        

    def generate_exercise(self, source_rel_fn, dest_dir='./'):
        """ Given a relative filename, generates the corresponding exercise file in dest_dir
        """
        if not FileKinds.is_supported_ext(source_rel_fn, self.distrib_ext):
            raise ValueError("Exercise generation from solution not supported for file type %s" % source_rel_fn)

        kind = FileKinds.detect(source_rel_fn)

        source_abs_fn = os.path.abspath(source_rel_fn)
        source_dir = os.path.dirname(source_abs_fn)
        exercise_fn = FileKinds.exercise_from_solution(os.path.basename(source_rel_fn), self.distrib_ext)
        
        exercise_abs_fn = os.path.join(source_dir, exercise_fn)
        exercise_dest_fn = os.path.join(dest_dir , exercise_fn)

        info("  Generating %s" % exercise_dest_fn)

        with open(source_abs_fn) as sol_source_f:            

            found_tag = self.validate_tags(source_abs_fn)                      
            if not found_tag and not os.path.isfile(exercise_abs_fn) :
                error("There is no exercise file and couldn't find any jupman solution tag in solution file for generating exercise !" +\
                    "\n  solution: %s\n  exercise: %s" % (source_abs_fn, exercise_abs_fn))                                                                      
            if not kind == FileKinds.CHALLENGE_SOLUTION and found_tag and os.path.isfile(exercise_abs_fn) :
                error("Found jupman tags in solution file but an exercise file exists already !\n  solution: %s\n  exercise: %s" % (source_abs_fn, exercise_abs_fn))
                                
            with open(exercise_dest_fn, 'w') as exercise_dest_f:
                
                if source_abs_fn.endswith('.ipynb'):
                    
                    import nbformat
                    
                    # note: for weird reasons nbformat does not like the sol_source_f 
                    nb_node = nbformat.read(source_abs_fn, nbformat.NO_CONVERT)
                    self._sol_nb_to_ex(nb_node, source_abs_fn, website=False)
                            
                    nbformat.write(nb_node, exercise_dest_f)
                
                
                elif source_abs_fn.endswith('.py'):                       
                    exercise_text = self.sol_to_ex_code(sol_source_f.read(), source_abs_fn)
                    #debug("FORMATTED TEXT=\n%s" % exercise_text)
                    exercise_dest_f.write(exercise_text)                    
                else:
                    raise ValueError("Don't know how to translate solution to exercise for source file %s" % source_abs_fn)
   
    def copy_code(self, source_dir, dest_dir, copy_solutions=False):
                
        info("Copying code %s \n    from  %s \n    to    %s" % ('and solutions' if copy_solutions else '', source_dir, dest_dir))

        # creating folders
        for dirpath, dirnames, filenames in os.walk(source_dir):
                                    
            compath = os.path.commonpath([dirpath, source_dir])
            dest_subdir = os.path.join(dest_dir, dirpath[len(compath)+1:])
                            
            if not self.is_zip_ignored(dest_subdir):
                if not os.path.isdir(dest_subdir) :
                    info("Creating dir %s" % dest_subdir)
                    os.makedirs(dest_subdir)
                        
                for source_fn in filenames:                    
                    if not self.is_zip_ignored(source_fn):
                        
                        source_abs_fn = os.path.join(dirpath,source_fn)
                        dest_fn = os.path.join(dest_subdir , source_fn)                           
                        fileKind = FileKinds.detect(source_fn)
                        
                        if fileKind == FileKinds.CHALLENGE_SOLUTION:
                            # challenge solutions are supposed to be generated 
                            # manually inside the jupyter notebook

                            pass
                        elif fileKind == FileKinds.SOLUTION:
                            if copy_solutions:                                           
                                self._copy_sols(source_fn, 
                                                source_abs_fn,
                                                dest_fn)
                            
                            if FileKinds.is_supported_ext(  source_fn,
                                                            self.distrib_ext):
                                self.generate_exercise( os.path.join(dirpath,source_fn),
                                                        dest_dir=dest_subdir)
                                            
                                
                        elif fileKind == FileKinds.TEST:                            
                            self._copy_test(source_abs_fn,
                                            source_fn,
                                            dest_fn)
                        else:  # EXERCISE and OTHER
                            self._copy_other(source_abs_fn,
                                             source_fn,
                                             dest_fn)

    def _common_files_maps(self, zip_name):
        """        
           @since 3.2 Created in order to make exam.py work
        """
        deglobbed_common_files = []
        deglobbed_common_files_patterns = []
        for common_path in self.chapter_files:                
            cur_deglobbed = glob.glob(common_path, recursive=True)       
            deglobbed_common_files.extend(cur_deglobbed)
            deglobbed_common_files_patterns.extend(
                [("^(%s)$" % x, "%s/%s" % (zip_name, x)) for x in cur_deglobbed])
        return (deglobbed_common_files, deglobbed_common_files_patterns)

    def zip_folder(self, source_folder, renamer=None):
        """ Takes source folder and creates a zip with processed files

            renamer: (optional) function which takes source folder names 
                      and gives the corresponding zip name to generate

        """
        if source_folder.startswith('..'):
            fatal("BAD FOLDER TO ZIP ! STARTS WITH '..'=%s" % source_folder)
        if len(source_folder.strip()) == 0:
            fatal("BAD FOLDER TO ZIP ! BLANK STRING")

        build_jupman = os.path.join(self.build, 'jupman')
        if renamer:
            zip_name = renamer(source_folder)
        else:
            zip_name = os.path.basename(os.path.normpath(source_folder))

        build_folder = os.path.join(build_jupman, zip_name)
        if not os.path.exists(self.generated):
            os.makedirs(self.generated)
        if os.path.exists(build_folder):
            delete_tree(build_folder, '_build')

        self.copy_code(source_folder, build_folder, copy_solutions=True)

        deglobbed_common_files, deglobbed_common_files_patterns = self._common_files_maps(zip_name)
        
        info("zip_name = %s" % zip_name)            
        zip_path = os.path.join(self.generated, zip_name)
        self.zip_paths( deglobbed_common_files + [build_folder], 
                        zip_path,
                        patterns = deglobbed_common_files_patterns + [("^(%s)" % build_jupman,"")])
        info("Done zipping %s" % source_folder ) 

    def zip_folders(self, selector, renamer=None):
        """ Takes source folder and creates a zip for each subfolder 
            filling it with processed files.

            selector: a glob pattern 
            renamer: (optional) function which takes source folder names 
                      and gives the corresponding zip name to generate
                      WITHOUT the .zip extension
        """
        source_folders =  glob.glob(selector)
        
        if selector.startswith('..'):
            fatal("BAD FOLDER TO ZIP ! STARTS WITH '..'=%s" % selector)
        if len(selector.strip()) == 0:
            fatal("BAD FOLDER TO ZIP ! BLANK STRING")
        if len(source_folders) == 0:
            warn("Nothing to zip for %s!" % selector)
            return
        info("Found stuff in %s , zipping them to %s" % (selector, self.generated))
        
        for d in source_folders:
            self.zip_folder( d, renamer)
        info("Done zipping %s" % selector ) 


    def latex_maketitle(self, html_baseurl):
    # - see this: https://tex.stackexchange.com/questions/409677/edit-1st-page-only
    # - ALSO ADDED THE SUPER IMPORTANT \makeatletter according to
    #    https://groups.google.com/d/msg/sphinx-users/S_ip2b-lrRs/62zkfWcODwAJ

        return r'''
            \makeatletter
            \pagestyle{empty}
            \thispagestyle{empty}
            \noindent\rule{\textwidth}{1pt}\par
                \begingroup % for PDF information dictionary
                \def\endgraf{ }\def\and{\& }%
                \pdfstringdefDisableCommands{\def\\{, }}% overwrite hyperref setup
                \hypersetup{pdfauthor={\@author}, pdftitle={\@title}}%
                \endgroup
            \begin{flushright}
                \sphinxlogo
                \py@HeaderFamily
                {\Huge \@title }\par
            ''' + r"{\itshape\large %s}\par" % unicode_to_latex( self.subtitle) + \
            r'''
                \vspace{25pt}
                {\Large
                \begin{tabular}[t]{c}
                    \@author
                \end{tabular}}\par
                \vspace{25pt}
                \@date \par
                \py@authoraddress \par
            \end{flushright}
            \@thanks
            \setcounter{footnote}{0}
            \let\thanks\relax\let\maketitle\relax
            %\gdef\@thanks{}\gdef\@author{}\gdef\@title{}
                \vfill
                \noindent Copyright \copyright\ \the\year\ by \@author.
                \vskip 10pt
                \noindent \@title\ is available under the Creative Commons Attribution 4.0
                International License, granting you the right to copy, redistribute, modify, and
                sell it, so long as you attribute the original to \@author\ and identify any
                changes that you have made. Full terms of the license are available at:
                \vskip 10pt
                \noindent \url{http://creativecommons.org/licenses/by/4.0/}
                \vskip 10pt
                \noindent The complete book can be found online for free at:
                \vskip 10pt''' + (r'''
                \noindent \url{%s}''' % html_baseurl)


    def zip_paths(self, rel_paths, zip_path, patterns=[], remap=None):
        """ zips provided rel_folder to file zip_path (WITHOUT .zip) !
            rel_paths MUST be relative to project root
            
            This function was needed as default python zipping machinery created weird zips 
            people couldn't open in Windows AND it is not deterministic https://github.com/DavidLeoni/jupman/issues/60
            
            - patterns is a list of tuples source regexes to dest               
            - remap is a function that takes a string and returns a string, and is applied after patterns
            
        """
        
        
        if zip_path.endswith('.zip'):
            raise ValueError("zip_path must not end with .zip ! Found instead: %s" % zip_path)

        for rel_path in rel_paths:
            abs_path = os.path.join(super_doc_dir() , rel_path)

            if not(os.path.exists(abs_path)):
                raise ValueError("Expected an existing file or folder relative to project root ! Found instead: %s" % rel_path)

        
        def write_file(fname):
            
            
            if not self.is_zip_ignored(fname) :
                #info('Zipping: %s' % fname)            
                
                
                if isinstance(patterns, types.FunctionType):
                    warn("zip_paths: using patterns as a function is deprecated, please use remap attribute instead")                    
                    the_remap = patterns
                    the_patterns = []
                else:
                    the_patterns = patterns
                    the_remap = remap
                    
                if len(the_patterns) == 0 and the_remap == None:
                    to_name = '/%s' % fname
                else:
                    if len(the_patterns) > 0:
                        to_name = fname
                        for pattern, to in the_patterns:
                            try:
                                to_name = re.sub(pattern, to, to_name)
                            except Exception as ex:
                                error("Couldn't substitute pattern \n  %s\nto\n  %s\nin string\n  %s\n\n" % (pattern, to, to_name) , ex)
                                                                
                    if the_remap != None:
                        to_name = the_remap(fname)

                #info('to_name = %s' % to_name)                    
                
                permission = 0o755 if os.access(fname, os.X_OK) else 0o644
                zip_info = zipfile.ZipInfo.from_file(fname, to_name)
                zip_info.date_time = (2020, 1, 1, 0, 0, 0)
                zip_info.external_attr = (stat.S_IFREG | permission) << 16
                with open(fname, "rb") as fp:
                    archive.writestr(
                        zip_info,
                        fp.read(),
                        compress_type=zipfile.ZIP_DEFLATED,
                        #compresslevel=9, # python 3.7+
                    )                
                

        archive = zipfile.ZipFile(zip_path + '.zip', "w")
                
        
        
        for rel_path in sorted(rel_paths):

            if os.path.isdir(rel_path):            
                for dirname, dirs, files in sorted(os.walk(rel_path), key=lambda t: t[0]):
                    dirNamePrefix = dirname + "/*"                
                    filenames = glob.glob(dirNamePrefix)                    
                    for fname in sorted(filenames):
                        if os.path.isfile(fname):
                            write_file(fname)
            elif os.path.isfile(rel_path):
                info('Writing %s' % rel_path)
                write_file(rel_path)
            else:
                raise ValueError("Don't know how to handle %s" % rel_path)
        archive.close()
            
        info("Wrote %s.zip" % zip_path)

