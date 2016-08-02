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
import csv
import ROOT


address_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]; #hex ID

#Updates GEB/AMC states for run from Error/Warning histograms
def updateStates(rootFilename):
    rootFile = ROOT.TFile(rootFilename,"READ")
    runName = rootFilename[rootFilename.rfind('run',0,len(rootFilename)):-14]
    print 'Run Name:',runName
    run = Run.objects.get(Name=runName)
    if not run:
        print "Could not locate %s in database"%runName
        return

    systemState = run.State

    if not systemState:
        newSystemState = SystemState()
        newSystemState.save()
        systemState = newSystemState
        systemState.run_set.add(run)

    #print 'Locating error/warning histograms'
    for path,hist in getEWHists(rootFile): #one hist at a time
        # print 'path:',path
        # print 'hist:',hist

        entries = int(hist.GetEntries())
    
        vfatSlot,geb,amc = parsePath(path,hist.GetName())
        # print 'VFAT Slot:',vfatSlot
        # print 'GEB:',geb
        # print 'AMC:',amc
        
        geb = 'GTX-'+str(geb)
        amc = 'AMC-'+str(amc)

        newState = 0
        if entries>0:
            if hist.GetName() == "Warnings": newState = 1
            if hist.GetName() == "Errors": newState = 3
        # print "New State:",newState
            
        #Check if HWStates in DB



        # 0 = Good  (Green)
        # 1 = Warn  (Yellow)
        # 2 = Dead  (Grey)
        # 3 = Error (Red)
        # 9 = Disabled

        if vfatSlot > -1: #VFAT Error/Warning histogram
            vfatID = parseVFATSlot(run,vfatSlot,geb,amc)
            # print 'VFAT ID:',vfatID
            if not systemState.vfatStates.filter(HWID=vfatID):
                vhws = HWstate(HWID=vfatID,State=newState)
                print vfatID,'-->',newState
                vhws.save()
                systemState.vfatStates.add(vhws)
            else:
                vhws = systemState.vfatStates.get(HWID=vfatID)
                if int(vhws.State) < newState:
                    print vfatID,vhws.State,'-->',newState
                    vhws.State = newState
                    vhws.save()
            if not systemState.amcStates.filter(HWID=amc):
                ahws = HWstate(HWID=amc, State=newState)
                print amc,'-->',newState
                ahws.save()
                systemState.amcStates.add(ahws)
            else:
                ahws = systemState.amcStates.get(HWID=amc)
                if int(ahws.State) < newState:
                    print amc,ahws.State,'-->',newState
                    ahws.State = newState
                    ahws.save()
            if not systemState.gebStates.filter(HWID=geb):
                ghws = HWstate(HWID=geb, State=newState)
                print geb,'-->',newState
                ghws.save()
                systemState.gebStates.add(ghws)
            else:
                ghws = systemState.gebStates.get(HWID=geb)
                if int(ghws.State) < newState:
                    print geb,ghws.State,'-->',newState
                    ghws.State = newState
                    ghws.save()
        else: #GEB/AMC Error/Warning histogram
            if not systemState.amcStates.filter(HWID=amc):
                ahws = HWstate(HWID=amc, State=newState)
                print amc,'-->',newState
                ahws.save()
                systemState.amcStates.add(ahws)
            else:
                # print 'Getting existing AMC system state:',amc
                ahws = systemState.amcStates.get(HWID=amc)
                # print 'ahws.State:',ahws.State
                # print 'newState:',newState
                if int(ahws.State) < newState:
                    # print 'Updating with new state!'
                    print amc,ahws.State,'-->',newState
                    ahws.State = newState
                    ahws.save()
            if not systemState.gebStates.filter(HWID=geb):
                ghws = HWstate(HWID=geb, State=newState)
                print geb,'-->',newState
                ghws.save()
                systemState.gebStates.add(ghws)
            else:
                ghws = systemState.gebStates.get(HWID=geb)
                if int(ghws.State) < newState:
                    print geb,ghws.State,'-->',newState
                    ghws.State = newState
                    ghws.save()




# Fill address list with info from database
def parseVFATSlot(run,slot,geb,amc):
    thisAMC = run.amcs.get(BoardID=amc)
    thisGEB = thisAMC.gebs.get(ChamberID=geb)
    thisVFATID = thisGEB.vfats.get(Slot=slot)
    return thisVFATID

#Recursively returns histograms with title Errors or Warnings and path
def getEWHists(source, basepath="/"):
    for key in source.GetListOfKeys():
        kname = key.GetName()
        if key.IsFolder():
	        for i in getEWHists(source.Get(kname), basepath+kname+"/"):
		        yield i 
        else:
            if kname == "Errors" or kname == "Warnings":
                yield basepath+kname, source.Get(kname)


# Return VFAT,GEB,AMC numbers (-1 if not present) 
def parsePath(path,ending):
    done = False
    vfat = -1
    geb = -1
    amc = -1
    dividerchar = path[path.find(ending)-1:path.find(ending)]
    while not done:
        lastDiv = path.rfind(dividerchar,0,len(path))
        secondtolastDiv = path.rfind(dividerchar,0,lastDiv)
        hardware = path[secondtolastDiv+1:lastDiv]
        path = path[:secondtolastDiv+1]
        if "AMC13" in hardware:
            done = True
        elif "AMC" in hardware:
            amc = int(hardware[4:])
        elif "GTX" in hardware or "GEB" in hardware:
            geb = int(hardware[4:])
        elif "VFAT" in hardware:
            vfat = int(hardware[5:])
    return vfat,geb,amc
