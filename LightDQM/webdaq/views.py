from django.shortcuts import render
from webdaq.forms import *
import uhal
import amc13
import sys
import io
import os
import threading
from cStringIO import StringIO
import struct
from amc13manager import AMC13manager
from helper import OutputGrabber
from registers_uhal import *
from glib_system_info_uhal import *
from glib_user_functions_uhal import *

def gemsupervisor(request):
  amc13N = 0
  if request.POST:
    form = ConfigForm(request.POST)
    if form.is_valid():
      configured = 'disabled'
      state = 'configured'
      amc13N = form.cleaned_data['amc13_choice']
      amcN = form.cleaned_data['amc_list']
      trigger_type = form.cleaned_data['trigger_type']
      trigger_rate = form.cleaned_data['trigger_rate']
      verbosity = int(form.cleaned_data['verbosity'])
      uhal.setLogLevelTo(uhal.LogLevel.ERROR)
      m_AMC13manager = AMC13manager(amc13N)
      #m_AMC13manager.configureInputs(uTCAslot)
      #m_AMC13manager.configureTrigger()
      #m_AMC13manager.startDataTaking(options.ofile,options.n_events)
      status = m_AMC13manager.device.getStatus()
      status.SetHTML()
      # Create pipe and dup2() the write end of it on top of stdout, saving a copy
      # of the old stdout
      out = OutputGrabber()
      out.start()
      status.Report(verbosity)
      out.stop()
      shtml = out.capturedtext
      b = shtml.find("<body>")
      e = shtml.find("</body>")
      #shtml = shtml[b+6:e]
      with open("webdaq/templates/amc13status.html", "w") as text_file:
        text_file.write(shtml)
  else:
    form = ConfigForm()
    configured = 'primary'
    state = 'halted'
  return render(request, 'gemsupervisor.html',{'form':form,
                                               'state':state,
                                               'configured':configured,
                                               'amc13N':amc13N})
