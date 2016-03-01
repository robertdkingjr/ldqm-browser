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

amc13N = 0
state = 'halted'
amcN = u'10'
m_uTCAslot = 160+int(amcN)

ipaddr = '192.168.0.%d'%(m_uTCAslot)
address_table = "file://${GEM_ADDRESS_TABLE_PATH}/glib_address_table.xml"
uri = "chtcp-2.0://localhost:10203?target=%s:50001"%(ipaddr)
m_AMC13manager = AMC13manager()
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
        m_uTCAslot = 160+int(amcN)
        ipaddr = '192.168.0.%d'%(m_uTCAslot)
        address_table = "file://${GEM_ADDRESS_TABLE_PATH}/glib_address_table.xml"
        uri = "chtcp-2.0://localhost:10203?target=%s:50001"%(ipaddr)
        m_glib  = uhal.getDevice( "glib" , uri, address_table )
        writeRegister(m_glib, "GLIB.DAQ.CONTROL", 0x8)# reset GLIB
        m_AMC13manager.connect(str(amc13N))
        writeRegister(m_glib, "GLIB.DAQ.CONTROL", 0x381)# enable both GTX links
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
          text_file.write("-> DAQ control reg :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.CONTROL")))
          text_file.write("-> DAQ status reg  :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.STATUS")))
          text_file.write("-> DAQ GTX NOT_IN_TABLE error counter :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.NOTINTABLE_ERR")))
          text_file.write("-> DAQ GTX dispersion error counter   :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.DISPER_ERR")))
          text_file.write("-> DAQ L1A ID          :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.L1AID")))
          text_file.write("-> DAQ sent events cnt :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.EVT_SENT")))
          text_file.write("-> DAQ DAV_TIMEOUT :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.CONTROL.DAV_TIMEOUT")))
          text_file.write("-> DAQ RUN_TYPE      :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_CONTROL.RUN_TYPE")))
          text_file.write("-> DAQ RUN_PARAMS    :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_CONTROL.RUN_PARAMS")))
          text_file.write("-> DAQ GTX0 corrupted VFAT block counter :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.COUNTERS.CORRUPT_VFAT_BLK_CNT")))
          text_file.write("-> DAQ GTX0 evn :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.COUNTERS.EVN")))
          text_file.write("-> GLIB STATUS 0 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.STATUS")))
          text_file.write("-> GLIB STATUS 1 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.STATUS")))
          text_file.write("-> GLIB MAX_DAV_TIMER :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.MAX_DAV_TIMER")))
          text_file.write("-> GLIB LAST_DAV_TIMER :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.LAST_DAV_TIMER")))
          text_file.write("-> GLIB MAX_DAV_TIMER GTX0:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.DAV_STATS.MAX_DAV_TIMER")))
          text_file.write("-> GLIB LAST_DAV_TIMER GTX0:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.DAV_STATS.LAST_DAV_TIMER")))
          text_file.write("-> GLIB MAX_DAV_TIMER GTX1:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.DAV_STATS.MAX_DAV_TIMER")))
          text_file.write("-> GLIB LAST_DAV_TIMER GTX1:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.DAV_STATS.LAST_DAV_TIMER")))
          text_file.write("-> GLIB DAV_TIMEOUT GTX0:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.DAV_TIMEOUT")))
          text_file.write("-> GLIB DAV_TIMEOUT GTX1:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.DAV_TIMEOUT")))
          text_file.write("===================================================================================== <br>")
          text_file.write("DEBUG INFO <br>")
          text_file.write("===================================================================================== <br>")
          text_file.write("GTX0 <br>")
          text_file.write("-> DAQ debug0 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.0")))
          text_file.write("-> DAQ debug1 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.1")))
          text_file.write("-> DAQ debug2 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.2")))
          text_file.write("-> DAQ debug3 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.3")))
          text_file.write("-> DAQ debug4 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.4")))
          text_file.write("-> DAQ debug5 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.5")))
          text_file.write("-> DAQ debug6 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.6")))
          text_file.write("===================================================================================== <br>")
          text_file.write("DEBUG INFO <br>")
          text_file.write("===================================================================================== <br>")
          text_file.write("GTX1 <br>")
          text_file.write("-> DAQ debug0 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.0")))
          text_file.write("-> DAQ debug1 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.1")))
          text_file.write("-> DAQ debug2 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.2")))
          text_file.write("-> DAQ debug3 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.3")))
          text_file.write("-> DAQ debug4 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.4")))
          text_file.write("-> DAQ debug5 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.5")))
          text_file.write("-> DAQ debug6 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.6")))
          text_file.write("--======================================= <br>")
          text_file.write("-> SSSSSSSSSSSSSSSSSSSSSSBITSSSSSSSSSSSSSS <br>")
          text_file.write("--======================================= <br>")
          text_file.write("-> GTX 0 clusters 01 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0_CLUSTER_01")))
          text_file.write("-> GTX 0 clusters 23 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0_CLUSTER_23")))
          text_file.write("-> GTX 1 clusters 01 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1_CLUSTER_01")))
          text_file.write("-> GTX 1 clusters 23 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1_CLUSTER_23")))
          text_file.write("-> SBIT_RATE :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.SBIT_RATE")))
    elif 'halt' in request.POST:
      form = ConfigForm()
      m_AMC13manager.connect(amc13N)
      state = 'halted'
    elif 'run' in request.POST:
      print "running"
      form = ConfigForm()
      m_glib  = uhal.getDevice( "glib" , uri, address_table )
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
        text_file.write("-> DAQ control reg :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.CONTROL")))
        text_file.write("-> DAQ status reg  :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.STATUS")))
        text_file.write("-> DAQ GTX NOT_IN_TABLE error counter :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.NOTINTABLE_ERR")))
        text_file.write("-> DAQ GTX dispersion error counter   :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.DISPER_ERR")))
        text_file.write("-> DAQ L1A ID          :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.L1AID")))
        text_file.write("-> DAQ sent events cnt :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.EVT_SENT")))
        text_file.write("-> DAQ DAV_TIMEOUT :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.CONTROL.DAV_TIMEOUT")))
        text_file.write("-> DAQ RUN_TYPE      :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_CONTROL.RUN_TYPE")))
        text_file.write("-> DAQ RUN_PARAMS    :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_CONTROL.RUN_PARAMS")))
        text_file.write("-> DAQ GTX0 corrupted VFAT block counter :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.COUNTERS.CORRUPT_VFAT_BLK_CNT")))
        text_file.write("-> DAQ GTX0 evn :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.COUNTERS.EVN")))
        text_file.write("-> GLIB STATUS 0 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.STATUS")))
        text_file.write("-> GLIB STATUS 1 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.STATUS")))
        text_file.write("-> GLIB MAX_DAV_TIMER :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.MAX_DAV_TIMER")))
        text_file.write("-> GLIB LAST_DAV_TIMER :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.EXT_STATUS.LAST_DAV_TIMER")))
        text_file.write("-> GLIB MAX_DAV_TIMER GTX0:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.DAV_STATS.MAX_DAV_TIMER")))
        text_file.write("-> GLIB LAST_DAV_TIMER GTX0:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.DAV_STATS.LAST_DAV_TIMER")))
        text_file.write("-> GLIB MAX_DAV_TIMER GTX1:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.DAV_STATS.MAX_DAV_TIMER")))
        text_file.write("-> GLIB LAST_DAV_TIMER GTX1:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.DAV_STATS.LAST_DAV_TIMER")))
        text_file.write("-> GLIB DAV_TIMEOUT GTX0:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.DAV_TIMEOUT")))
        text_file.write("-> GLIB DAV_TIMEOUT GTX1:0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.DAV_TIMEOUT")))
        text_file.write("===================================================================================== <br>")
        text_file.write("DEBUG INFO <br>")
        text_file.write("===================================================================================== <br>")
        text_file.write("GTX0 <br>")
        text_file.write("-> DAQ debug0 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.0")))
        text_file.write("-> DAQ debug1 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.1")))
        text_file.write("-> DAQ debug2 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.2")))
        text_file.write("-> DAQ debug3 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.3")))
        text_file.write("-> DAQ debug4 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.4")))
        text_file.write("-> DAQ debug5 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.5")))
        text_file.write("-> DAQ debug6 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0.LASTBLOCK.6")))
        text_file.write("===================================================================================== <br>")
        text_file.write("DEBUG INFO <br>")
        text_file.write("===================================================================================== <br>")
        text_file.write("GTX1 <br>")
        text_file.write("-> DAQ debug0 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.0")))
        text_file.write("-> DAQ debug1 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.1")))
        text_file.write("-> DAQ debug2 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.2")))
        text_file.write("-> DAQ debug3 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.3")))
        text_file.write("-> DAQ debug4 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.4")))
        text_file.write("-> DAQ debug5 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.5")))
        text_file.write("-> DAQ debug6 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1.LASTBLOCK.6")))
        text_file.write("--======================================= <br>")
        text_file.write("-> SSSSSSSSSSSSSSSSSSSSSSBITSSSSSSSSSSSSSS <br>")
        text_file.write("--======================================= <br>")
        text_file.write("-> GTX 0 clusters 01 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0_CLUSTER_01")))
        text_file.write("-> GTX 0 clusters 23 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX0_CLUSTER_23")))
        text_file.write("-> GTX 1 clusters 01 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1_CLUSTER_01")))
        text_file.write("-> GTX 1 clusters 23 :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.GTX1_CLUSTER_23")))
        text_file.write("-> SBIT_RATE :0x%08x <br>"%(readRegister(m_glib,"GLIB.DAQ.SBIT_RATE")))
      state = 'configured'



  else:
    form = ConfigForm()
    state = 'halted'
  return render(request, 'gemsupervisor.html',{'form':form,
                                               'state':state,
                                               'amc13N':amc13N})
