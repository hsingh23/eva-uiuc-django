import sys
from urllib import FancyURLopener
from django.core.management.base import BaseCommand, CommandError
import string
import re #regular expression
from bs4 import BeautifulSoup, Comment, SoupStrainer #used for HTML and XML
from datetime import datetime
from time import time
import os
from evauiuc.models import *
from random import choice, randrange
import time
import Queue
import threading
least_year = 2011
base = 'http://courses.illinois.edu/cisapp/explorer/schedule.xml'
max_workers=100
queue = Queue.Queue()
user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
]
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

class MyOpener(FancyURLopener, object):
    version = choice(user_agents)

class ThreadUrl(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            #grabs host from queue
            host = self.queue.get()
            print bcolors.HEADER + host +bcolors.ENDC
            try:
                update_database(host)
            except IOError:
                print bcolors.WARNING + host +bcolors.ENDC
                time.sleep(randrange(1,3))
                update_database(host)
            print host
            self.queue.task_done()

class Command(BaseCommand):
    args = '<None>'
    help = 'Scrapes your shit'

    def handle(self, *args, **options):

        links = []
        soup = BeautifulSoup(MyOpener().open(base).read(),"xml")
        years = soup.find_all("calendarYear")
        for a in years:
            if int(a["id"]) >= least_year:
                terms = BeautifulSoup(MyOpener().open(a["href"]).read(),"xml").find_all("term")
                for b in terms:
                    # links.append(b["href"])
                    subjects = BeautifulSoup(MyOpener().open(b["href"]).read(),"xml").find_all("subject")
                    for c in subjects:
                        links.append(c["href"]+"?mode=cascade")
                        # print "Hold you shit, ",c["href"]
                        # soup = BeautifulSoup(MyOpener().open(c["href"]+"?mode=cascade").read(),"xml")
                        # update_database(soup)
        # print links
        # raise Exception()
        #populate queue with data
        for link in links:
            queue.put(link)

        for i in range(100):
        #for i in range(4):
            t = ThreadUrl(queue)
            t.setDaemon(True)
            t.start()


        #wait on the queue until everything has been processed
        # queue.join()



def update_database(host):
    # soup = BeautifulSoup(open("subject.xml","r"),"xml")
    soup = BeautifulSoup(MyOpener().open(host).read(),"xml")
    try:
        sid = soup.contents[0]['id']
    except Exception as e:
        # sys.stderr.write(host)
        return
# CHANGE this shitty code, use functions and next for soup
    slabel = soup.find("label").get_text(strip=True) if soup.find("label") else ""
    collegeCode = soup.find("collegeCode").get_text(strip=True) if soup.find("collegeCode") else ""
    departmentCode = soup.find("departmentCode").get_text(strip=True) if soup.find("departmentCode") else ""
    unitName = soup.find("unitName").get_text(strip=True) if soup.find("unitName") else ""
    contactName = soup.find("contactName").get_text(strip=True) if soup.find("contactName") else ""
    contactTitle = soup.find("contactTitle").get_text(strip=True) if soup.find("contactTitle") else ""
    addressLine1 = soup.find("addressLine1").get_text(strip=True) if soup.find("addressLine1") else ""
    addressLine2 = soup.find("addressLine2").get_text(strip=True) if soup.find("addressLine2") else ""

    phoneNumber = soup.find("phoneNumber").get_text(strip=True) if soup.find("phoneNumber") else ""
    webSiteURL = soup.find("webSiteURL").get_text(strip=True) if soup.find("webSiteURL") else ""
    collegeDepartmentDescription = soup.find("collegeDepartmentDescription").get_text(strip=True)

    s,created = Subject.objects.get_or_create(sid=sid, label=slabel, collegeCode=collegeCode,
     unitName=unitName, defaults={"departmentCode":departmentCode, "contactName":contactName,
     "contactTitle":contactTitle, "addressLine1":addressLine1, "addressLine2":addressLine2,
     "phoneNumber":phoneNumber, "webSiteURL":webSiteURL, "collegeDepartmentDescription":collegeDepartmentDescription})
    subject_id = s.id
    s.save()



    courses = soup.find_all("cascadingCourse")
    for c in courses:
        number = re.search(r"\d+",c["id"]).group()
        clabel = c.label.get_text(strip=True)
        creditHours = re.search(r"\d+",c.creditHours.get_text(strip=True)).group()
        sectionDegreeAttributes = c.sectionDegreeAttributes.get_text(strip=True)  if c.sectionDegreeAttributes else ""
        description = c.description.get_text(strip=True) if c.description else ""
        course, a = Course.objects.get_or_create(label=clabel,number=number,subject_id=subject_id,
        defaults={"creditHours":creditHours,
         "sectionDegreeAttributes":sectionDegreeAttributes,
         "description":description} )
        course.save()
        course_id = course.id
        sections = c.find_all("detailedSection")
        all_sections = []
        all_instructors = []
        for s in sections:
            calendarYear = s.calendarYear.get_text(strip=True) if s.calendarYear else ""
            term = s.term.get_text(strip=True) if s.term else ""
            sectionNumber = s.sectionNumber.get_text(strip=True) if s.sectionNumber else ""
            statusCode = s.statusCode.get_text(strip=True) if s.statusCode else ""
            partOfTerm = s.partOfTerm.get_text(strip=True) if s.partOfTerm else ""
            sectionStatusCode = s.sectionStatusCode.get_text(strip=True) if s.sectionStatusCode else ""
            enrollmentStatus = s.enrollmentStatus.get_text(strip=True) if s.enrollmentStatus else ""
            startDate = datetime.strptime(s.startDate.get_text(strip=True),"%Y-%m-%d-%H:%M") if s.startDate else None
            endDate = datetime.strptime(s.endDate.get_text(strip=True),"%Y-%m-%d-%H:%M") if s.endDate else None
            section_type = s.type.get_text(strip=True) if s.type else ""
            roomNumber = s.roomNumber.get_text(strip=True) if s.roomNumber else ""
            buildingName = s.buildingName.get_text(strip=True) if s.buildingName else "Unknown"
            daysOfTheWeek = s.daysOfTheWeek.get_text(strip=True) if s.daysOfTheWeek else ""
            loc,created = Location.objects.get_or_create(buildingName=buildingName)
            if created:
                loc.save()
            section,created = Section.objects.get_or_create(calendarYear=calendarYear, term=term, sectionNumber=sectionNumber,
             course_id=course_id, defaults = {"statusCode":statusCode, "partOfTerm":partOfTerm,"sectionStatusCode":sectionStatusCode,
                "enrollmentStatus":enrollmentStatus, "startDate":startDate, "endDate":endDate,
                "section_type":section_type, "roomNumber":roomNumber, "daysOfTheWeek":daysOfTheWeek, "location_id":loc.id})
            if created:
                section.save()
            # lookup,created = Section_Location.objects.get_or_create(section=section, location=loc)
            # if created:
            #     lookup.save()
            instructors = s.find_all("instructor")
            for i in instructors:
                if i:
                    firstName = i["firstName"]
                    lastName = i["lastName"]
                    # fullName = i.get_text(strip=True)
                    instructor,created = Instructor.objects.get_or_create(firstName=firstName,lastName=lastName, course=course.label)
                    instructor.save()
                    lookup,created = Section_Instructor.objects.get_or_create(section=section, instructor=instructor)
                    lookup.save()
            # gen_eds = c.find_all("genEdCategories")
            # for g in gen_eds:
            #     temp = g.findAll("description")
            #     attributes = g.find_all("genEdAttribute")
            #     for a in attributes:
            #         ns2code = a['code']
            #         ns2desc = temp[1].get_text(strip=True) if temp[1] else ""


            #     description = temp[0].get_text(strip=True) if temp[0] else ""
            #     category = g.category['id']



            #     print description, category, ns2code, ns2desc

    # course = models.ForeignKey(Course, to_field='label')
    # category = models.CharField(max_length=10)
    # description = models.CharField(max_length=1000)
    # ns2code = models.CharField(max_length=10)
    # ns2desc = models.CharField(max_length=1000)
        # print c["id"], all_instructors