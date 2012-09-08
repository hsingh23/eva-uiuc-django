# Create your views here.
from django.shortcuts import render_to_response
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from models import *
import json
import re
import os
from django.core import serializers
PRODUCTION = "PRODUCTION" in os.environ and os.environ['PRODUCTION'] == 'True'
POSTGRES = False

def find(request):
    pass
def test(request):
    get = request.GET
    if "q" in get:
        # escape this shit
        course = str(get["q"])
        return HttpResponse(serializers.serialize('json',
            Section.objects.filter(course__label__icontains=course)[:1], indent=4,
            relations={'course':{'relations':('subject',)}}))
    return HttpResponse(status=404)

def test_a(request):
    get = request.GET
    if "q" in get:
        # escape this shit
        course = str(get["q"])
        a = [get_everything_interesting(a) for a in Section.objects.filter(course__label__icontains=course, term="Fall 2012")[:10]]
        return HttpResponse(json.dumps(a))
    return HttpResponse(status=404)

def get_everything_interesting(a):
    result = {}
    result["section"] = [a.id, a.sectionNumber, a.statusCode, a.partOfTerm, a.term,
        a.sectionStatusCode, a.enrollmentStatus, str(a.startDate), str(a.endDate), str(a.calendarYear),
        a.code, a.section_type, a.roomNumber, a.daysOfTheWeek]
    try:
        result["instructor"] = [a.instructor.firstName, a.instructor.lastName, a.instructor.rating]
    except AttributeError:
        result["instructor"] = ["Unknown"]
    try:
        result["location"] = [a.location.buildingName, a.location.address, str(a.location.lat), str(a.location.lng)]
    except AttributeError:
        # TODO: Make this better
        result["location"] = ["Unknown"]
    result["subject"] = [a.course.subject.sid, a.course.subject.label]
    result["course"] = [a.course.label, a.course.description, a.course.creditHours, a.course.votes, a.course.number,
        a.course.courseSectionInformation,a.course.sectionDegreeAttributes, a.course.classScheduleInformation]
    return result



def course_code(request):
    if ("q" in request.GET and request.GET["q"] != ""):
        q = str(request.GET["q"]).replace("\'","").replace("\"","")
        result = course_code_helper(q)
        if ("callback" in request.GET):
            if is_valid_jsonp_callback_value(callback):
                return HttpResponse(callback+"("+json.dumps(result)+");", content_type='application/json')
            else:
                return HttpResponse('Sorry - Your callback is bogus.')
        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        return HttpResponse(status=400)

def course_title(request):
    if ("q" in request.GET and request.GET["q"] != ""):
        q = str(request.GET["q"]).replace("\'","").replace("\"","")
        result = [a.label for a in Course.objects.filter(label__icontains=q)]
        if ("callback" in request.GET):
            if is_valid_jsonp_callback_value(callback):
                return HttpResponse(callback+"("+json.dumps(result)+");", content_type='application/json')
            else:
                return HttpResponse('Sorry - Your callback is bogus.')
        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        return HttpResponse(status=400)

def course_info(request):
    if ("q" in request.GET and request.GET["q"] != ""):
        result = {}
        q = str(request.GET["q"]).replace("\'","").replace("\"","")
        result["course_codes"]=course_code_helper(q,5)
        if POSTGRES:
            result["course_titles"]=[a.label for a in Course.objects.filter(label__icontains=q).distinct('label')[:10]]
            result["teachers"]=[{"name":str(a.lastName)+", "+(a.firstName),"course":(a.course)} for a in Instructor.objects.filter(lastName__icontains=q).order_by("lastName")[:10]]

        else:
            result["course_titles"]=[a.label for a in Course.objects.filter(label__icontains=q)[:10]]
            result["teachers"]=[{"name":str(a.lastName)+", "+(a.firstName),"course":(a.course)} for a in Instructor.objects.filter(lastName__icontains=q).order_by("lastName")[:10]]
        if ("callback" in request.GET):
            if is_valid_jsonp_callback_value(callback):
                return HttpResponse(callback+"("+json.dumps(result)+");", content_type='application/json')
            else:
                return HttpResponse('Sorry - Your callback is bogus.')
        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        return HttpResponse(status=400)

# Helper
def course_code_helper(q, limit=15):
    q = q.replace("\'","").replace("\"","")
    result = []
    if (" " in q):
        # return numbers with name
        q = q.split(" ")
        if not q[1]:
            q[1]= ""
        for a in Course.objects.filter(subject__sid=q[0], number__icontains=q[1]).order_by("number")[:limit]:
            result.append({"code":str(a.subject.sid)+" "+str(a.number), "name":a.label})
    else:
        # return just subject titles
        for a in Subject.objects.filter(sid__icontains=q).order_by("sid")[:15]:
            result.append({"code":a.sid, "name":a.label})
    return result



# THIS IS for is_valid_jsonp_callback_value
import re
from unicodedata import category
valid_jsid_categories_start = frozenset([
    'Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl'
    ])
valid_jsid_categories = frozenset([
    'Lu', 'Ll', 'Lt', 'Lm', 'Lo', 'Nl', 'Mn', 'Mc', 'Nd', 'Pc'
    ])
valid_jsid_chars = ('$', '_')
array_index_regex = re.compile(r'\[[0-9]+\]$')
has_valid_array_index = array_index_regex.search
replace_array_index = array_index_regex.sub
is_reserved_js_word = frozenset([
    'abstract', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class',
    'const', 'continue', 'debugger', 'default', 'delete', 'do', 'double',
    'else', 'enum', 'export', 'extends', 'false', 'final', 'finally', 'float',
    'for', 'function', 'goto', 'if', 'implements', 'import', 'in', 'instanceof',
    'int', 'interface', 'long', 'native', 'new', 'null', 'package', 'private',
    'protected', 'public', 'return', 'short', 'static', 'super', 'switch',
    'synchronized', 'this', 'throw', 'throws', 'transient', 'true', 'try',
    'typeof', 'var', 'void', 'volatile', 'while', 'with',

    # potentially reserved in a future version of the ES5 standard
    # 'let', 'yield'

    ]).__contains__

def is_valid_javascript_identifier(identifier, escape=r'\u', ucd_cat=category):
    """Return whether the given ``id`` is a valid Javascript identifier."""

    if not identifier:
        return False

    if not isinstance(identifier, unicode):
        try:
            identifier = unicode(identifier, 'utf-8')
        except UnicodeDecodeError:
            return False

    if escape in identifier:

        new = []; add_char = new.append
        split_id = identifier.split(escape)
        add_char(split_id.pop(0))

        for segment in split_id:
            if len(segment) < 4:
                return False
            try:
                add_char(unichr(int('0x' + segment[:4], 16)))
            except Exception:
                return False
            add_char(segment[4:])

        identifier = u''.join(new)

    if is_reserved_js_word(identifier):
        return False

    first_char = identifier[0]

    if not ((first_char in valid_jsid_chars) or
            (ucd_cat(first_char) in valid_jsid_categories_start)):
        return False

    for char in identifier[1:]:
        if not ((char in valid_jsid_chars) or
                (ucd_cat(char) in valid_jsid_categories)):
            return False

    return True


def is_valid_jsonp_callback_value(value):
    """Return whether the given ``value`` can be used as a JSON-P callback."""

    for identifier in value.split(u'.'):
        while '[' in identifier:
            if not has_valid_array_index(identifier):
                return False
            identifier = replace_array_index(u'', identifier)
        if not is_valid_javascript_identifier(identifier):
            return False
    return True