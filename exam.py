#!/usr/bin/python

# David Leoni Sept 2017
# This script allows initialization and management of exams.

print(  "\n###############  JUPMAN EXAM MANAGER   #################\n")

import conf
import sys
import os
import shutil
import datetime
from arghandler import *


def _JM_(key, exam_date):
    if key == None:
        raise Exception("Found key equal to None !")
    if len(key) == 0:
        raise Exception("Found empty key !")
    if key == 'exam.date':
        return exam_date
    if key.startswith('conf.'):
        return getattr(conf, key.substr(len('conf.')))
    raise Exception("Unrecognized key: '" + key + "'")

def expand_JM(source, target, exam_date):
    sourcef = open(source, "r")
    s = f.read()
    s = s.replace('_JM_(exam.date)', exam_date )
    for k in conf.__dict__:
        s = s.replace('_JM_(conf.' + k + ')', conf.__dict__[k])
    destf = open(target, 'w')
    destf.write(s)

def fatal(msg, ex=None):
    if ex == None:
        exMsg = ""
    else:
        exMsg = " \n  " + repr(ex)
    info("\n\n    ERROR! " + str(msg) + exMsg + "\n\n")
    exit(1)
    
def info(msg):
    print("  " + str(msg))

cur_dir_names = os.listdir('.')    

if 'exam.py' not in cur_dir_names:
    fatal('You must execute exam.py from within the directory it is contained!')

def parse_date(ld):
    try:
        return str(datetime.datetime.strptime( str(ld), "%Y-%m-%d")).replace(' 00:00:00','')
    except:
        info("\n\nERROR! NEED FORMAT 'yyyy-mm-dd', GOT INSTEAD: '" + str(ld) + "'\n\n")
        exit(1)

def arg_date(parser, args):
    parser.add_argument('date', help="date in format 'yyyy-mm-dd'" )
    return parse_date(vars(parser.parse_args(args))['date'])    
    

@subcmd(help="Initializes a new exam")
def init(parser,context,args):
    ld = arg_date(parser, args)
    eld = "private/exams/" + ld
    pubeld = "exams/" + ld 
    exam_ipynb = 'exam-' + ld + '.ipynb'

    if os.path.exists(eld):
        fatal("PRIVATE EXAM " + eld + " ALREADY EXISTS !")

    if os.path.exists(pubeld):
        fatal("PUBLIC EXAM " + pubeld + " ALREADY EXISTS !")

    if os.path.exists(exam_ipynb):
        fatal("PUBLIC EXAM " + exam_ipynb + " ALREADY EXISTS !")

    shutil.copytree("templates/exam", eld)
    expand_JM('templates/exam-yyyy-mm-dd.ipynb', exam_ipynb)

    os.rename(eld + "/" + "jupman-yyyy-mm-dd-grades.ods", eld + "/" + conf.filename + "-" + ld + "-grades.ods")
    os.rename(eld + "/" + "jupman-yyyy-mm-dd", eld + "/" + conf.filename  + "-" + ld)

    shutil.copytree("templates/exam", pubeld)  
    os.rename(pubeld + "/" + "yyyy-mm-dd", pubeld + "/" + ld)


@subcmd(help='Zips a builded exam, making it ready for deploy on the exam server')
def package(parser,context,args):
    ld = arg_date(parser, args)
    eld = "private/exams/" + ld
    
    built_site_dir = "_build/"

    if not os.path.exists(built_site_dir):
        fatal(built_site_dir + " WAS NOT BUILT !")

    try:
        dir_names = os.listdir(built_site_dir)    
    except Exception, e:        
        fatal("ERROR WITH DIR " + built_site_dir, ex=e)

    if len(dir_names) == 0:
        fatal("SITE DIRECTORY AT " + built_site_dir + " WAS NOT BUILT !")

    server_algolab = eld + "/server/" + conf.filename
    if os.path.exists(server_algolab):
        if server_algolab.endswith("server/" + conf.filename):
            info("Cleaning " + server_algolab + " ...")
            shutil.rmtree(server_algolab)        
        else:
            fatal("Failed security check before deleting target " + str(server_algolab)) 

    info("Copying built website ...")        
    shutil.copytree(built_site_dir, server_algolab)            
    target_student_zip = eld +"/server/" + conf.filename + "-" + ld
    info("Creating student exercises zip:  " + target_student_zip + ".zip" )        
    shutil.make_archive(target_student_zip, 'zip', ld + "/" + conf.filename + "-" + ld)
    target_server_zip = eld +"/" + conf.filename + "-" + ld + "-server"    # without '.zip'
    info("Creating server zip: " + target_server_zip + ".zip")            
    shutil.make_archive(target_server_zip, 'zip', "exams/" + ld + "/server")
    print("")    
    info("You can now browse the website at:  " + os.path.abspath(eld + "/server/algolab/index.html"))
    print("")

@subcmd(help='Set up grading for the provided exam')
def grade(parser,context,args):
    ld = arg_date(parser, args)
    eld = "private/exams/" + ld

    try:
        dir_names = os.listdir(ld + "/shipped")
    
    except Exception, e:        
        info("\n\n    ERROR! " + repr(e) + "\n\n")
        exit(1)
    if len(dir_names) == 0:
        fatal("NOTHING TO GRADE!")
        
    for dn in dir_names:
        target = eld + "/graded/" + dn
        
        if (os.path.exists(target + "/shipped")):
            info ("\n\n   ERROR! DIRECTORY ALREADY EXISTS: " + target + "/shipped\n\n")
            exit(1)
        if (os.path.exists(target + "/corrected")):
            info ("\n\n   ERROR! DIRECTORY ALREADY EXISTS: " + target + "/corrected\n\n")
            exit(1)
            
        shutil.copytree(eld + "/shipped/" + dn , target + "/shipped")        
        shutil.copytree(eld + "/shipped/" + dn , target + "/corrected")


@subcmd('zip-grades', help='Creates a separate zip for each student containing his graded sheet and code')
def zip_grades(parser,context,args):
    ld = arg_date(parser, args)
    eld = "private/exams/" + ld
    try:
        dir_names = os.listdir(eld + "/shipped")
    except Exception, e:        
        info("\n\n    ERROR! " + repr(e) + "\n\n")
        exit(1)
    if len(dir_names) == 0:
        info("\n\n  ERROR! NOTHING TO ZIP!\n\n")
    for dn in dir_names:
        target = eld + "/graded/" + dn
        shutil.make_archive(target, 'zip', target)

@subcmd('publish-exam', help='To be used after an exam is finishedAfter an exam, copies the exam from private/exam/ to exam/')
def publish_exam(parser,context,args):
    ld = arg_date(parser, args)
    source = "private/exams/" + ld + "/"
    source_exercises = source  + conf.filename + "-"+ld 
    source_solutions = source +  "solutions" 

    if not os.path.exists(source):
        fatal("SOURCE PRIVATE EXAM FOLDER " + source + " DOES NOT EXISTS !")
    if os.path.exists(source_exercises):
        fatal("SOURCE PRIVATE EXAM FOLDER " + source_exercises + " DOES NOT EXISTS !")
    if os.path.exists(source_solutions):
        fatal("SOURCE PRIVATE EXAM FOLDER " + source_solutions + " DOES NOT EXISTS !")

    dest = "exams/" + ld + "/"
    dest_exercises = dest + "exercises"
    dest_solutions = dest + "solutions"

    if os.path.exists(dest):
        fatal("TARGET PUBLIC EXAM FOLDER " + dest + " ALREADY EXISTS !")
    if os.path.exists(dest_exercises):
        fatal("TARGET PUBLIC EXAM FOLDER " + dest_exercises + " ALREADY EXISTS !")
    if os.path.exists(dest_solutions):
        fatal("TARGET PUBLIC EXAM FOLDER " + dest_solutions + " ALREADY EXISTS !")

    info("Copying exercises to " + str(dest_exercises) + "  ...")
    for file in glob.glob(source_exercises + "/*"):
        print("Copying " + str(file))
        shutil.copy(file, dest_exercises)
    info("Copying solutions to " + str(dest_solutions) + "  ...")
    for file in glob.glob(source_solutions + "/*"):
        print("Copying " + str(file))
        shutil.copy(file, dest_solutions)
    info("DONE.")


handler = ArgumentHandler(description='Manages ' + conf.filename + ' exams.',
                         use_subcommand_help=True)
handler.run()

print("")
info("DONE.\n")




