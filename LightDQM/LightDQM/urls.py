"""LightDQM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, patterns, include
from .views import BugListView, BugDetailView, RegisterView, BugCreateView
from django.core.urlresolvers import reverse_lazy
from django.contrib import admin
from LightDQM.views import *
from webdaq.views import *
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^help/', dqm_help),
    url(r'^main/$', main),
    url(r'^main/chamber/$', chamber),
    url(r'^chamber/chip/$', chamber),
    url(r'^run/chamber/$', chamber),
    url(r'^main/([a-zA-Z]+)/run/(\d+)/$', chamber),
    url(r'^main/([a-zA-Z]+)/run/(\d+)/report/$', report),
    url(r'^main/([a-zA-Z]+)/run/(\d+)/amc/([\w\+%_&\- ]+)/$', amc), #runType, runN, amc
    url(r'^main/([a-zA-Z]+)/run/(\d+)/([\w\+%_&\- ]+)/$', gebs), #runType, runN, chamber
    url(r'^main/([a-zA-Z]+)/run/(\d+)/([\w\+%_&\- ]+)/vfat/(\d+)/$', vfats), #runType, runN, chamber, vfatN
    url(r'^main/([a-zA-Z]+)/run/(\d+)/([\w\+%_&\- ]+)/vfat/(\d+)/([\w\+%_&\- ]+)/$', display_vfat), #runType, runN, chamber, vfatN, hist
    url(r'^main/([a-zA-Z]+)/run/(\d+)/([\w\+%_&\- ]+)/canvas/([a-zA-Z]+)/$', display_canvas), #runType, runN, chamber, canvas

#for bugtracker
    url(r'^bugs/', include('bugtracker.urls')),
# for gemsupervisot
    url(r'^gemsupervisor/', include('webdaq.urls')),
]
