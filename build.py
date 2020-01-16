#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Builds documentation for Jupiter notebooks courses: https://github.com/DavidLeoni/jupman

# For more info, see help() function


import subprocess
import os
import sys
import inspect
import re
import glob
import fileinput
import string
from pathlib import Path

import conf

from conf import jm

from jupman_tools import info, warn, fatal
import jupman_tools as jt

def help():

    print("")
    print("  FOR COMPLETE EXPLANATION OF DOCS SYSTEM, SEE JUPMAN WEBSITE: https://github.com/DavidLeoni/jupman")
    print("")
    print("  From the root of your project, run :")
    print("")
    print("      python3 build.py")
    print("")
    print("")
    print("    OPTIONS")
    print("")
    print("        --quick   -q     Quick build that just generates student manual, only in html format")
    print("")
    print("        --formats  -f    " + ' | '.join(jm.formats) + "       separate with comma to build more than one")
    print("")
    print("    EXAMPLE USAGE:")
    print("")
    print("        python3s build.py  -f html,epub,latex")
    print("")


sphinxcmd = "./sphinx3-build"

# use this for python2:
# sphinxcmd = "sphinx-build"



def print_generated_banner(manual, fmt):
    tinfo = jm.manuals[manual]
    print("\n\n    Generated %s %s !\n\n\n       This manual is intended for %s audience" % (manual, fmt, tinfo['name'])) 
    print("\n\n       You can now find it at\n\n")

def get_path(manual, fmt):
    tinfo = jm.manuals[jm.manual]
    if fmt == "html":
        return "file://" + os.path.abspath(jm.build + tinfo['output']  + "/html/index.html")
    else:
        return "file://" + os.path.abspath(jm.build + tinfo['output']  + "/" + fmt + "/")


def outdir(manual, fmt):
    """ Returns the output directory given a manual and format
    """
    return os.path.join(jm.build, jm.manuals[jm.manual]['output'], fmt)



new_python_path = None

if 'PYTHONPATH' in os.environ:
    new_python_path = os.path.join(os.environ['PYTHONPATH'],  jt.super_doc_dir())
else:
    new_python_path = jt.super_doc_dir()
my_env = os.environ.copy()
my_env['PYTHONPATH'] = new_python_path

def run(cmd, cwd=None):
    print("")
    print("  " + cmd)
    print("")
    res = subprocess.check_output(cmd,
                                   shell=True,
                                   env=my_env,
                                   cwd=cwd
                                  )
    print(res.decode('UTF-8'))
    return res
    
def run_sphinx(manuals, formats):
    built = {}
    failed = {}

    jupman_out = os.path.join(jm.build, 'jupman')
    if os.path.isdir(jupman_out):
        jt.delete_tree(jupman_out, '_build')
    
    for manual in manuals: 
        for fmt in formats:

            relout = outdir(manual, fmt)
            if os.path.isdir(relout):
                jt.delete_tree(relout, '_build')

            tinfo = jm.manuals[manual]

            print("Building %s %s in %s" % (tinfo['name'], fmt, relout))

            # sphinx-build -b  html doc _build/student/html 

            try:
                cmd = (sphinxcmd + " -j 4 -b " + fmt + " . " + relout + " " + tinfo['args'] )
                res = run(cmd)
                    

                if fmt == 'html':

                    print("Fixing links to PDFs and EPUBs ... ") # Because of this crap: http://stackoverflow.com/a/23855541

                    with open(relout + '/index.html', "r+") as f:
                        data = f.read()

                        data = data.replace('_JM_{download}', 'Download ')
                        
#<a href="http://readthedocs.org/projects/jupman/downloads/pdf/latest/" target="_blank">PDF</a>
                        print(formats)
                        data = data.replace('_JM_{html}', '&ensp;<a target="_blank" href="/downloads/htmlzip/latest/">HTML</a>')

                        if 'pdf' in formats:
                            data = data.replace('_JM_{pdf}', '&ensp;<a target="_blank" href="/downloads/pdf/latest/">PDF</a>')
                        elif 'latex' in formats:
                            print("TODO LATEX !")
                        else:
                            data = data.replace('_JM_{pdf}', '')

                        if 'epub' in formats:
                            data = data.replace('_JM_{epub}', '&ensp;<a target="_blank" href="/downloads/epub/latest/">EPUB</a>')
                        else:
                            data = data.replace('_JM_{epub}', '')


                        print("Putting code documentation links ...")

                        f.seek(0)
                        f.write(data)
                    
                    info("Fixing html paths for offline browsing ....")

                    replace_html(relout, 'https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/', '_static/js/')
                    replace_html(relout, 'https://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.10/', '_static/js/')
                    replace_html(relout, 'https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML', '_static/js/MathJax.js')
                    replace_html(relout, 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML',  '_static/js/MathJax.js')

                elif fmt == 'latex':                  
                    run('latexmk -r latexmkrc -pdf -f -dvi- -ps- -jobname=' + jm.filename + ' -interaction=nonstopmode', cwd=relout)
                
                print_generated_banner(manual, fmt)            

                print("          "  + get_path(manual, fmt)  + "\n\n");
        
                built[(manual, fmt)] = {}

            except  subprocess.CalledProcessError as err:
                failed[(manual, fmt)] = {'err': err}
                print("ERROR: FAILED BUILDING %s %s  SKIPPING IT !!" % (manual, fmt))
                print(err.output)
    

    if len(built) > 0:
        print("\n\n  GENERATED MANUALS: \n\n")
        maxpad = 0
        for (manual, fmt) in sorted(built.keys()):
            maxpad = max(maxpad, len("     %s %s  :   " % (manual, fmt)))
        for (manual, fmt) in sorted(built.keys()):
            print(("      %s %s :   " % (manual, fmt)).rjust(maxpad) + get_path(manual, fmt))
        print("")
        print("")
    if len(failed) > 0:
        print("\n\n   THERE WERE ERRORS WHILE BUILDING:\n\n")
        for (manual, fmt) in failed.keys():
            print("       %s %s :   " % (manual, fmt))
            print("             " + str(failed[(manual, fmt)]['err']) + "   \n\n" )
        exit(1)
    

def wrongarg(msg):
    #print("    ERROR! " + msg)
    #print("")
    exit("\n\n    ERROR! " + msg + "\n\n\n    For more info run:   build.py help\n\n")



def replace_html(relout, stext, rtext):
    """ Replaces strings in html files (useful for correcting links to cdn libs)
        stext:  string to find
        rtext:  string to replace with
        relout: i.e. _build/html
    """

    path =  "%s/**/*.html" % relout

    info("finding %s: replacing with:  %s in: %s " % (stext, rtext, path))

    files = glob.glob(path, recursive=True)  # recursive since python 3.5 https://stackoverflow.com/a/2186565
    
    for fname in files:
        #debug(fname)
        
        # debug([p.name for p in Path(relfname).parents])
        # for some reason it adds an empty string:    DEBUG=['exam-solutions', 'jm-templates', '']        
        
        for line in fileinput.input(fname,inplace=1):
            lineno = 0
            lineno = line.find(stext)
            if lineno >0:
                relfname = os.path.relpath(fname, start=relout)  # works from current dir                
                prefix =  '../' * (len(Path(relfname).parents) - 1)
                line =line.replace(stext, prefix + rtext)
            sys.stdout.write(line)


#  MAIN

manuals=jm.manuals.keys()
formats = ['latex', 'epub', 'html'] #html must be at the end because we need to copy pdfs !
draft = False

if len(sys.argv) == 2 and (sys.argv[1] == 'help' or sys.argv[1] == '--help' or sys.argv[1] == '-h'):
    help()
    exit()

i = 1
while i < len(sys.argv):
    if sys.argv[i] == '-f'  or sys.argv[i] == '--formats':
        if i + 1 == len(sys.argv):
            wrongarg("Missing parameter !")        
        formats = sys.argv[i+1].split(",")
        for fmt in formats:
            if not fmt in jm.formats:
                wrongarg("Expected format to be one of %s found instead '%s' "  %(jm.formats, fmt))
        i += 2
    elif sys.argv[i] == '-q' or sys.argv[i] == '--quick':
        draft = True
        manuals=['student']
        formats=['html']
        i += 1
    else:
        wrongarg("Unrecognized parameter '%s'" % sys.argv[i])
        i += 1

run_sphinx(manuals, formats)

