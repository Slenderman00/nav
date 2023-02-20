import sqlite3
from pathlib import Path

from nav.modules.jobman.crondate import Crondate

#get path to module
MODULE_DIR = Path(__file__).parent


def createDB():
    dbpath = Path(MODULE_DIR, "jobman.db")

    #raise Exception(dbpath)


    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute('''CREATE TABLE jobs
                 (job_id INTEGER PRIMARY KEY, job_name text, job_description text, job_regex text, job_logtype text, date text, command text)''')
    conn.commit()
    conn.close()

def DBExist():
    dbpath = Path(MODULE_DIR, "jobman.db")
    if dbpath.is_file():
        return True
    else:
        return False

def tableExists():
    if DBExist():
        dbpath = Path(MODULE_DIR, "jobman.db")
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
        if c.fetchone() is not None:
            return True
        else:
            return False
    else:
        return False

def addJobToDB(job):
    if DBExist() and tableExists():
        dbpath = Path(MODULE_DIR, "jobman.db")
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("INSERT INTO jobs (job_name, job_description, job_regex, job_logtype, date, command) VALUES (?,?,?,?,?,?)", job)
        conn.commit()
        conn.close()
    else:
        createDB()
        addJobToDB(job)

def updateJobInDB(job):
    if DBExist() and tableExists():
        dbpath = Path(MODULE_DIR, "jobman.db")
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("UPDATE jobs SET job_name = ?, job_description = ?, job_regex = ?, job_logtype = ?, date = ?, command = ? WHERE job_id = ?", job)
        conn.commit()
        conn.close()
    else:
        createDB()
        updateJobInDB(job)

class Job():
    def __init__(self, name, description, regex, plottype, crondate, command, id=None):
        self.name = name
        self.description = description
        self.regex = regex
        self.plottype = plottype
        self.crondate = Crondate(crondate)
        self.command = command
        self.id = id

    def getJob(self):
        return (self.name, self.description, self.regex, self.plottype, self.crondate.getString(), self.command, self.id)
    
    def addJobToDB(self):
        addJobToDB(self.getJob())

    def updateJobInDB(self):
        updateJobInDB(self.getJob())


class Jobman():
    def __init__(self):
        self.jobs = []


    def getJobs(self):
        return self.jobs
    
    def getJobsFromDB(self):
        if DBExist():
            dbpath = Path(MODULE_DIR, "jobman.db")
            conn = sqlite3.connect(dbpath)
            c = conn.cursor()
            c.execute("SELECT * FROM jobs")
            jobs = c.fetchall()
            conn.close()
            
            for job in jobs:
                self.jobs.append(Job(job[1], job[2], job[3], job[4], job[5], job[6], id=job[0]))

        else:
            createDB()

    def getJobById(self, id):
        for job in self.jobs:
            if job.id == id:
                return job