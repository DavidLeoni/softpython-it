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

def fatal(msg, ex=None):
    if ex == None:
        exMsg = ""
    else:
        exMsg = " \n  " + repr(ex)
    info("\n\n    ERROR! " + str(msg) + exMsg + "\n\n")
    exit(1)
    
def info(msg=""):
    print("  " + str(msg))

def warn(msg):
    print("\n\n   WARNING: " + str(msg))


def expand_JM(source, target, exam_date):
    d = conf.parse_date(exam_date)
    sourcef = open(source, "r")
    s = sourcef.read()
    s = s.replace('_JM_(exam.date)', exam_date )
    s = s.replace('_JM_(exam.date_human)', d.strftime('%A %d, %B %Y') )
    for k in conf.__dict__:
        s = s.replace('_JM_(conf.' + k + ')', str(conf.__dict__[k]))
    p = re.compile('_JM_\([a-zA-Z][\w\.]*\)')
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
    eld = "private/" + ld
    pubeld = "past-exams/" + ld 
    exam_ipynb = eld + '/exam-' + ld + '.ipynb'
    
    if os.path.exists(eld):
        fatal("PRIVATE EXAM ALREADY EXISTS: " + eld)

    if os.path.exists(pubeld):
        fatal("PUBLIC EXAM ALREADY EXISTS: " + pubeld)

    if os.path.exists(exam_ipynb):
        fatal("PUBLIC EXAM ALREADY EXISTS: " +  exam_ipynb)

    shutil.copytree("templates/exam", eld)
    expand_JM('templates/exam/exam-yyyy-mm-dd.ipynb', exam_ipynb, ld)

    os.rename(eld + "/" + "jupman-yyyy-mm-dd-grades.ods", eld + "/" + conf.filename + "-" + ld + "-grades.ods")
    
    info("Following material is now ready to edit: ")
    print("")
    info('   Python exercises and tests : ' + eld + "/exercises")
    info('   Python solutions           : ' + eld + "/solutions" )

    info('   Exam notebook              : ' + exam_ipynb)

@subcmd(help='Zips a builded exam, making it ready for deploy on the exam server')
def package(parser,context,args):
    ld = arg_date(parser, args)
    eld = "private/" + ld
    source_student = eld + "/exercises"
    target_student = eld + "/server/" + conf.filename + "-" + ld + "/FIRSTNAME-LASTNAME-ID"
    target_student_zip = eld +"/server/" + conf.filename + "-" + ld

    built_site_dir = "_build/"

    if not os.path.exists(built_site_dir):
        fatal(built_site_dir + " WAS NOT BUILT !")

    if not os.path.exists(source_student):
        fatal("MISSING SOURCE STUDENT EXERCISES: " + source_student)

    if os.path.exists(target_student):
        fatal("TARGET STUDENT EXERCISES DIRECTORY ALREADY EXISTS: " + target_student)


    try:
        dir_names = os.listdir(built_site_dir)    
    except Exception as e:        
        fatal("ERROR WITH DIR " + built_site_dir, ex=e)

    if len(dir_names) == 0:
        fatal("SITE DIRECTORY AT " + built_site_dir + " WAS NOT BUILT !")

    server_jupman = eld + "/server/" + conf.filename

    if os.path.exists(server_jupman):
        info("Cleaning " + server_jupman + " ...")
        delete_tree(server_jupman, "server/" + conf.filename)

    info("Copying built website ...")        
    shutil.copytree(built_site_dir, server_jupman)
    
    info("Copying exercises to " + str(target_student))
    shutil.copytree(source_student, target_student)            
    info("Creating student exercises zip:  " + target_student_zip + ".zip" )        
    shutil.make_archive(target_student_zip, 'zip', target_student_zip)
    target_server_zip = eld +"/" + conf.filename + "-" + ld + "-server"    # without '.zip'
    info("Creating server zip: " + target_server_zip + ".zip")            
    shutil.make_archive(target_server_zip, 'zip', eld + "/server")
    print("")    
    info("You can now browse the website at:  " + os.path.abspath(eld + "/server/" + conf.filename + "/html/index.html"))
    print("")

@subcmd(help='Set up grading for the provided exam')
def grade(parser,context,args):
    ld = arg_date(parser, args)
    eld = "private/" + ld
    shipped = eld + "/shipped"
    graded = eld + "/graded"

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
        shutil.copytree(eld + "/shipped/" + dn , target + "/shipped")        
        info("Copying original shipped files (don't touch them!) in " + target + "/shipped")
        shutil.copytree(eld + "/shipped/" + dn , target + "/corrected")
    

@subcmd('zip-grades', help='Creates a separate zip for each student containing his graded sheet and code')
def zip_grades(parser,context,args):
    ld = arg_date(parser, args)
    eld = "private/" + ld
    shipped = eld + "/shipped"
    graded =  eld + "/graded"
    try:
        
        dir_names = next(os.walk(shipped))[1]
    except Exception as e:        
        info("\n\n    ERROR! " + repr(e) + "\n\n")
        exit(1)
    if len(dir_names) == 0:
        info("\n\n  ERROR! NOTHING TO ZIP!\n\n")
    for dn in dir_names:
        target = eld + "/graded/" + dn
        shutil.make_archive(target, 'zip', target)
    print("")
    info("You can now find zips to send to students in " + eld + "/graded")
    print("")

@subcmd('publish', help='Copies exam python files from private/ to exam/ (both exercises and solutions), and zips them')
def publish(parser,context,args):
    ld = arg_date(parser, args)
    source = "private/" + ld + "/"
    source_exercises = source  + 'exercises' 
    source_solutions = source +  'solutions' 
    source_ipynb = source + 'exam-' + ld + '.ipynb'

    if not os.path.isdir(source):
        fatal("SOURCE PRIVATE EXAM FOLDER " + source + " DOES NOT EXISTS !")
    if not os.path.isdir(source_exercises):
        fatal("SOURCE PRIVATE EXAM FOLDER " + source_exercises + " DOES NOT EXISTS !")
    if not os.path.isdir(source_solutions):
        fatal("SOURCE PRIVATE EXAM FOLDER " + source_solutions + " DOES NOT EXISTS !")

    dest = "past-exams/" + ld + "/"
    dest_zip = "past-exams/" + ld  
    dest_exercises = dest + "exercises"
    dest_solutions = dest + "solutions"
    dest_ipynb = dest + 'exam-' + ld + '.ipynb' 

    if os.path.exists(dest):
        fatal("TARGET PUBLIC EXAM FOLDER " + dest + " ALREADY EXISTS !")
    if os.path.exists(dest_zip):
        fatal("TARGET PUBLIC EXAM ZIP " + dest_zip + ".zip ALREADY EXISTS !")    
    if os.path.exists(dest_exercises):
        fatal("TARGET PUBLIC EXAM FOLDER " + dest_exercises + " ALREADY EXISTS !")
    if os.path.exists(dest_solutions):
        fatal("TARGET PUBLIC EXAM FOLDER " + dest_solutions + " ALREADY EXISTS !")

    info("Copying exercises to " + str(dest_exercises))
    shutil.copytree(source_exercises, dest_exercises)
    info("Copying solutions to " + str(dest_solutions))
    shutil.copytree(source_solutions, dest_solutions)
    info('Copying notebook to ' + str(dest_ipynb))
    shutil.copy(source_ipynb, dest_ipynb)
    info("Creating zip " + dest_zip + '.zip')
    shutil.make_archive(dest_zip, 'zip', dest)

    info()
    info("Exam python files copied.")
    info()
    info("You can now manually run the following git instructions to publish the exam,")
    info("ReadTheDocs will automatically build the website.")
    info()
    info("  git status  # just to check everything is ok")
    info("  git add .")
    info("  git commit -m 'published " + ld + " exam'")
    info("  git push")
    info()

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

    if path.endswith(path_check):
        shutil.rmtree(path)
    else:
        fatal("FAILED SAFETY CHECK FOR DELETING DIRECTORY " + path + " ! \n REASON: PATH DOES NOT END IN " + path_check)

@subcmd('delete', help="Deletes an existing exam")
def delete_exam(parser,context,args):
        
    ld = arg_date(parser, args)
    eld = "private/" + ld
    pubeld = "past-exams/" + ld 
    pubeldzip = pubeld + ".zip" 

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
    if os.path.exists(eld):
        info("Deleting " + eld + " ...")
        delete_tree(eld, "private/" + ld)
        deleted.append(eld)
    if os.path.exists(pubeld):
        info("Deleting " + pubeld + " ...")
        delete_tree(pubeld, "past-exams/" + ld)
        deleted.append(pubeld)
    if os.path.exists(pubeldzip):
        info("Deleting " + pubeldzip + " ...")
        delete_file(pubeldzip, "past-exams/" + ld + ".zip")
        deleted.append(pubeldzip)

    if len(deleted) == 0:
        fatal("COULDN'T FIND ANY EXAM FILE TO DELETE FOR DATE: " + ld)

handler = ArgumentHandler(description='Manages ' + conf.filename + ' exams.',
                         use_subcommand_help=True)
handler.run()

print("")
info("DONE.\n")




