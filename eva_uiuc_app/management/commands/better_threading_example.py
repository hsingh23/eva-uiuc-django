import sys
from urllib import FancyURLopener
from django.core.management.base import BaseCommand, CommandError
import string
import re
from bs4 import BeautifulSoup, Comment, SoupStrainer #used for HTML and XML
from datetime import datetime
from time import time
import os
from eva_uiuc_app.models import *
from random import choice, randrange
import time
import Queue
import threading
import logging
logger = logging.getLogger(__name__)

least_year = 2013
base = 'http://courses.illinois.edu/cisapp/explorer/schedule.xml'
max_workers=100

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
    BGWHITEFGBLUE = '\033[91m'
    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
        self.BGWHITEFGBLUE = ''

class MyOpener(FancyURLopener, object):
    version = choice(user_agents)

queue = Queue.Queue()
out_queue = Queue.Queue()
geo_queue = Queue.Queue()

def get_all_cascade_urls():
    links = []
    soup = BeautifulSoup(MyOpener().open(base).read(),"xml")
    years = soup.find_all("calendarYear")
    for a in years:
        if int(a["id"]) >= least_year:
            terms = BeautifulSoup(MyOpener().open(a["href"]).read(),"xml").find_all("term")
            for b in terms:
                subjects = BeautifulSoup(MyOpener().open(b["href"]).read(),"xml").find_all("subject")
                for c in subjects:
                    links.append(c["href"]+"?mode=cascade")
    print links
    return links

def get_create_subject_info(soup):
    sid = soup.contents[0]['id']
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
    s.save()
    return s

def get_create_course_info(c, subject_id):
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
    return course

def get_create_section_info(s, course_id):
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
        geo_queue.put(buildingName, loc)

    section,created = Section.objects.get_or_create(calendarYear=calendarYear, term=term, sectionNumber=sectionNumber,
        course_id=course_id, defaults = {"statusCode":statusCode, "partOfTerm":partOfTerm,"sectionStatusCode":sectionStatusCode,
        "enrollmentStatus":enrollmentStatus, "startDate":startDate, "endDate":endDate,
        "section_type":section_type, "roomNumber":roomNumber, "daysOfTheWeek":daysOfTheWeek, "location_id":loc.id})
    if created:
        section.save()
    return section

def get_create_teacher_info(i, course_label):
    firstName = i["firstName"]
    lastName = i["lastName"]
    instructor,created = Instructor.objects.get_or_create(firstName=firstName,lastName=lastName, course=course_label)
    if created:
        instructor.save()
    return instructor

def get_create_gened_category(c):
    category = c["id"]
    description = c.description.get_text(strip=True).encode("utf-8")
    gened_category, created = GenEdCategory.objects.get_or_create(category=category, description=description)
    if created:
        gened_category.save()

    for a in c.find_all("genEdAttribute"):
        gened_category.genEdAttribute.add(get_create_gened_attribute(a))

def get_create_gened_attribute(a):
    code = a["code"]
    desc = a.get_text(strip=True).encode("utf-8")
    gened_attribute,created = GenEdAttribute.objects.get_or_create(ns2code=code,ns2desc=desc)
    if created:
        gened_attribute.save()
    return gened_attribute

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while True:
            #grabs host from queue
            host = self.queue.get()

            #place chunk into out queue
            try:
                chunk = MyOpener().open(host).read()
            except Exception:
                time.sleep(randrange(1,3))
                chunk = MyOpener().open(host).read()

            self.out_queue.put(chunk)
            print "%s %s %s" %(bcolors.HEADER, host, bcolors.ENDC)
            #signals to queue job is done
            self.queue.task_done()

class GetLocation(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            host = self.queue.get()

            buildingName = host[0]
            loc = host[1]
            try:
                a = json.loads(urllib.urlopen('http://maps.google.com/maps/api/geocode/json?address='+buildingName.replace(" ","+")+',%20Urbana,%20Champaign,%20IL&sensor=false').read())
            except Exception:
                time.sleep(randrange(1,3))
                a = json.loads(urllib.urlopen('http://maps.google.com/maps/api/geocode/json?address='+buildingName.replace(" ","+")+',%20Urbana,%20Champaign,%20IL&sensor=false').read())

            loc.address = a["results"][0]["formatted_address"]
            loc.lat = a["results"][0]["geometry"]["location"]["lat"]
            loc.lng = a["results"][0]["geometry"]["location"]["lng"]
            loc.save()

            print "%s %s %s" %(bcolors.BGWHITEFGBLUE, "Just got location "+loc.address, bcolors.ENDC)
            #signals to queue job is done
            self.queue.task_done()

class DatamineThread(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, out_queue):
        threading.Thread.__init__(self)
        self.out_queue = out_queue

    def run(self):
        while True:
            #grabs host from queue
            chunk = self.out_queue.get()
            soup = BeautifulSoup(chunk, "xml")
            # Some checks for stupid stuff on university side
            # EX: "No courses found. year=2013,semester=spring,subject=BMNA"
            do_next = True
            try:
                sid = soup.contents[0]['id']
            except Exception as e:
                self.out_queue.task_done()
                do_next = False
                # IS THIS KILLING MY THREADS?
            if do_next:
                # sometimes blah is not defined
                try:
                    blah = soup.cascadingCourses.cascadingCourse.subject["href"]
                    print "%s working on %s %s"  %(bcolors.WARNING, blah , bcolors.ENDC)
                except:
                    pass
                # Sometime the database freaks out and dies - usually give Integrity Error and some other error
                try:
                    subject = get_create_subject_info(soup)
                    courses = soup.find_all("cascadingCourse")
                    for c in courses:
                        course = get_create_course_info(c, subject.id)
                        if c.genEdCategories:
                            for g in c.genEdCategories.find_all("category"):
                                get_create_gened_category(g)
                        sections = c.find_all("detailedSection")

                        for s in sections:
                            section = get_create_section_info(s, course.id)

                        instructors = s.find_all("instructor")
                        for i in instructors:
                            if i:
                                instructor=get_create_teacher_info(i, course.label)
                                section.instructor.add(instructor)
                        section.save()
                except Exception as e:
                    if blah:
                        print '%s Database error: %s at %s %s' %(bcolors.FAIL, e, blah, bcolors.ENDC)
                    else:
                        print '%s Database error: %s %s' %(bcolors.FAIL, e, bcolors.ENDC)


                #signals to queue job is done
                try:
                    print "%s DONE working on %s %s"  %(bcolors.OKGREEN, blah, bcolors.ENDC)
                except:
                    pass
                self.out_queue.task_done()


class Command(BaseCommand):
    args = '<None>'
    help = 'Scrapes your shit'

    def handle(self, *args, **options):
        # This is like main()
        start = time.time()
        urls = get_all_cascade_urls()
        for i in range(30):
            t = ThreadUrl(queue, out_queue)
            t.setDaemon(True)
            t.start()

        for link in urls:
            queue.put(link)

        for i in range(40):
            dt = DatamineThread(out_queue)
            dt.setDaemon(True)
            dt.start()

        for i in range(10):
            dt = DatamineThread(geo_queue)
            dt.setDaemon(True)
            dt.start()

        queue.join()
        out_queue.join()
        geo_queue.join()
        print "Elapsed Time: %s" % (time.time() - start)