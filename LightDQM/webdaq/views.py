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
from amcmanager import AMCmanager

amc13N = 0
state = 'halted'
amcN = u'10'
m_uTCAslot = 160+int(amcN)

ipaddr = '192.168.0.%d'%(m_uTCAslot)
address_table = "file://${GEM_ADDRESS_TABLE_PATH}/glib_address_table.xml"
uri = "chtcp-2.0://localhost:10203?target=%s:50001"%(ipaddr)
m_AMC13manager = AMC13manager()
m_AMCmanager = AMCmanager()
verbosity = 1

def gemsupervisor(request):
  global amc13N
  global state
  global amcN
  global m_uTCAslot
  global ipaddr
  global address_table
  global uri
  global m_AMC13manager
  global m_AMCmanager
  global verbosity

  if request.POST:
    if 'configure' in request.POST:
      form = ConfigForm(request.POST)
      if form.is_valid():
        state = 'configured'
        amc13N = form.cleaned_data['amc13_choice']
        amcN = form.cleaned_data['amc_list']
        trigger_type = form.cleaned_data['trigger_type']
        if trigger_type == 'local':
          lt=True
        else:
          lt=False
        trigger_rate = int(form.cleaned_data['trigger_rate'])
        verbosity = int(form.cleaned_data['verbosity'])
        uhal.setLogLevelTo(uhal.LogLevel.ERROR)
        #configure GLIB. Currently supports only one GLIB
        m_AMCmanager.connect(amcN)
        m_AMCmanager.reset()
        m_AMC13manager.connect(str(amc13N))
        m_AMCmanager.activateGTX()
        m_AMC13manager.configureInputs(str(amcN))
        #m_AMC13manager.configureTrigger()
        m_AMC13manager.configureTrigger(True,2,1,int(trigger_rate),0)
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
        with open("webdaq/templates/amc13status.html", "w") as text_file:
          text_file.write(shtml)
        with open("webdaq/templates/amcstatus.html", "w") as text_file:
          text_file.write(m_AMCmanager.getStatus(verbosity))

    elif 'halt' in request.POST:
      form = ConfigForm()
      m_AMC13manager.connect(amc13N)
      state = 'halted'
    elif 'run' in request.POST:
      print "running"
      form = ConfigForm()
      nevents = int(request.POST['nevents'])
      m_AMC13manager.startDataTaking("/home/mdalchen/work/tmp/testdjango.dat",nevents)
      status = m_AMC13manager.device.getStatus()
      status.SetHTML()
      # Create pipe and dup2() the write end of it on top of stdout, saving a copy
      # of the old stdout
      out = OutputGrabber()
      out.start()
      status.Report(verbosity)
      out.stop()
      shtml = out.capturedtext
      with open("webdaq/templates/amc13status.html", "w") as text_file:
        text_file.write(shtml)
      with open("webdaq/templates/amcstatus.html", "w") as text_file:
          text_file.write(m_AMCmanager.getStatus(verbosity))
      state = 'configured'
  else:
    form = ConfigForm()
    state = 'halted'
  return render(request, 'gemsupervisor.html',{'form':form,
                                               'state':state,
                                               'amc13N':amc13N})
