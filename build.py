#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Builds documentation for Jupiter notebooks courses: https://github.com/DavidLeoni/jupman

# For more info, see help() function

# 0.1  Sept 2017  David Leoni

import subprocess
import os
import sys
import inspect
import re
import glob
import fileinput
import string

from conf import *

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
    print("        --formats  -f    " + ' | '.join(FORMATS) + "       separate with comma to build more than one")
    print("")
    print("    EXAMPLE USAGE:")
    print("")
    print("        python3s build.py  -f html,epub,latex")
    print("")


sphinxcmd = "./sphinx3-build"

# use this for python2:
# sphinxcmd = "sphinx-build"


    
def detect_system():
    print("")
    print("Trying to detect system ...")
    import os.path

    print("Defaulting to 'default'")
    system = "default"
    print("")
    return system

def print_generated_banner(manual, format):
    tinfo = MANUALS[manual]
    print("\n\n    Generated " + tinfo['name'] + " " +  format + "!"
                                + "\n\n\n       This manual is intended for " + tinfo['audience'])
    print("\n\n       You can now find it at\n\n")

def get_path(manual, format):
    tinfo = MANUALS[manual]
    if format == "html":
        return "file://" + os.path.abspath(SYSTEMS[system]['outdir'] + tinfo['output']  + "/html/index.html")
    else:
        return "file://" + os.path.abspath(SYSTEMS[system]['outdir'] + tinfo['output']  + "/" + format + "/")


def outdir(manual, format):
    """ Returns the output directory given a manual and format
    """
    return SYSTEMS[system]['outdir'] + MANUALS[manual]['output']  + "/" + format



new_python_path = None

if 'PYTHONPATH' in os.environ:
    new_python_path = os.environ['PYTHONPATH'] + os.pathsep + super_doc_dir()
else:
    new_python_path = super_doc_dir()
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

    for manual in manuals: 
        for format in formats:

            tinfo = MANUALS[manual]

            relout = outdir(manual, format)
            print("Building " + tinfo['name'] + " "  + format +  " in " + relout)

            # sphinx-build -b  html doc _build/student/html 

            try:
                print("Cleaning " + str(relout) + "  ")
                
                if "_build/" in relout:
                    res = subprocess.check_output("rm -rf " + relout,
                                                   shell=True,
                                                   env=my_env
                                                  )
                else:
                    raise Exception("ERROR: FAILED SECURITY CHECK BEFORE CLEANING DIRECTORY: " + str(relout))
                    
                cmd = (sphinxcmd + " -j 4 -b " + format + " . " + relout + " " + tinfo['args'] )
                res = run(cmd)
                
                

                if format == 'html':

                    print("Fixing links to PDFs and EPUBs ... ") # Because of this crap: http://stackoverflow.com/a/23855541

                    with open(relout + '/home.html', "r+") as f:
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

                    replace_html('https://cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/', '_static/js/')
                    replace_html('https://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.10/', '_static/js/')
                    replace_html('https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML', '_static/js/MathJax.js')
                    replace_html('https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-AMS-MML_HTMLorMML',  '_static/js/MathJax.js')

                elif format == 'latex':                  
                    run('pdflatex *.tex', cwd=relout )
                    # running twice otherwise we get no TOC
                    run('pdflatex *.tex', cwd=relout )
                
                print_generated_banner(manual, format)                                                
                print("          "  + get_path(manual, format)  + "\n\n");
        
                built[(manual, format)] = {}

            except  subprocess.CalledProcessError as err:
                failed[(manual, format)] = {'err': err}
                print("ERROR: FAILED BUILDING " + manual + " " + format + ", SKIPPING IT !!")
                print(err.output)
    

    if len(built) > 0:
        print("\n\n  GENERATED MANUALS: \n\n")
        maxpad = 0
        for (manual, format) in sorted(built.keys()):
            maxpad = max(maxpad, len("      " + manual + " " + format + ":   "))
        for (manual, format) in sorted(built.keys()):
            print(("      " + manual + " " + format + ":   ").rjust(maxpad) + get_path(manual, format))
        print("")
        print("")
    if len(failed) > 0:
        print("\n\n   THERE WERE ERRORS WHILE BUILDING:\n\n")
        for (manual, format) in failed.keys():
            print("       " + manual + " " + format + ":   ")
            print("             " + str(failed[(manual, format)]['err']) + "   \n\n" )
        exit(1)
    

def wrongarg(msg):
    #print("    ERROR! " + msg)
    #print("")
    exit("\n\n    ERROR! " + msg + "\n\n\n    For more info run:   build.py help\n\n");



def replace_html(stext, rtext):
    """ Replaces strings in html files (useful for correcting links to cdn libs)
        stext: string to find
        rtext: string to replace with
    """

    path = "_build/html/*.html"

    info("finding: " + stext + " replacing with: " + rtext + " in: " + path)

    files = glob.glob(path)
    for line in fileinput.input(files,inplace=1):
        lineno = 0
        lineno = line.find(stext)
        if lineno >0:
            line =line.replace(stext, rtext)
        sys.stdout.write(line)

#  MAIN

manuals=MANUALS.keys()
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
        for format in formats:
            if not format in FORMATS:
                wrongarg("Expected format to be one of " + str(FORMATS) + " , found instead '" + format + "'");
        i += 2
    elif sys.argv[i] == '-q' or sys.argv[i] == '--quick':
        draft = True
        manuals=['student']
        formats=['html']
        i += 1
    else:
        wrongarg("Unrecognized parameter '" + sys.argv[i] + "'")
        i += 1

if system == None:
    system = detect_system()

run_sphinx(manuals, formats)

