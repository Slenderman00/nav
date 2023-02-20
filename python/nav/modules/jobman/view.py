#
# Copyright (C) 2018,2019 Joar Heimonen
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3 as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#

import django.http
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.shortcuts import render
from django.template import Context, Template
from django import forms

from nav.modulemanager import getTemplate, getTools, getModules
from nav.django.context_processors import account_processor
from nav.web.utils import get_navpath_root

from nav.modulemanager import getTemplate

from nav.modules.jobman.jobman import Job, Jobman

import re

def validate_crondate(crondate):
    reg = "/(@(annually|yearly|monthly|weekly|daily|hourly|reboot))|(@every (\d+(ns|us|µs|ms|s|m|h))+)|((((\d+,)+\d+|(\d+(\/|-)\d+)|\d+|\*) ?){5,7})/"
    if not re.match(reg, crondate):
        raise forms.ValidationError("Invalid crondate")
    
# get template
jobman = getTemplate("jobman", "jobman.html")
jobmanEdit = getTemplate("jobman", "jobmanedit.html")

class CreateJobForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    description = forms.CharField(label='Description', max_length=100)
    command = forms.CharField(label='Command', max_length=200)
    plottype = forms.ChoiceField(label='Plot type', choices=[
        ('1', 'Plot succsess rate'), ('2', 'Plot regex'), ('3', 'No plot')
    ], initial="1")
    crondate = forms.CharField(label='Crondate', max_length=100, initial="15 * * * *")
    regex = forms.CharField(label='Regex', max_length=200, required=False)


# create a view class
class JobmanView(View):
    # create a get method
    def get(self, request):

        j1 = Jobman()
        j1.getJobsFromDB()

        # This is boilerplate and should be added to the modulemanager
        data = {
            **account_processor(request),
            **{"STATIC_URL": "../static/"},
            **{"navpath": [get_navpath_root(), ("jobman",)]},
            **{"jobs": j1.getJobs()},
        }

        # return a response
        return HttpResponse(
            jobman.render(Context(data)),
        )

class JobmanEditView(View):
    def post(self, request, job_id):
        jobData = request.method

        if request.method == 'POST':
            form = CreateJobForm(request.POST)
            jobData = 'form not valid'
            
            for error in form.errors:
                jobData += error

            if form.is_valid():
                #    def __init__(self, name, description, regex, logtype, crondate, command):
                if job_id == '00':
                    newJob = Job(
                        form.cleaned_data['name'],
                        form.cleaned_data['description'],
                        form.cleaned_data['regex'],
                        form.cleaned_data['plottype'],
                        form.cleaned_data['crondate'],
                        form.cleaned_data['command']
                    )

                    newJob.addJobToDB()
                else:
                    newJob = Job(
                        form.cleaned_data['name'],
                        form.cleaned_data['description'],
                        form.cleaned_data['regex'],
                        form.cleaned_data['plottype'],
                        form.cleaned_data['crondate'],
                        form.cleaned_data['command'],
                        int(job_id)
                    )

                    newJob.updateJobInDB()


                #redirect to a new URL:
                return HttpResponseRedirect('/jobman/')


    def get(self, request, job_id):

        form = CreateJobForm()

        if job_id != '00':
            jman = Jobman()
            jman.getJobsFromDB()
            job = jman.getJobById(int(job_id))
            form = CreateJobForm(initial={
                'name': job.name,
                'description': job.description,
                'command': job.command,
                'plottype': job.plottype,
                'crondate': job.crondate.crondate,
                'regex': job.regex
            })

        data = {
            **account_processor(request),
            **{"STATIC_URL": "../../../static/"},
            **{"navpath": [get_navpath_root(), ("jobman",)]},
            **{"form": form},
        }

        return HttpResponse(
            jobmanEdit.render(Context(data)),
        )
