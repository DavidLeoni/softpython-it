#!/usr/bin/python3

# This script allows initialization and management of exams.

__author__ = "David Leoni"
__status__ = "Development"

import conf
import sys
import os
import shutil
import datetime
import glob
import re
import arghandler
from arghandler import ArgumentHandler
from arghandler import subcmd

import jupman_tools as jmt

from jupman_tools import info
from jupman_tools import fatal
from jupman_tools import warn

jm = conf.jm

def get_target_student(ld):
    return '_private/%s/student-zip/%s/'  % (ld, jm.get_exam_student_folder(ld))

def get_exam_text_filename(ld, extension):
    return 'exam-%s.%s' % (ld, extension)
    
cur_dir_names = os.listdir('.')    

if 'exam.py' not in cur_dir_names:
    fatal('You must execute exam.py from within the directory it is contained!')

def arg_date(parser, args):
    parser.add_argument('date', help="date in format 'yyyy-mm-dd'" )
    return jmt.parse_date_str(vars(parser.parse_args(args))['date'])    
    
@subcmd(help="Initializes a new exam")
def init(parser, context,args):
    
    parser.add_argument('date', help="date in format 'yyyy-mm-dd'" )
    #TODO parser.add_argument('--edit-notebook-mode')
    ld = jmt.parse_date_str(vars(parser.parse_args(args))['date'])    

    eld_admin = "_private/" + ld
    eld_solutions = "_private/%s/solutions" % ld
    pubeld = "exams/%s" % ld 
    exam_ipynb = '%s/exam-%s.ipynb' % (eld_solutions, ld)

    if os.path.exists(eld_admin):
        fatal("PRIVATE EXAM ADMIN ALREADY EXISTS: " + eld_admin)

    if os.path.exists(eld_solutions):
        fatal("PRIVATE EXAM SOLUTIONS ALREADY EXISTS: " + eld_solutions)
        
    if os.path.exists(pubeld):
        fatal("PUBLIC EXAM ALREADY EXISTS: " + pubeld)

    
    shutil.copytree("_templates/exam", 
                    eld_admin,
                    ignore=shutil.ignore_patterns('exam-yyyy-mm-dd.ipynb'))
    
    jmt.expand_JM(   '_templates/exam/solutions/exam-yyyy-mm-dd.ipynb', 
                    exam_ipynb,
                    ld,
                    conf)

    os.rename('%s/jupman-yyyy-mm-dd-grades.ods' % eld_admin,
              "%s/%s-%s-grades.ods" % (eld_admin, conf.jm.filename, ld))
    
    info()
    info("You can now edit Python solutions, tests, exercises and exam notebook here  : " )
    print()
    info("   " + eld_solutions)


                        
"""
jupman-2000-12-31-FIRSTNAME-LASTNAME-ID
    exams
       2000-12-31            
          exercise1.py
          exercise2.py
          exercise3.py  
"""
@subcmd(help='Zips a builded exam, making it ready for deploy on the exam server')
def package(parser,context,args):
    ld = arg_date(parser, args)
    eld_admin = '_private/' + ld 
    eld_solutions = '_private/%s/solutions' % ld
    eld_notebook = '%s/exam-%s.ipynb' % (eld_solutions, ld)
    target_student = get_target_student(ld)
    target_student_pdf = '%s/%s' % (get_target_student(ld), get_exam_text_filename(ld, 'pdf'))
    # no pdf as hiding cells is too boring, have still 
    # to properly review cells filtering https://github.com/DavidLeoni/jupman/issues/4
    # target_student_pdf = target_student + '/' + 'exam-' + ld + '.pdf'
    target_student_zip = "%s/server/%s-%s-exam" % (eld_admin,jm.filename,ld) # without '.zip'
    target_server_zip = "%s/%s-%s-server" % (eld_admin, jm.filename,ld) # without '.zip'

    

    if not os.path.exists(jm.build):
        fatal("%s WAS NOT BUILT !" % jm.build)

    if not os.path.exists(eld_solutions):
        fatal("MISSING SOURCE SOLUTION EXERCISES: " + eld_solutions)

    if os.path.exists(target_student):
        fatal("TARGET STUDENT EXERCISES DIRECTORY ALREADY EXISTS: " + target_student)


    try:
        dir_names = os.listdir(jm.build)    
    except Exception as e:        
        fatal("ERROR WITH DIR %s" % jm.build, ex=e)

    if len(dir_names) == 0:
        fatal("SITE DIRECTORY AT %s WAS NOT BUILT !" % jm.build)

    server_jupman = "%s/server/%s" % (eld_admin, jm.filename)

    if os.path.exists(server_jupman):
        jmt.delete_tree(server_jupman, "_private/%s/server" % ld)

    info("Copying built website ...")        
    shutil.copytree(jm.build, server_jupman)
    
    info("Building pdf ..")
    import nbformat
    import nbconvert
    from nbconvert import PDFExporter
    
    pdf_exporter = PDFExporter()    
    
    #Dav dic 2019:  couldn't make it work, keeps complaining about missing files
    #pdf_exporter.template_file = '_templates/classic.tplx
    # as a result we have stupid extra date and worse extra numbering in headers


    from nbconvert.preprocessors import ExecutePreprocessor
    with open(eld_notebook) as f:
        nb = nbformat.read(f, as_version=4)
        old_title = jmt._replace_title(nb, 
                                       eld_notebook, 
                                       "").strip('#')
        
        nb.cells = [cell for cell in nb.cells \
                             if not ('nbsphinx' in cell.metadata \
                                     and cell.metadata['nbsphinx'] == 'hidden')]

        (body, resources) = pdf_exporter.from_notebook_node(nb,
                                            resources={'metadata': {'name': old_title}})

        
        if not os.path.exists(target_student):
            os.makedirs(target_student)
        #ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        #ep.preprocess(nb, {'metadata': {'path': './'}})
        with open(target_student_pdf, 'wb') as pdf_f:
            #print("resources = %s" % resources)
            pdf_f.write(body)
            
            
    info("Copying exercises to " + str(target_student))
    jm.copy_code(eld_solutions, target_student, copy_solutions=False)

    
    info("Creating student exercises zip:  %s.zip" % target_student_zip)
    
    def mysub(fname):
        if fname.startswith('_private/'):
            return fname[len('_private/YYYY-MM-DD/student-zip/'):]
        else:
            return '/%s/%s' % (jm.get_exam_student_folder(ld), fname)
            
    
    jm.zip_paths([target_student] + jm.chapter_files,
                  target_student_zip,  
                  mysub)
    #shutil.make_archive(target_student_zip, 'zip', target_student_zip)
    info("Creating server zip: %s.zip" % target_server_zip )
    shutil.make_archive(target_server_zip, 'zip', eld_admin + "/server")
    print("")    
    info("You can now browse the website at:  %s" % (os.path.abspath(eld_admin + "/server/" + jm.filename + "/html/index.html")))
    print("")

@subcmd(help='Set up grading for the provided exam')
def grade(parser,context,args):
    ld = arg_date(parser, args)
    eld_admin = "_private/%s" % ld
    shipped = "%s/shipped" % eld_admin
    graded = "%s/graded" % eld_admin

    if not os.path.exists(shipped):
        fatal("Couldn't find directory: " + shipped)

    try:
        dir_names = next(os.walk(shipped))[1]
    except Exception as e:        
        info("\n\n    ERROR! %s\n\n" % repr(e))
        exit(1)
    if len(dir_names) == 0:
        fatal("NOTHING TO GRADE IN %s" % shipped)
        
    for dn in dir_names:
        target = "%s/%s" % (graded, dn)
        
        if (os.path.exists("%s/shipped" % target)):
            fatal("DIRECTORY ALREADY EXISTS: %s/shipped\n\n" % target)
            
        if (os.path.exists("%s/graded" % target)):
            fatal("DIRECTORY ALREADY EXISTS: %s/graded\n\n" % target)

        info("Copying Python files to execute and eventually grade in %s/graded" % target)
        shutil.copytree('%s/shipped/%s' % (eld_admin, dn) , '%s/shipped' % target)
        info("Copying original shipped files (don't touch them!) in %s/shipped" % target)
        shutil.copytree('%s/shipped/%s' % (eld_admin, dn) , '%s/graded' % target)
    

@subcmd('zip-grades', help='Creates a separate zip for each student containing his graded sheet and code')
def zip_grades(parser,context,args):
    ld = arg_date(parser, args)
    eld_admin = "_private/" + ld 
    shipped = eld_admin + "/shipped"

    try:
        
        dir_names = next(os.walk(shipped))[1]
    except Exception as e:        
        info("\n\n    ERROR! " + repr(e) + "\n\n")
        exit(1)
    if len(dir_names) == 0:
        info("\n\n  ERROR! NOTHING TO ZIP!\n\n")
    for dn in dir_names:
        target = "%s/graded/%s" % (eld_admin, dn)
        shutil.make_archive(target, 'zip', target)
    print("")
    info("You can now find zips to send to students in %s/graded" % eld_admin)
    print("")

@subcmd('publish', help='Copies exam python files from private/ to exam/ (both exercises and solutions), and zips them')
def publish(parser,context,args):
    ld = arg_date(parser, args)
    source = "_private/%s" % ld  
    source_admin = source
    source_solutions =  '%s/solutions' % source
    student_pdf = get_target_student(ld) + '/' + get_exam_text_filename(ld, 'pdf')
    
    
    if not os.path.isdir(source_admin):
        fatal("SOURCE PRIVATE EXAM FOLDER %s DOES NOT EXISTS !" % source_admin)
    if not os.path.isdir(source_solutions):
        fatal("SOURCE PRIVATE EXAM FOLDER %s DOES NOT EXISTS !" % source_solutions)

    dest = 'exams/%s/solutions' % ld
    dest_zip = '_static/generated/%s-%s-exam'  % (jm.filename, ld)

    if os.path.exists(dest):
        fatal("TARGET PUBLIC EXAM FOLDER %s ALREADY EXISTS !" % dest)
    if os.path.exists(dest_zip):
        fatal("TARGET PUBLIC EXAM ZIP %s.zip ALREADY EXISTS !" % dest_zip)    

    info("Copying solutions to %s" % dest)
    shutil.copytree(source_solutions, dest)

    info("Copying exam PDF text")
    shutil.copyfile(student_pdf, '%s/%s' % (dest, get_exam_text_filename(ld, 'pdf')))
    
    info()
    info("Exam Python files copied.")
    info()
    info("You can now manually build and run the following git instructions to publish the exam.")
    
    info("  ./build.py")
    info("  git status  # just to check everything is ok")
    info("  git add .")
    info("  git commit -m 'published " + ld + " exam'")
    info("  git push")
    info()

        
@subcmd('delete', help="Deletes an existing exam")
def delete_exam(parser,context,args):
        
    ld = arg_date(parser, args)
    eld_admin = '_private/%s' % ld
    
    pubeld = 'exams/%s' % ld
    pubeldzip = '_static/generated/%s-%s-exam.zip' % (jm.filename, ld)

    deleted = []

    ans = ''
    while ans != 'Y' and ans != 'n':  
        print ('DO YOU *REALLY* WANT TO DELETE EXAM %s (NOTE: CANNOT BE UNDONE) [Y/n]? ' % ld),
        ans = input()

    if ans != 'Y':
        print("")
        info("User cancelled, no data was deleted.")
        return

    print("")
    
    def delete_stuff(path, confirm_path):
        """ Deletes path and logs deleted stuff 
        """
        if os.path.exists(path):
            if os.path.isfile(path): 
                jmt.delete_file(path, confirm_path)
            elif os.path.isdir(path):
                jmt.delete_tree(path, confirm_path)
            else:
                raise Exception("File is neither a directory nor a file: %s" % path)
            deleted.append(path)
            
    delete_stuff(eld_admin, "_private/%s" % ld)
    delete_stuff(pubeld, "exams/%s" % ld)
    delete_stuff(pubeldzip, '_static/generated/%s-%s-exam.zip' % (jm.filename, ld))

    if len(deleted) == 0:
        fatal("COULDN'T FIND ANY EXAM FILE TO DELETE FOR DATE: " + ld)

handler = ArgumentHandler(description='Manages ' + jm.filename + ' exams.',
                         use_subcommand_help=True)
handler.run()

print("")
info("DONE.\n")




