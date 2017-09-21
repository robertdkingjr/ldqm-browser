from django.http import HttpResponse
from django.shortcuts import render
from ldqm_db.models import Run, AMC, GEB, VFAT, HWstate, SystemState
from django.views.generic import ListView, DetailView, CreateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from bugtracker.models import Ticket
from django.template import Template, Context
from django.contrib.staticfiles.templatetags.staticfiles import static
from helper import *
import os
import csv

DEBUG = True

slot_list = ['00','01','02','03','04','05','06','07',
             '08','09','10','11','12','13','14','15',
             '16','17','18','19','20','21','22','23'];

#vfat_address = []; #hex ID
#csvfilename = os.getenv('BUILD_HOME')+'/cmsgemos/gemreadout/data/slot_table.csv'
#with open(csvfilename, 'rd') as csvfile:
#  vfat_ids = csv.reader(csvfile, delimiter=',')
#  for num in vfat_ids:
#      vfat_address.extend(num)

vfat_address = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]; #hex ID

def getVFATSlots(crate,amc,geb):

    # Find correct GEB, add associated VFATs to vfat_address
    try:
        AMC = crate.amcs.get(BoardID=amc)
        #check here
        GEB = AMC.gebs.get(ChamberID=geb)
        VFATs = GEB.vfats.all()
    except:
        print "Error accessing database for run:",run.Name

    for VFAT in VFATs:
        vfat_address[VFAT.Slot] = VFAT.ChipID

    return vfat_address

def getChamberStates(run):
    amc_color = []
    geb_color = []
    for i, amc in enumerate(run.ConfigTag.amcs.all()):
        amc_color.insert(i,'default')
        geb_color.insert(i,['default','default']) 

    try:
        state = run.State
        amc_state = state.amcStates.all()
        geb_state = state.gebStates.all()
    except:
        if DEBUG: print "Could not locate AMC/GEB states for",run.Name,"in Database"
        return amc_color,geb_color
    
    for i, amc in enumerate(run.ConfigTag.amcs.all()):
        try:
            code = int(next((x for x in amc_state if x.HWID==amc.BoardID),None).State)
            del amc_color[i]
            if code==0: amc_color.insert(i,'success')
            elif code==1: amc_color.insert(i,'warning')
            elif code==9: amc_color.insert(i,'default')
            elif code==3: amc_color.insert(i,'danger')
            else: amc_color.insert(i,'danger')
        except:
            if DEBUG: print "Error locating AMC: ", amc.BoardID, amc.Type
        for j, geb in enumerate(amc.gebs.all()):
            try:
                code = int(next((x for x in geb_state if x.HWID==geb.ChamberID),None).State)
                del geb_color[i][j]
                if code==0: geb_color[i].insert(j,'success')
                elif code==1: geb_color[i].insert(j,'warning')
                elif code==9: geb_color[i].insert(j,'default')
                elif code==3: geb_color[i].insert(j,'danger')
                else: geb_color[i].insert(j,'danger')
            except:
                if DEBUG: print "Error locating GEB: ", geb.ChamberID, geb.Type
    return amc_color,geb_color

def getVFATStates(run,crate,amc,geb):
    vfats = []
    vfat_address = getVFATSlots(crate,amc,geb)
    for s in slot_list: #initialize vfats to work if no states in DB
      vfats.insert(int(s),[s, vfat_address[int(s)], 0, 'default', False])

#    for amc in run.amcs.all():
#      for geb in amc.gebs.all():
#	vfat_address=getVFATSlots(geb)
#	for s in slot_list: #initialize vfats to work if no states in DB
#	  vfats.insert(int(s),[s, vfat_address[int(s)], 0, 'default', False])

    try:
        state = run.State
        vfat_state = state.vfatStates.all()
    except:
        if DEBUG: print "Could not locate VFAT states for",run.Name,"in Database"
        return vfats
 
    for s in slot_list:
        try:
            code = int(next((x for x in vfat_state if x.HWID==vfat_address[int(s)]),None).State)
            del vfats[int(s)]          

            #0 = Good,green
            if code==0: vfats.insert(int(s),[s, vfat_address[int(s)], code, 'success', False])

            #1 = Warning,yellow
            elif code==1: vfats.insert(int(s),[s, vfat_address[int(s)], code, 'warning', False])

            #2 = Dead,grey - accessible
            elif code==2: vfats.insert(int(s),[s, vfat_address[int(s)], code, 'default', False])

            #9 = Dead,grey - not accessible
            elif code==9: vfats.insert(int(s),[s, vfat_address[int(s)], code, 'default', True])

            #3,other = Error,red
            elif code==3: vfats.insert(int(s),[s, vfat_address[int(s)], code, 'danger', False])
            else: vfats.insert(int(s),[s, vfat_address[int(s)], code, 'danger', False])


        except:
            print "Error locating state for vfat: ",vfat_address[int(s)]
    
    return vfats
