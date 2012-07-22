from django.db import models

class GenEdAttribute(models.Model):
    ns2code = models.CharField(max_length=5, unique=True)
    ns2desc = models.CharField(max_length=500)
    def __unicode__(self):
        return self.ns2code

class GenEdCategory(models.Model):
    category = models.CharField(max_length=5)
    description = models.CharField(max_length=500)
    genEdAttribute = models.ManyToManyField(GenEdAttribute)
    def __unicode__(self):
        return self.category

class Instructor(models.Model):
    firstName = models.CharField(max_length=10)
    lastName = models.CharField(max_length=100)
    rating = models.IntegerField(default=0, max_length=6)
    course = models.CharField(max_length=100)
    def __unicode__(self):
        return "%s %s, %s" % (self.firstName, self.lastName, self.course)

class Location(models.Model):
    buildingName = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=5000, blank=True)
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, db_index=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, db_index=True)

    def __unicode__(self):
        return self.buildingName

class Subject(models.Model):
    sid = models.CharField(max_length=10, unique=True, db_index=True)
    label = models.CharField(max_length=300, db_index=True)
    collegeCode = models.CharField(max_length=50, db_index=True)
    departmentCode = models.CharField(max_length=50)
    unitName = models.CharField(max_length=400, db_index=True)
    contactName = models.CharField(max_length=500)
    contactTitle = models.CharField(max_length=50)
    addressLine1 = models.CharField(max_length=1000)
    addressLine2 = models.CharField(max_length=1000)
    phoneNumber = models.CharField(max_length=600)
    webSiteURL = models.CharField(max_length=5000)
    collegeDepartmentDescription = models.CharField(max_length=10000)
    def __unicode__(self):
        return self.label

class Course(models.Model):
    subject = models.ForeignKey(Subject, to_field='id')
    label = models.CharField(max_length=500, db_index=True)
    description = models.CharField(max_length=5000)
    creditHours = models.IntegerField()
    sectionDegreeAttributes = models.CharField(max_length=5000)
    votes = models.IntegerField(default=0)
    number = models.IntegerField(db_index=True)
    courseSectionInformation = models.CharField(max_length=5000, blank=True)
    sectionDegreeAttributes = models.CharField(max_length=5000, blank=True)
    classScheduleInformation = models.CharField(max_length=5000, blank=True)
    def __unicode__(self):
        return self.label

class Section(models.Model):
    instructor = models.ManyToManyField(Instructor, blank=True, null=True)
    gened = models.ManyToManyField(GenEdCategory, blank=True, null=True)
    course = models.ForeignKey(Course, to_field='id', blank=True, null=True)
    location = models.ForeignKey(Location, to_field='id', blank=True, null=True)
    sectionNumber = models.CharField(max_length=10, db_index=True)
    statusCode = models.CharField(max_length=1000)
    partOfTerm = models.CharField(max_length=1000)
    term = models.CharField(max_length=100, db_index=True)
    sectionStatusCode = models.CharField(max_length=1000)
    enrollmentStatus = models.CharField(max_length=1000)
    startDate = models.DateTimeField('Date started', null=True)
    endDate = models.DateTimeField('Date ended', null=True)
    calendarYear = models.IntegerField(max_length=4, db_index=True)
    code = models.CharField(max_length=10)
    section_type = models.CharField(max_length=30, blank=True)
    roomNumber = models.CharField(max_length=30)
    daysOfTheWeek = models.CharField(max_length=10)
    def __unicode__(self):
        if self.course:
            return "%s %s %s: %s" %(self.course.label, self.sectionNumber, self.code, self.calendarYear)
        return "%s %s: %s" %(self.sectionNumber, self.code, self.calendarYear)

