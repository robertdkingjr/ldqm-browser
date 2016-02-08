from django.http import HttpResponse
from django.shortcuts import render
from ldqm_db.models import Run, AMC, GEB
from django.views.generic import ListView, DetailView, CreateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from bugtracker.models import Ticket

slot_list = ['00','01','02','03','04','05','06','07','08','09','10','11',
             '12','13','14','15','16','17','18','19','20','21','22','23'];
lslot_list = ["a","b","c","d"];
hist_list = ["2D CRC for VFAT chip Slot",
             "Strips fired for VFAT chip Slot",
             "Channels fired for VFAT chip Slot"];
sum_can_names  = ["integrity", "occupancy", "clusterMult", "clusterSize"];
hist_list_long = ['CRC', 
                  'Channels_fired_for_VFAT_chip_Slot15',
                  'CRC_2D_for_VFAT_chip_Slot13',
                  'Strips_fired_for_VFAT_chip_Slot14',
                  'Strips_fired_for_VFAT_chip_Slot6',
                  'CRC_2D_for_VFAT_chip_Slot8',
                  'VFAT_chip_Slot5_fired_per_event',
                  'VFAT_chip_Slot20_fired_per_event',
                  'CRC_2D_for_VFAT_chip_Slot2',
                  'Strips_fired_for_VFAT_chip_Slot3',
                  'Channels_fired_for_VFAT_chip_Slot5',
                  'CRC_2D_for_VFAT_chip_Slot20',
                  'Channels_fired_for_VFAT_chip_Slot4',
                  'VFAT_chip_Slot18_fired_per_event',
                  'CRC_2D_for_VFAT_chip_Slot11',
                  'VFAT_chip_Slot4_fired_per_event',
                  'Channels_fired_for_VFAT_chip_Slot17',
                  'Channels_fired_for_VFAT_chip_Slot8',
                  'Strips_fired_for_VFAT_chip_Slot17',
                  'CRC_2D_for_VFAT_chip_Slot19',
                  'Strips_fired_for_VFAT_chip_Slot22',
                  'CRC_2D_for_VFAT_chip_Slot10',
                  'Channels_fired_for_VFAT_chip_Slot14',
                  'Channels_fired_for_VFAT_chip_Slot3',
                  'Strips_fired_for_VFAT_chip_Slot4',
                  'Strips_fired_for_VFAT_chip_Slot23',
                  'VFAT_chip_Slot17_fired_per_event',
                  'Channels_fired_for_VFAT_chip_Slot16',
                  'Channels_fired_for_VFAT_chip_Slot18',
                  'VFAT_chip_Slot13_fired_per_event',
                  'Strips_fired_for_VFAT_chip_Slot21',
                  'Strips_fired_for_VFAT_chip_Slot2',
                  'Channels_fired_for_VFAT_chip_Slot9',
                  'Strips_fired_for_VFAT_chip_Slot20',
                  'Cluster_multiplicity',
                  'CRC_2D_for_VFAT_chip_Slot1',
                  'Channels_fired_for_VFAT_chip_Slot22',
                  'Strips_fired_for_VFAT_chip_Slot10',
                  'Strips_fired_for_VFAT_chip_Slot18',
                  'CRC_2D_for_VFAT_chip_Slot18',
                  'Channels_fired_for_VFAT_chip_Slot0',
                  'Number_of_bad_VFAT_blocks_in_event',
                  'VFAT_chip_Slot19_fired_per_event',
                  'Channels_fired_for_VFAT_chip_Slot6',
                  'CRC_calc_vs_CRC_VFAT',
                  'CRC_2D_for_VFAT_chip_Slot7',
                  'VFAT_chip_Slot1_fired_per_event',
                  'CRC_2D_for_VFAT_chip_Slot14',
                  'VFAT_chip_Slot2_fired_per_event',
                  'Channels_not_fired_per_event',
                  'ChipID','Flag',
                  'Control_Bits_1010',
                  'Strips_fired_for_VFAT_chip_Slot11',
                  'Cluster_size',
                  'CRC_2D_for_VFAT_chip_Slot23',
                  'Difference_of_BX_and_BC',
                  'VFAT_chip_Slot3_fired_per_event',
                  'Channels_fired_for_VFAT_chip_Slot2',
                  'CRC_2D_for_VFAT_chip_Slot9',
                  'Control_Bits_1100',
                  'Channels_fired_for_VFAT_chip_Slot10',
                  'CRC_2D_for_VFAT_chip_Slot16',
                  'Channels_fired_for_VFAT_chip_Slot12',
                  'VFAT_chip_Slot16_fired_per_event',
                  'CRC_Diff',
                  'Channels_fired_for_VFAT_chip_Slot1',
                  'VFAT_chip_Slot10_fired_per_event',
                  'VFAT_chip_Slot8_fired_per_event',
                  'Strips_fired_for_VFAT_chip_Slot16',
                  'VFAT_chip_Slot6_fired_per_event',
                  'VFAT_chip_Slot7_fired_per_event',
                  'Strips_fired_for_VFAT_chip_Slot15',
                  'Beam_Profile',
                  'CRC_2D_for_VFAT_chip_Slot12',
                  'CRC_2D_for_VFAT_chip_Slot22',
                  'Strips','VFAT_slot_number',
                  'Strips_fired_for_VFAT_chip_Slot13',
                  'Strips_fired_for_VFAT_chip_Slot1',
                  'Channels_fired_per_event',
                  'CRC_2D_for_VFAT_chip_Slot4',
                  'CRC_2D_for_VFAT_chip_Slot6',
                  'VFAT_chip_Slot14_fired_per_event',
                  'CRC_2D_for_VFAT_chip_Slot5',
                  'VFAT_chip_Slot22_fired_per_event',
                  'Channels_fired_for_VFAT_chip_Slot13',
                  'Strips_fired_for_VFAT_chip_Slot19',
                  'Strips_fired_for_VFAT_chip_Slot8',
                  'Channels_fired_for_VFAT_chip_Slot23',
                  'Strips_fired_for_VFAT_chip_Slot12',
                  'Ratio_of_BX_and_BC',
                  'CRC_2D_for_VFAT_chip_Slot17',
                  'Number_VFAT_blocks_per_event',
                  'VFAT_chip_Slot11_fired_per_event',
                  'CRC_2D_for_VFAT_chip_Slot21',
                  'VFAT_chip_Slot9_fired_per_event',
                  'VFAT_chip_Slot12_fired_per_event',
                  'Channels_fired_for_VFAT_chip_Slot21',
                  'Number_of_good_VFAT_blocks_in_event',
                  'Channels_fired_for_VFAT_chip_Slot7',
                  'CRC_2D_for_VFAT_chip_Slot3',
                  'VFAT_chip_Slot15_fired_per_event',
                  'Channels_fired_for_VFAT_chip_Slot19',
                  'Channels_fired_for_VFAT_chip_Slot20',
                  'VFAT_chip_Slot23_fired_per_event',
                  'Channels_fired_for_VFAT_chip_Slot11',
                  'Strips_fired_for_VFAT_chip_Slot0',
                  'Strips_fired_for_VFAT_chip_Slot7',
                  'Control_Bits_1110',
                  'VFAT_chip_Slot0_fired_per_event',
                  'VFAT_chip_Slot21_fired_per_event',
                  'Strips_fired_for_VFAT_chip_Slot9',
                  'CRC_2D_for_VFAT_chip_Slot15',
                  'CRC_2D_for_VFAT_chip_Slot0',
                  'Strips_fired_for_VFAT_chip_Slot5']

def dqm_help(request):
  return render(request,'test.html', {'hist_list_long':hist_list_long,})

def dqm_canvases(request):
  return render(request, 'dqm_canvases.html')

def all_plots(request):
  
  return render(request, 'all_plots.html', {'slot_list':slot_list, 
                                            'selected_slot':-1})

def chip_plots(request):
  if 'selectSlot' in request.GET:
    slot=int(request.GET['selectSlot'])
  else: slot = -1
  return render(request,'chip_plots.html', {'selected_slot':int(slot), 
                                            'slot_list':slot_list,
                                            'hist_list':hist_list})
#def goto_main(request):

  

def main(request):
  run_list = Run.objects.all()
  return render(request,'main.html', {'run_list':run_list,})

def report(request, runType, runN):
  run_list = Run.objects.all()
  run = Run.objects.get(Type=runType, Number = runN)
  return render(request,'report.html', {'run_list':run_list,
                                        'hist_list':hist_list,
                                        'hist_list_long':hist_list_long,
                                        'run':run})


def chamber(request, runType, runN):
  run_list = Run.objects.all()
  run = Run.objects.get(Type=runType, Number = runN)
  geb_color = "success"

  return render(request,'chambers.html', {'run_list':run_list,
                                          'slot_list':slot_list,
                                          'hist_list':hist_list,
                                          'hist_list_long':hist_list_long,
                                          'run':run,
                                          'geb_color':geb_color}) # <-- Pass this down to child defs

def gebs(request, runType, runN, chamber):
  run_list = Run.objects.all()
  run = Run.objects.get(Type=runType, Number = runN)
  
  color_code = "success"
  # color_code = "warning"
  # color_code = "danger"

  return render(request,'gebs.html', {'run_list':run_list,
                                      'slot_list':slot_list,
                                      'hist_list':hist_list,
                                      'hist_list_long':hist_list_long,
                                      'run':run,
                                      'chamber':chamber,
                                      'sum_can_names':sum_can_names,
                                      'color_code':color_code})

def vfats(request, runType, runN, chamber, vfatN):
  run_list = Run.objects.all()
  run = Run.objects.get(Type=runType, Number = runN)
  color_code = "success"

  return render(request,'vfats.html', {'run_list':run_list,
                                       'slot_list':slot_list,
                                       'hist_list':hist_list,
                                       'hist_list_long':hist_list_long,
                                       'run':run,
                                       'chamber':chamber,
                                       'vfat':int(vfatN),
                                       'sum_can_names':sum_can_names,
                                       'color_code':color_code})

def summary(request, runType, runN, chamber, summaryN):
  run_list = Run.objects.all()
  run = Run.objects.get(Type=runType, Number = runN)
  color_code = "success"

  return render(request,'summary.html', {'run_list':run_list,
                                         'slot_list':slot_list,
                                         'hist_list':hist_list,
                                         'hist_list_long':hist_list_long,
                                         'run':run,
                                         'chamber':chamber,
                                         'sum_can_names':sum_can_names,
                                         'sumN':summaryN,
                                         'color_code':color_code})
def display_vfat(request, runType, runN, chamber, vfatN, histN):
  run_list = Run.objects.all()
  run = Run.objects.get(Type=runType, Number = runN)  
  color_code = "success"

  return render(request,'display_vfat.html', {'run_list':run_list,
                                              'slot_list':slot_list,
                                              'hist_list':hist_list,
                                              'hist_list_long':hist_list_long,
                                              'run':run,
                                              'chamber':chamber,
                                              'sum_can_names':sum_can_names,
                                              'vfat':int(vfatN),
                                              'hist':histN,
                                              'color_code':color_code})

def display_canvas(request, runType, runN, chamber, canvas):
  run_list = Run.objects.all()
  run = Run.objects.get(Type=runType, Number = runN)
  color_code = "success"

  return render(request,'display_canvas.html', {'run_list':run_list,
                                                'slot_list':slot_list,
                                                'hist_list':hist_list,
                                                'hist_list_long':hist_list_long,
                                                'run':run,
                                                'chamber':chamber,
                                                'sum_can_names':sum_can_names,
                                                'canvas':canvas,
                                                'color_code':color_code})


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
