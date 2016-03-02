from django.shortcuts import render
from webdaq.forms import *
from ldqm_db.models import *
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

state = 'halted'
m_AMC13manager = AMC13manager()
m_AMCmanager = AMCmanager()
verbosity = 1

def gemsupervisor(request):
  global state
  global m_AMC13manager
  global m_AMCmanager
  global verbosity

  if request.POST:
    if 'configure' in request.POST:
      form = ConfigForm(request.POST)
      if form.is_valid():
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
        try:
          m_AMCmanager.connect(amcN)
          m_AMCmanager.reset()
          m_AMC13manager.connect(str(amc13N))
          m_AMCmanager.activateGTX()
          # retrieve VFAT slot numberd and ChipIDs from HW
          chipids = m_AMCmanager.getVFATs(0)
          # retrieve VFAT slot numberd and ChipIDs from DB
          vfats = VFAT.objects.all()
          # Check if the VFATs are in DB, add if not
          for chip in chipids.keys():
            t_chipid = "0x%04x"%(chipids[chip])
            if t_chipid in vfats.filter(Slot=chip).values_list("ChipID", flat=True):
              pass
            else:
              print "Adding VFAT(ChipID = %s, Slot = %d)"%(t_chipid,chip)
              v = VFAT(ChipID = t_chipid, Slot = chip)
              v.save()

          gebs = GEB.objects.all().values_list("ChamberID", flat=True)
          print gebs
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
          state = 'configured'
        except ValueError,e:
          print colors.YELLOW,e,colors.ENDC
          state = 'halted'
    elif 'halt' in request.POST:
      form = ConfigForm()
      m_AMC13manager.reset()
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
                                               'state':state})
