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


lslot_list = ["a","b","c","d"];

hist_list = ["b1010",
             "b1100",
             "b1110",
             "BC",
             "EC",
             "SlotN",
             "Flag",
             "ChipID",
             "FiredChannels",
             "crc",
             "crc_calc",
             "Warnings",
             "Errors",
             "latencyScan",
             "thresholdScan"];

threshold_channels = range(0,127);

amc13_hist_list = ["Control_Bit5",
                   "Control_BitA",
                   "Evt_ty",
                   "LV1_id",
                   "Bx_id",
                   "Source_id",
                   "CalTyp",
                   "nAMC",
                   "OrN",
                   "CRC_amc13",
                   "Blk_Not",
                   "LV1_idT",
                   "BX_idT",
                   "EvtLength",
                   "CRC_cdf"];
amc_hist_list = ["AMCnum",
                 "L1A",
                 "BX",
                 "Dlength",
                 "FV",
                 "Rtype",
                 "Param1",
                 "Param2",
                 "Param3",
                 "Onum",
                 "BID",
                 "GEMDAV",
                 "Bstatus",
                 "GDcount",
                 "Tstate",
                 "ChamT",
                 "OOSG",
                 "CRC",
                 "L1AT",
                 "DlengthT"];

geb_hist_list = ["Errors",
                 "InputID",
                 "OHCRC",
                 "Vwh",
                 "Vwt",
                 "Warnings",
                 "ZeroSup",
                 "BeamProfile"];

sum_can_list  = ["integrity", "occupancy", "clusterMult", "clusterSize"];


def dqm_help(request):
  return render(request,'test.html', {'hist_list':hist_list,})

def runs(request):
  run_list = Run.objects.all()
  return render(request,'runs.html', {'run_list':run_list,})

def main(request):
  run_list = Run.objects.all()
  return render(request,'main.html', {'run_list':run_list,})

def report(request, runStation, runN):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
  
  amc_color,geb_color = getChamberStates(run)

  
  return render(request,'report.html', {'run_list':run_list,
                                        'hist_list':hist_list,
                                        'run':run,
                                        'amc_color':amc_color,
                                        'geb_color':geb_color})


def chamber(request, runStation, runN):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)

  amc_color,geb_color = getChamberStates(run)
  
  return render(request,'chambers.html', {'run_list':run_list,
                                          'slot_list':slot_list,
                                          'hist_list':hist_list,
                                          'run':run,
                                          'amc_color':amc_color,
                                          'geb_color':geb_color})

def amc_13(request, runStation, runN):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
  
  amc_color,geb_color = getChamberStates(run)


  return render(request,'amc_13.html', {'run_list':run_list,
                                        'slot_list':slot_list,
                                        'hist_list':hist_list,
                                        'amc13_hist_list':amc13_hist_list,
                                        'run':run,
                                        'sum_can_list':sum_can_list,
                                        'amc_color':amc_color,
                                        'geb_color':geb_color})

def display_amc_13(request, runStation, runN, hist):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
 
  amc_color,geb_color = getChamberStates(run)

  return render(request,'display_amc_13.html', {'run_list':run_list,
                                        'slot_list':slot_list,
                                        'hist_list':hist_list,
                                        'amc13_hist_list':amc13_hist_list,
                                        'hist':hist,
                                        'run':run,
                                        'sum_can_list':sum_can_list,
                                        'amc_color':amc_color,
                                        'geb_color':geb_color})

def amc(request, runStation, runN, amc_boardid):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
  
  amc_color,geb_color = getChamberStates(run)


  return render(request,'amc.html', {'run_list':run_list,
                                     'slot_list':slot_list,
                                     'hist_list':hist_list,
                                     'amc_hist_list':amc_hist_list,
                                     'run':run,
                                     'amc_boardid':amc_boardid,
                                     'sum_can_list':sum_can_list,
                                     'amc_color':amc_color,
                                     'geb_color':geb_color})

def display_amc(request, runStation, runN, amc_boardid, hist):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
  
  amc_color,geb_color = getChamberStates(run)
 
  return render(request,'display_amc.html', {'run_list':run_list,
                                     'slot_list':slot_list,
                                     'hist_list':hist_list,
                                     'amc_hist_list':amc_hist_list,
                                     'run':run,
                                     'hist':hist,
                                     'amc_boardid':amc_boardid,
                                     'sum_can_list':sum_can_list,
                                     'amc_color':amc_color,
                                     'geb_color':geb_color})



def gebs(request, runStation, runN, amc_boardid, geb_chamberid):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
  
  amc_color,geb_color = getChamberStates(run)
  vfats = getVFATStates(run,amc_boardid,geb_chamberid)
  
  return render(request,'gebs.html', {'run_list':run_list,
                                      'slot_list':slot_list,
                                      'hist_list':hist_list,
                                      'geb_hist_list':geb_hist_list,
                                      'run':run,
                                      'amc_boardid':amc_boardid,
                                      'geb_chamberid':geb_chamberid,
                                      'sum_can_list':sum_can_list,
                                      'amc_color':amc_color,
                                      'geb_color':geb_color,
                                      'vfats':vfats})

def display_geb(request, runStation, runN, amc_boardid, geb_chamberid, hist):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
  amc_color,geb_color = getChamberStates(run)
  vfats = getVFATStates(run,amc_boardid,geb_chamberid)

  return render(request,'display_geb.html', {'run_list':run_list,
                                      'slot_list':slot_list,
                                      'hist_list':hist_list,
                                      'geb_hist_list':geb_hist_list,
                                      'hist':hist,
                                      'run':run,
                                      'amc_boardid':amc_boardid,
                                      'geb_chamberid':geb_chamberid,
                                      'sum_can_list':sum_can_list,
                                      'amc_color':amc_color,
                                      'geb_color':geb_color,
                                      'vfats':vfats})


def vfats(request, runStation, runN, amc_boardid, geb_chamberid, vfatN):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
  amc_color,geb_color = getChamberStates(run)
  vfats = getVFATStates(run,amc_boardid,geb_chamberid)

  selected_vfat = vfats[int(vfatN)]
  return render(request,'vfats.html', {'run_list':run_list,
                                       'slot_list':slot_list,
                                       'hist_list':hist_list,
                                       'geb_hist_list':geb_hist_list,
                                       'threshold_channels':threshold_channels,
                                       'run':run,
                                       'amc_boardid':amc_boardid,
                                       'geb_chamberid':geb_chamberid,
                                       'vfat':int(vfatN),
                                       'sum_can_list':sum_can_list,
                                       'vfats':vfats,
                                       'selected_vfat':selected_vfat,
                                       'amc_color':amc_color,
                                       'geb_color':geb_color})

def summary(request, runStation, runN, chamber, summaryN):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
  amc_color,geb_color = getChamberStates(run)

  return render(request,'summary.html', {'run_list':run_list,
                                         'slot_list':slot_list,
                                         'hist_list':hist_list,
                                         'geb_hist_list':geb_hist_list,
                                         'run':run,
                                         'chamber':chamber,
                                         'sum_can_list':sum_can_list,
                                         'sumN':summaryN,
                                         'amc_color':amc_color,
                                         'geb_color':geb_color})

def display_vfat(request, runStation, runN, amc_boardid, geb_chamberid, vfatN, histN):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)  
  
  amc_color,geb_color = getChamberStates(run)
  vfats = getVFATStates(run,amc_boardid,geb_chamberid)
  
  selected_vfat = vfats[int(vfatN)]

  return render(request,'display_vfat.html', {'run_list':run_list,
                                              'slot_list':slot_list,
                                              'hist_list':hist_list,
                                              'geb_hist_list':geb_hist_list,
                                              'run':run,
                                              'amc_boardid':amc_boardid,
                                              'geb_chamberid':geb_chamberid,
                                              'sum_can_list':sum_can_list,
                                              'vfat':int(vfatN),
                                              'hist':histN,
                                              'vfats':vfats,
                                              'selected_vfat':selected_vfat,
                                              'amc_color':amc_color,
                                              'geb_color':geb_color})


def display_canvas(request, runStation, runN, amc_boardid, geb_chamberid, canvas):
  run_list = Run.objects.all()
  run = Run.objects.get(Station=runStation, Number = runN)
  
  amc_color,geb_color = getChamberStates(run)
  vfats = getVFATStates(run,amc_boardid,geb_chamberid)

  return render(request,'display_canvas.html', {'run_list':run_list,
                                                'slot_list':slot_list,
                                                'hist_list':hist_list,
                                                'geb_hist_list':geb_hist_list,
                                                'run':run,
                                                'amc_boardid':amc_boardid,
                                                'geb_chamberid':geb_chamberid,
                                                'chamber':chamber,
                                                'sum_can_list':sum_can_list,
                                                'canvas':canvas,
                                                'vfats':vfats,
                                                'amc_color':amc_color,
                                                'geb_color':geb_color})


class BugListView(ListView):
    model = Ticket
    template_name = 'list.html'

class BugDetailView(DetailView):
    model = Ticket
    template_name = 'detail.html'

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('index')

class BugCreateView(CreateView):
    model = Ticket
    template_name = 'add.html'
    fields = ['title', 'text']
    success_url = reverse_lazy('index')

def form_valid(self, form):
        form.instance.user = self.request.user
        return super(BugCreateView, self).form_valid(form)

