#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Builds documentation for Soft Python Course: https://github.com/DavidLeoni/softpython

# For more info, see help() function

# 0.1  August 2017  David Leoni

import subprocess
import os
import sys
import inspect
import re
from conf import *
from build_common import *


def help():

    print("")
    print("  FOR COMPLETE EXPLANATION OF DOCS SYSTEM, SEE TODO")
    print("")
    print("  From the root of your project, run :")
    print("")
    print("      ./build.py")
    print("")
    print("")
    print("    OPTIONS")
    print("")
    print("        --quick   -q     Quick build that just generates student manual, only in html format")
    print("")
    print("        --system   -s    " + ' | '.join(SYSTEMS)) + "     if omitted will be autodetected."
    print("")
    print("        --manuals  -m    " + ' | '.join(MANUALS) + "  separate with comma to build more than one")
    print("")
    print("        --formats  -f    " + ' | '.join(FORMATS) + "       separate with comma to build more than one")
    print("")
    print("    EXAMPLE USAGE:")
    print("")
    print("        python3 build.py  -m student,instructor  -f html,epub,pdf")
    print("")

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

def run_sphinx(manuals, formats):
    built = {}
    failed = {}

    for manual in manuals: 
        for format in formats:

            tinfo = MANUALS[manual]

            assembly = detect_assembly(system)

            relout = outdir(manual, format)
            print("Building " + tinfo['name'] + " "  + format +  " in " + relout)

            # sphinx-build -b  html doc _build/student/html 


            new_python_path = None

            if 'PYTHONPATH' in os.environ:
                new_python_path = os.environ['PYTHONPATH'] + os.pathsep + super_doc_dir()
            else:
                new_python_path = super_doc_dir()
            my_env = os.environ.copy()
            my_env['PYTHONPATH'] = new_python_path

            try:
                print("Cleaning " + str(relout) + "  ")
                
                if "_build/" in relout:
                    res = subprocess.check_output("rm -rf " + relout,
                                                   shell=True,
                                                   env=my_env
                                                  )
                else:
                    raise Exception("ERROR: FAILED SECURITY CHECK BEFORE CLEANING DIRECTORY: " + str(relout))
                    
                cmd = ("sphinx-build -b " + format + " " + ("." if assembly else ".") + " " + relout
                      + " " + tinfo['args'] + " -t " + system
                      + (" -t assembly " if assembly else ""))
                print("")
                print("  " + cmd)
                print("")
                res = subprocess.check_output(cmd,
                                               shell=True,
                                               env=my_env
                                              )
                print(res)

                if format == 'html':

                    print("Fixing links to PDFs and EPUBs ... ") # Because of this crap: http://stackoverflow.com/a/23855541

                    with open(relout + '/index.html', "r+") as f:
                        data = f.read()

                        if "pdf" in formats or "epub" in formats:
                            data = data.replace('${download}', 'Download ')
                            print('Creating symlinks for PDFs and EPUBs ...')
                            if 'pdf' in formats:
                                os.symlink( '../pdf', relout + '/pdf')
                            if 'epub' in formats:
                                os.symlink( '../epub', relout + '/epub')
                        else:
                            data = data.replace('${download}', '')

                        print(formats)
                        if 'pdf' in formats:
                            data = data.replace('${pdf}', '&ensp;<a target="_blank" href="pdf/' + manual + '-manual.pdf">PDF</a>')
                        else:
                            
                            data = data.replace('${pdf}', '')

                        if 'epub' in formats:
                            data = data.replace('${epub}', '&ensp;<a target="_blank" href="epub/' + manual + '-manual.epub">EPUB</a>')
                        else:
                          data = data.replace('${epub}', '')


                        print("Putting code documentation links ...")

                        try:
                            h1 = 'href="#internals" title="Permalink to this headline">¶</a></h1>'

                            if system == 'kos':

                                data = data.replace(h1,
                                                    h1 + ' &emsp; &ensp; <a href="jsdoc/index.html" target="_blank">JSDOC</a> <br/>' \
                                                    '&emsp; &ensp; &ensp;<a href="codo/index.html" target="_blank">CoffeeScript</a><br>')
                            elif system == 'sweb':
                                data = data.replace(h1,
                                                    h1 + ' &ensp;  &ensp;  <a href="apidocs/index.html" target="_blank">Javadoc</a> <br>')
                        except Exception as inst:
                            print('\n\nERROR: GOT AN EXCEPTION WHILE PUTTING CODE DOCUMENTATION LINKS: \n' + str(inst))

                        try:
                            regex = '(<li class="toctree-l1"><a class="reference internal" href="(.*)/doc/(.*)/index.html">)(.*)</a><ul>'

                            p = re.compile(regex)
                            for m in p.finditer(data):
                                print(m.start(), m.group())

                            def repl(m):
                                # print("***** MATCHOBJ.group() = \n" + str(m.groups()).replace(',','\n'))
                                mantype = m.group(3)

                                app_path = m.group(2)
                                docpath = '../../all/' + app_path + '/doc/' + mantype + '/'
                                if system == 'kos':
                                    list_items = '\n<li><a href="' + docpath + 'jsdoc/index.html" target="_blank">JSDOC</a></li>\n' \
                                                  '<li><a href="'+ docpath + 'codo/index.html" target="_blank">CoffeeScript</a></li>\n'
                                elif system == 'sweb':
                                    list_items = '\n<li><a href="' + docpath + 'apidocs/index.html" target="_blank">Javadoc</a></li>\n'
                                else:
                                    list_items = ''
                                return m.group(1) + app_path + ' ' + MANUALS[mantype]['name']  + '</a><ul>' + list_items

                            
                            data = re.sub(regex, repl, data)
                        except Exception as inst:
                            print('\n\nERROR: GOT AN EXCEPTION WHILE PUTTING CODE DOCUMENTATION LINKS: \n' + str(inst))

                        f.seek(0)
                        f.write(data)

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

#  MAIN

manuals=MANUALS.keys()
formats = ['pdf', 'epub', 'html']
system = None
draft = False

if len(sys.argv) == 2 and (sys.argv[1] == 'help' or sys.argv[1] == '--help' or sys.argv[1] == '-h'):
    help()
    exit()

i = 1
while i < len(sys.argv):
    if sys.argv[i] == '-s' or sys.argv[i] == '--system':
        if i + 1 == len(sys.argv):
          wrongarg("Missing parameter !")
        system = sys.argv[i+1]
        if not system in SYSTEMS.keys():
            wrongarg("Expected system to be one of " + str(SYSTEM.keys()) + " , found instead '" + system  + "'")
        i += 2
    elif sys.argv[i] == '-m' or sys.argv[i] == '--manuals':
        if i + 1 == len(sys.argv):
            wrongarg("Missing parameter !")
        manuals = sys.argv[i+1].split(",")
        for manual in manuals:
            if not manual in MANUALS:
                wrongarg("Expected manual to be one of " + str(MANUALS.keys()) + " , found instead '" + manual  + "'")
        i += 2
    elif sys.argv[i] == '-f'  or sys.argv[i] == '--formats':
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

