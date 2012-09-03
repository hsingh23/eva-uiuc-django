from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('eva_uiuc_app.views',
    # Examples:
    # url(r'^$', 'eva.views.home', name='home'),
    # url(r'^eva/', include('eva.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^course-info/',"course_info"),
    url(r'^course-title/',"course_title"),
    url(r'^course-code/',"course_code"),
    url(r'^test/',"test"),
    url(r'^test-a/',"test_a"),

)
