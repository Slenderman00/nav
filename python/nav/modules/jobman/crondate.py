import time
import datetime

class Crondate():
    def __init__(self, crondate):
        self.crondate = crondate

        self.minutes = None
        self.hours = None
        self.days = None
        self.months = None
        self.weekdays = None

        self.parse()
        self.handleData()

        self.lastRun = None

    def parse(self):
        if self.crondate.startswith("@"):
            self.parseSpecial()
        else:
            self.parseNormal()

    def getString(self):
        return self.crondate

    def parseSpecial(self):
        if self.crondate == '@annually' or self.crondate == '@yearly':
            self.minutes = "0"
            self.hours = "0"
            self.days = "1"
            self.months = "1"
            self.weekdays = "*"
        
        if self.crondate == '@monthly':
            self.minutes = "0"
            self.hours = "0"
            self.days = "1"
            self.months = "*"
            self.weekdays = "*"
        
        if self.crondate == '@weekly':
            self.minutes = "0"
            self.hours = "0"
            self.days = "*"
            self.months = "*"
            self.weekdays = "0"
        
        if self.crondate == '@daily' or self.crondate == '@midnight':
            self.minutes = "0"
            self.hours = "0"
            self.days = "*"
            self.months = "*"
            self.weekdays = "*"
        
        if self.crondate == '@hourly':
            self.minutes = "0"
            self.hours = "*"
            self.days = "*"
            self.months = "*"
            self.weekdays = "*"

    def parseNormal(self):
        if len(self.crondate.split()) == 5:
            self.minutes, self.hours, self.days, self.months, self.weekdays = self.crondate.split()
        else:
            raise ValueError("Invalid crondate")
        
    def handleData(self):
        #check for lists and ranges
        if "," in self.minutes:
            self.minutes = self.minutes.split(",")
        elif "-" in self.minutes:
            #all numbers between the two numbers must be generated
            start, end = self.minutes.split("-")
            self.minutes = [str(i) for i in range(int(start), int(end)+1)]
        elif "/" in self.minutes:
            #all numbers between 0 and 59 that are divisible by the number must be generated
            start, end = self.minutes.split("/")
            self.minutes = [str(i) for i in range(0, 60) if i % int(start) == 0]
        
        if "," in self.hours:
            self.hours = self.hours.split(",")
        elif "-" in self.hours:
            start, end = self.hours.split("-")
            self.hours = [str(i) for i in range(int(start), int(end)+1)]
        elif "/" in self.hours:
            start, end = self.hours.split("/")
            self.hours = [str(i) for i in range(0, 24) if i % int(start) == 0]
        
        if "," in self.days:
            self.days = self.days.split(",")
        elif "-" in self.days:
            start, end = self.days.split("-")
            self.days = [str(i) for i in range(int(start), int(end)+1)]
        elif "/" in self.days:
            start, end = self.days.split("/")
            self.days = [str(i) for i in range(1, 32) if i % int(start) == 0]

        if "," in self.months:
            self.months = self.months.split(",")
        elif "-" in self.months:
            start, end = self.months.split("-")
            self.months = [str(i) for i in range(int(start), int(end)+1)]
        elif "/" in self.months:
            start, end = self.months.split("/")
            self.months = [str(i) for i in range(1, 13) if i % int(start) == 0]

        if "," in self.weekdays:
            self.weekdays = self.weekdays.split(",")
        elif "-" in self.weekdays:
            start, end = self.weekdays.split("-")
            self.weekdays = [str(i) for i in range(int(start), int(end)+1)]

        #check for special characters
        if self.minutes == "*":
            self.minutes = [str(i) for i in range(0, 60)]
        if self.hours == "*":
            self.hours = [str(i) for i in range(0, 24)]
        if self.days == "*":
            self.days = [str(i) for i in range(1, 32)]
        if self.months == "*":
            self.months = [str(i) for i in range(1, 13)]
        if self.weekdays == "*":
            self.weekdays = [str(i) for i in range(0, 7)]

        #convert to int and add to list if not in list
        if type(self.minutes) != list:
            self.minutes = [int(self.minutes)]
        
        if type(self.hours) != list:
            self.hours = [int(self.hours)]

        if type(self.days) != list:
            self.days = [int(self.days)]
        
        if type(self.months) != list:
            self.months = [int(self.months)]
        
        if type(self.weekdays) != list:
            self.weekdays = [int(self.weekdays)]
        

    def getNextRun(self):
        now = datetime.datetime.now()
        next_minute = (now.minute // 15 + 1) * 15
        next_hour = min(self.hours, key=lambda h: (h - now.hour) % 24)
        next_day = min(self.days, key=lambda d: (d - now.day) % 31)
        next_month = min(self.months, key=lambda m: (m - now.month) % 12)
        next_weekday = min(self.weekdays, key=lambda wd: (wd - now.weekday()) % 7)
        next_run = datetime.datetime(now.year, next_month, next_day, next_hour, next_minute)
        if next_run <= now:
            next_run = datetime.datetime(now.year, next_month, next_day, next_hour, next_minute) + datetime.timedelta(days=31)
        return (next_run - now).total_seconds()
        

    #jobs might not be called on time, 
    # in this case the program has to call it even 
    # if it is a minute late

    def shouldRun(self):
        dt = datetime.datetime.now()
        hours = dt.hour
        minutes = dt.minute
        days = dt.day
        months = dt.month
        weekdays = dt.weekday()

        if str(hours) in self.hours and str(minutes) in self.minutes and str(days) in self.days and str(months) in self.months and str(weekdays) in self.weekdays:
            return True
        else:
            return False

            
    def setLastRun(self):
        self.lastRun = time.time()