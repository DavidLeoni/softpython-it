#!/usr/bin/python3

# David Leoni Sept 2017
# This script allows initialization and management of exams.

import conf
import sys
import os
import shutil
import datetime
import glob
import re
from arghandler import *


from conf import info
from conf import fatal
from conf import warn

def get_target_student(ld):
    return "private/" + ld + "-student-zip/" + conf.get_exam_student_folder(ld) + '/exams/' + ld 

def get_exam_text_filename(ld, extension):
    return 'exam-' + ld + '-text' + '.' + extension
    

def expand_JM(source, target, exam_date):
    d = conf.parse_date(exam_date)
    sourcef = open(source, "r")
    s = sourcef.read()
    s = s.replace('_JM_{exam.date}', exam_date )
    s = s.replace('_JM_{exam.date_human}', d.strftime('%A %d, %B %Y') )
    for k in conf.__dict__:
        s = s.replace('_JM_{conf.' + k + '}', str(conf.__dict__[k]))
    p = re.compile('_JM_\{[a-zA-Z][\w\.]*\}')
    if p.search(s):
        warn("FOUND _JM_ macros which couldn't be expanded!")
        print("               file: " + source)
        print("\n                 ".join(p.findall(s)))
        print("")
    destf = open(target, 'w')    
    destf.write(s)


cur_dir_names = os.listdir('.')    

if 'exam.py' not in cur_dir_names:
    fatal('You must execute exam.py from within the directory it is contained!')

def arg_date(parser, args):
    parser.add_argument('date', help="date in format 'yyyy-mm-dd'" )
    return conf.parse_date_str(vars(parser.parse_args(args))['date'])    
    
@subcmd(help="Initializes a new exam")
def init(parser,context,args):
        
    ld = arg_date(parser, args)
    eld_admin = "private/" + ld + "-admin"
    eld_solutions = "private/" + ld + "-solutions"
    pubeld = "exams/" + ld 
    exam_ipynb = eld_solutions + '/exam-' + ld + '.ipynb'

    if os.path.exists(eld_admin):
        fatal("PRIVATE EXAM ADMIN ALREADY EXISTS: " + eld_admin)

    if os.path.exists(eld_solutions):
        fatal("PRIVATE EXAM SOLUTIONS ALREADY EXISTS: " + eld_solutions)
        
    if os.path.exists(pubeld):
        fatal("PUBLIC EXAM ALREADY EXISTS: " + pubeld)

    shutil.copytree("jm-templates/exam-admin", eld_admin)
    shutil.copytree("jm-templates/exam-solutions", eld_solutions, ignore=shutil.ignore_patterns('exam-yyyy-mm-dd.ipynb'))
    
    expand_JM('jm-templates/exam-solutions/exam-yyyy-mm-dd.ipynb', exam_ipynb, ld)

    os.rename(eld_admin + "/" + "jupman-yyyy-mm-dd-grades.ods", eld_admin + "/" + conf.filename + "-" + ld + "-grades.ods")
    
    info("You can now edit Python solutions, tests, exercisesa and exam notebook here  : " )
    print()
    info("   " + eld_solutions)

    

                        
"""
jupman-2000-12-31-FIRSTNAME-LASTNAME-ID
    |-some files ...
    |-exams
        |-2000-12-31            
            |- exercise1.py
            |- exercise2.py
            |- exercise3.py  
"""
@subcmd(help='Zips a builded exam, making it ready for deploy on the exam server')
def package(parser,context,args):
    ld = arg_date(parser, args)
    eld_admin = "private/" + ld + '-admin'
    eld_solutions = 'private/' + ld + "-solutions"
    eld_notebook = eld_solutions + '/' + 'exam-' + ld + '.ipynb'
    target_student = get_target_student(ld)
    target_student_html = get_target_student(ld) + '/' + get_exam_text_filename(ld, 'html')
    # no pdf as hiding cells is too boring, have still 
    # to properly review cells filtering https://github.com/DavidLeoni/jupman/issues/4
    # target_student_pdf = target_student + '/' + 'exam-' + ld + '.pdf'
    target_student_zip = eld_admin +"/server/" + conf.filename + "-" + ld + "-exam" # without '.zip'
    target_server_zip = eld_admin +"/" + conf.filename + "-" + ld + "-server"    # without '.zip'

    built_site_dir = "_build/"

    if not os.path.exists(built_site_dir):
        fatal(built_site_dir + " WAS NOT BUILT !")

    if not os.path.exists(eld_solutions):
        fatal("MISSING SOURCE SOLUTION EXERCISES: " + eld_solutions)

    if os.path.exists(target_student):
        fatal("TARGET STUDENT EXERCISES DIRECTORY ALREADY EXISTS: " + target_student)


    try:
        dir_names = os.listdir(built_site_dir)    
    except Exception as e:        
        fatal("ERROR WITH DIR " + built_site_dir, ex=e)

    if len(dir_names) == 0:
        fatal("SITE DIRECTORY AT " + built_site_dir + " WAS NOT BUILT !")

    server_jupman = eld_admin + "/server/" + conf.filename

    if os.path.exists(server_jupman):
        info("Cleaning " + server_jupman + " ...")
        conf.delete_tree(server_jupman, "server/" + conf.filename)

    info("Copying built website ...")        
    shutil.copytree(built_site_dir, server_jupman)
    
    info("Building html ..")
    import nbformat
    import nbconvert
    from nbconvert import HTMLExporter
    
    html_exporter = HTMLExporter()    
    
    from nbconvert.preprocessors import ExecutePreprocessor
    with open(eld_notebook) as f:
        nb = nbformat.read(f, as_version=4)
        (body, resources) = html_exporter.from_notebook_node(nb)
        if not os.path.exists(target_student):
            os.makedirs(target_student)
        #ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        #ep.preprocess(nb, {'metadata': {'path': './'}})
        with open(target_student_html, 'wt') as html_f:
            #print("resources = %s" % resources)
            html_f.write(body)
            
            
    info("Copying exercises to " + str(target_student))
    conf.copy_code(eld_solutions, target_student)

    
    info("Creating student exercises zip:  " + target_student_zip + ".zip" )        
    
    def mysub(fname):
        if fname.startswith('private/'):                    
            return fname[len('private/YYYY-MM-DD-student-zip/'):]
        else:
            return '/' + conf.get_exam_student_folder(ld) + '/' + fname
            
    
    conf.zip_paths([target_student] + conf.exercise_common_files, target_student_zip,  mysub)
    #shutil.make_archive(target_student_zip, 'zip', target_student_zip)
    info("Creating server zip: " + target_server_zip + ".zip")            
    shutil.make_archive(target_server_zip, 'zip', eld_admin + "/server")
    print("")    
    info("You can now browse the website at:  " + os.path.abspath(eld_admin + "/server/" + conf.filename + "/html/index.html"))
    print("")

@subcmd(help='Set up grading for the provided exam')
def grade(parser,context,args):
    ld = arg_date(parser, args)
    eld_admin = "private/" + ld + "-admin"
    shipped = eld_admin + "/shipped"
    graded = eld_admin + "/graded"

    if not os.path.exists(shipped):
        fatal("Couldn't find directory: " + shipped)

    try:
        dir_names = next(os.walk(shipped))[1]
    except Exception as e:        
        info("\n\n    ERROR! " + repr(e) + "\n\n")
        exit(1)
    if len(dir_names) == 0:
        fatal("NOTHING TO GRADE IN " + shipped)
        
    for dn in dir_names:
        target = graded + "/" + dn
        
        if (os.path.exists(target + "/shipped")):
            fatal("DIRECTORY ALREADY EXISTS: " + target + "/shipped\n\n")
            
        if (os.path.exists(target + "/corrected")):
            fatal("DIRECTORY ALREADY EXISTS: " + target + "/corrected\n\n")

        info("Copying Python files to execute and eventually correct in " + target + "/corrected")
        shutil.copytree(eld_admin + "/shipped/" + dn , target + "/shipped")        
        info("Copying original shipped files (don't touch them!) in " + target + "/shipped")
        shutil.copytree(eld_admin + "/shipped/" + dn , target + "/corrected")
    

@subcmd('zip-grades', help='Creates a separate zip for each student containing his graded sheet and code')
def zip_grades(parser,context,args):
    ld = arg_date(parser, args)
    eld_admin = "private/" + ld + '-admin'
    shipped = eld_admin + "/shipped"
    graded =  eld_admin + "/graded"
    try:
        
        dir_names = next(os.walk(shipped))[1]
    except Exception as e:        
        info("\n\n    ERROR! " + repr(e) + "\n\n")
        exit(1)
    if len(dir_names) == 0:
        info("\n\n  ERROR! NOTHING TO ZIP!\n\n")
    for dn in dir_names:
        target = eld_admin + "/graded/" + dn
        shutil.make_archive(target, 'zip', target)
    print("")
    info("You can now find zips to send to students in " + eld_admin + "/graded")
    print("")

@subcmd('publish', help='Copies exam python files from private/ to exam/ (both exercises and solutions), and zips them')
def publish(parser,context,args):
    ld = arg_date(parser, args)
    source = "private/" + ld  
    source_admin = source + '-admin'
    source_solutions = source +  '-solutions' 
    source_ipynb = source + '-solutions/exam-' + ld + '.ipynb'
    student_html = get_target_student(ld) + '/' + get_exam_text_filename(ld, 'html')
    
    
    if not os.path.isdir(source_admin):
        fatal("SOURCE PRIVATE EXAM FOLDER " + source_admin + " DOES NOT EXISTS !")
    if not os.path.isdir(source_solutions):
        fatal("SOURCE PRIVATE EXAM FOLDER " + source_solutions + " DOES NOT EXISTS !")

    dest = "exams/" + ld + "/"
    dest_zip = "overlay/_static/" + conf.filename + '-'+ld + '-exam'  

    if os.path.exists(dest):
        fatal("TARGET PUBLIC EXAM FOLDER " + dest + " ALREADY EXISTS !")
    if os.path.exists(dest_zip):
        fatal("TARGET PUBLIC EXAM ZIP " + dest_zip + ".zip ALREADY EXISTS !")    

    info("Copying solutions to " + str(dest))
    conf.copy_code(source_solutions, dest, copy_solutions=True)
    info("Copying exam HTML text")
    shutil.copyfile(student_html, dest + '/' + get_exam_text_filename(ld, 'html'))
    
    info()
    info("Exam python files copied.")
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
    eld_admin = "private/" + ld + '-admin'
    eld_solutions = "private/" + ld + '-solutions'
    eld_student_zip = "private/" + ld + '-student-zip' 
    
    pubeld = "exams/" + ld 
    pubeldzip = "overlay/_static/" + conf.filename + "-" + ld + "-exam.zip" 

    deleted = []

    ans = ''
    while ans != 'Y' and ans != 'n':  
        print ("DO YOU *REALLY* WANT TO DELETE EXAM " + ld + " (NOTE: CANNOT BE UNDONE) [Y/n]? "),
        ans = input()

    if ans != 'Y':
        print("")
        info("User cancelled, no data was deleted.")
        return

    print("")
    
    def delete_stuff(path, confirm_path):
        
        if os.path.exists(path):
            info("Deleting " + path + " ...")
            if os.path.isfile(path): 
                conf.delete_file(path, confirm_path)
            elif os.path.isdir(path):
                conf.delete_tree(path, confirm_path)
            else:
                raise Exception("File is neither a directory nor a file: %s" % path)
            deleted.append(path)
            
    delete_stuff(eld_admin, "private/" + ld + '-admin')
    delete_stuff(eld_solutions, "private/" + ld + '-solutions')
    delete_stuff(eld_student_zip, "private/" + ld + '-student-zip')
    delete_stuff(pubeld, "exams/" + ld)
    delete_stuff(pubeldzip, "overlay/_static/" + conf.filename + "-" + ld + "-exam.zip" )

    if len(deleted) == 0:
        fatal("COULDN'T FIND ANY EXAM FILE TO DELETE FOR DATE: " + ld)

handler = ArgumentHandler(description='Manages ' + conf.filename + ' exams.',
                         use_subcommand_help=True)
handler.run()

print("")
info("DONE.\n")




