from django.contrib import admin
from models import Course, Location, Section, Subject, Instructor, GenEdCategory, GenEdAttribute

admin.site.register(Subject)
admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Location)
admin.site.register(Instructor)
admin.site.register(GenEdAttribute)
admin.site.register(GenEdCategory)
