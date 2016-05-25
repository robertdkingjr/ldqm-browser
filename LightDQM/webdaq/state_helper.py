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
import datetime
from subprocess import call
from time import sleep
import os
import sys
import threading
import ROOT
import csv


#Updates GEB/AMC states for run from Error/Warning histograms
def updateStates(rootFilename):
    print 'Creating new system state'
    newSystemState = SystemState()
    newSystemState.save()
    rootFile = ROOT.TFile(rootFilename,"READ")
    print 'Locating error/warning histograms'
    for path,hist in getEWHists(rootFile): #one hist at a time
        entries = int(hist.GetEntries())
        print hist.ClassName(), path
        print "Entries", entries
        #for bin in range(hist.GetNbinsX()): #check each bin
            #print bin,":",hist.GetBinContent(bin)
        amc13=path[path.find('AMC13'):path.find('AMC13')+7]
        if path[path.rfind('AMC')+6]=='/': #2 digit AMC#
            amc = path[path.rfind('AMC'):path.rfind('AMC')+6]
        else: #1 digit AMC#
            amc = path[path.rfind('AMC'):path.rfind('AMC')+5]
        geb = path[path.find('GTX'):path.find('GTX')+5]

        newState = 0
        if entries>0: 
            if hist.GetName() == "Warnings": newState = 1
            if hist.GetName() == "Errors": newState = 3
        print "New State:",newState

        #Check if HWStates in DB
        if not HWstate.objects.filter(HWID=amc,State=newState):
            print "Adding AMC State to DB"
            ahws = HWstate(HWID=amc, State=newState)
            ahws.save()
        else:
            print 'AMC state already exists. Adding...'
            ahws = HWstate.objects.get(HWID=amc,State=newState)
        newSystemState.amcStates.add(ahws)
        print 'AMC state added to new system state'
        if not HWstate.objects.filter(HWID=geb,State=newState):
            print "Adding GEB State to DB"
            ghws = HWstate(HWID=geb, State=newState)
            ghws.save()   
        else:
            print 'GEB state already exists. Adding...'
            ghws = HWstate.objects.get(HWID=geb,State=newState)
        newSystemState.gebStates.add(ghws)
        print 'GEB state added to new system state'

        parseVFATs(newSystemState)
    
    #Add new state to run in DB
    print 'Adding new system state to run in DB'
    runName_start = rootFilename.find('run')
    runName_end = rootFilename.find('.',runName_start)
    runName = rootFilename[runName_start:runName_end]
    print 'runName',runName
    run = Run.objects.get(Name=runName)
    if run:
        print 'Found run, adding new system state'
        newSystemState.run_set.add(run)
        #run.State.add(newSystemState,False,False)
    else:
        print "Could not locate Run %s in database"%runName
        

def parseVFATs(system_state):
    vfat_table = '/home/kingr/ldqm-browser/LightDQM/LightDQM/test/config/slot_table_TAMUv2.csv'
    with open(vfat_table, 'rd') as csvfile:
        vfat_ids = csv.reader(csvfile, delimiter=',')
        for line in vfat_ids:
            for address in line:
                print address
                if 'dead' in address: newState=2
                else: newState=0
                if not HWstate.objects.filter(HWID=address,State=newState):
                    print "Adding VFAT State to DB"
                    vhws = HWstate(HWID=address, State=newState)
                    vhws.save()
                else:
                    print 'VFAT state already exists. Adding...'
                    vhws = HWstate.objects.get(HWID=address,State=newState)
                system_state.vfatStates.add(vhws)
                print 'VFAT state %s added to new system state'%str(address)



#Recursively returns histograms with title Errors or Warnings and path
def getEWHists(source, basepath="/"):
    for key in source.GetListOfKeys():
        kname = key.GetName()
        if key.IsFolder():
            for i in getEWHists(source.Get(kname), basepath+kname+"/"):
                yield i
        else:
            if kname == "Errors" or kname=="Warnings":
                yield basepath+kname, source.Get(kname)
