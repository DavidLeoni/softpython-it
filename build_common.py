# file shared between build.py and conf.py

import os
import inspect


def detect_assembly(system):
    return False

def warn(msg):
    print("")
    print("   WARNING: " + str(msg))
    print("")

def super_doc_dir():
    return os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

FORMATS = ["html", "epub", "pdf"]

SYSTEMS = {
    "default" : {
        "name" : "Default system",
        "outdir":"_build/",
        "exclude_patterns": ["**_build"]
    }
}

MANUALS = {
    "student": {
        "name" : "Corso Soft Python",
        "audience" : "Studenti",
        "args" : "-t student",
        "output" : "student",
        "exclude_patterns" : ['instructor/*']
    },
    "instructors": {
        "name" : "Soft Python - Manuale dell'istruttore",
        "audience": "manuale per insegnanti",
        "args" : "-t instructor",
        "output" : "instructor",
        "exclude_patterns" : ['student/*']
    }
}
