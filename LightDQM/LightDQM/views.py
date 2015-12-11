from django.http import HttpResponse
from django.shortcuts import render

slot_list = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23];
hist_list = ["2D CRC for VFAT chip Slot",
             "Strips fired for VFAT chip Slot",
             "Channels fired for VFAT chip Slot"];
hist_list_long = ['CRC.png', 
                  'Channels fired for VFAT chip Slot15.png', 
                  '2D CRC for VFAT chip Slot13.png', 
                  'Strips fired for VFAT chip Slot14.png', 
                  'Strips fired for VFAT chip Slot6.png', 
                  '2D CRC for VFAT chip Slot8.png', 
                  'VFAT chip Slot5 fired per event.png', 
                  'VFAT chip Slot20 fired per event.png', 
                  '2D CRC for VFAT chip Slot2.png', 
                  'Strips fired for VFAT chip Slot3.png', 
                  'Channels fired for VFAT chip Slot5.png', 
                  '2D CRC for VFAT chip Slot20.png', 
                  'Channels fired for VFAT chip Slot4.png', 
                  'VFAT chip Slot18 fired per event.png', 
                  '2D CRC for VFAT chip Slot11.png', 
                  'VFAT chip Slot4 fired per event.png', 
                  'Channels fired for VFAT chip Slot17.png', 
                  'Channels fired for VFAT chip Slot8.png', 
                  'Strips fired for VFAT chip Slot17.png', 
                  '2D CRC for VFAT chip Slot19.png', 
                  'Strips fired for VFAT chip Slot22.png', 
                  '2D CRC for VFAT chip Slot10.png', 
                  'Channels fired for VFAT chip Slot14.png', 
                  'Channels fired for VFAT chip Slot3.png', 
                  'Strips fired for VFAT chip Slot4.png', 
                  'Strips fired for VFAT chip Slot23.png', 
                  'VFAT chip Slot17 fired per event.png', 
                  'Channels fired for VFAT chip Slot16.png', 
                  'Channels fired for VFAT chip Slot18.png', 
                  'VFAT chip Slot13 fired per event.png', 
                  'Strips fired for VFAT chip Slot21.png', 
                  'Strips fired for VFAT chip Slot2.png', 
                  'Channels fired for VFAT chip Slot9.png', 
                  'Strips fired for VFAT chip Slot20.png', 
                  'Cluster multiplicity.png', 
                  '2D CRC for VFAT chip Slot1.png', 
                  'Channels fired for VFAT chip Slot22.png', 
                  'Strips fired for VFAT chip Slot10.png', 
                  'Strips fired for VFAT chip Slot18.png', 
                  '2D CRC for VFAT chip Slot18.png', 
                  'Channels fired for VFAT chip Slot0.png', 
                  'Number of bad VFAT blocks in event.png', 
                  'VFAT chip Slot19 fired per event.png', 
                  'Channels fired for VFAT chip Slot6.png', 
                  'CRC_{calc} vs CRC_{VFAT}.png', 
                  '2D CRC for VFAT chip Slot7.png', 
                  'VFAT chip Slot1 fired per event.png', 
                  '2D CRC for VFAT chip Slot14.png', 
                  'VFAT chip Slot2 fired per event.png', 
                  'Channels not fired per event.png', 
                  'ChipID.png', 'Flag.png', 
                  'Control Bits 1010.png', 
                  'Strips fired for VFAT chip Slot11.png', 
                  'Cluster size.png', 
                  '2D CRC for VFAT chip Slot23.png', 
                  'Difference of BX and BC.png', 
                  'VFAT chip Slot3 fired per event.png', 
                  'Channels fired for VFAT chip Slot2.png', 
                  '2D CRC for VFAT chip Slot9.png', 
                  'Control Bits 1100.png', 
                  'Channels fired for VFAT chip Slot10.png', 
                  '2D CRC for VFAT chip Slot16.png', 
                  'Channels fired for VFAT chip Slot12.png', 
                  'VFAT chip Slot16 fired per event.png', 
                  'CRC_Diff.png', 
                  'Channels fired for VFAT chip Slot1.png', 
                  'VFAT chip Slot10 fired per event.png', 
                  'VFAT chip Slot8 fired per event.png', 
                  'Strips fired for VFAT chip Slot16.png', 
                  'VFAT chip Slot6 fired per event.png', 
                  'VFAT chip Slot7 fired per event.png', 
                  'Strips fired for VFAT chip Slot15.png', 
                  'Beam Profile.png', 
                  '2D CRC for VFAT chip Slot12.png', 
                  '2D CRC for VFAT chip Slot22.png', 
                  'Strips.png', 'VFAT slot number.png', 
                  'Strips fired for VFAT chip Slot13.png', 
                  'Strips fired for VFAT chip Slot1.png', 
                  'Channels fired per event.png', 
                  '2D CRC for VFAT chip Slot4.png', 
                  '2D CRC for VFAT chip Slot6.png', 
                  'VFAT chip Slot14 fired per event.png', 
                  '2D CRC for VFAT chip Slot5.png', 
                  'VFAT chip Slot22 fired per event.png', 
                  'Channels fired for VFAT chip Slot13.png', 
                  'Strips fired for VFAT chip Slot19.png', 
                  'Strips fired for VFAT chip Slot8.png', 
                  'Channels fired for VFAT chip Slot23.png', 
                  'Strips fired for VFAT chip Slot12.png', 
                  'Ratio of BX and BC.png', 
                  '2D CRC for VFAT chip Slot17.png', 
                  'Number VFAT blocks per event.png', 
                  'VFAT chip Slot11 fired per event.png', 
                  '2D CRC for VFAT chip Slot21.png', 
                  'VFAT chip Slot9 fired per event.png', 
                  'VFAT chip Slot12 fired per event.png', 
                  'Channels fired for VFAT chip Slot21.png', 
                  'Number of good VFAT blocks in event.png', 
                  'Channels fired for VFAT chip Slot7.png', 
                  '2D CRC for VFAT chip Slot3.png', 
                  'VFAT chip Slot15 fired per event.png', 
                  'Channels fired for VFAT chip Slot19.png', 
                  'Channels fired for VFAT chip Slot20.png', 
                  'VFAT chip Slot23 fired per event.png', 
                  'Channels fired for VFAT chip Slot11.png', 
                  'Strips fired for VFAT chip Slot0.png', 
                  'Strips fired for VFAT chip Slot7.png', 
                  'Control Bits 1110.png', 
                  'VFAT chip Slot0 fired per event.png', 
                  'VFAT chip Slot21 fired per event.png', 
                  'Strips fired for VFAT chip Slot9.png', 
                  '2D CRC for VFAT chip Slot15.png', 
                  '2D CRC for VFAT chip Slot0.png', 
                  'Strips fired for VFAT chip Slot5.png']

def hello(request):
  return HttpResponse('Hello world')

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
def main(request):
  return render(request,'chambers.html')

def chamber(request):
  if 'selectSlot' in request.GET:
    slot=int(request.GET['selectSlot'])
    dqm_canvases_active=False
  else: 
    slot = 0
    dqm_canvases_active=False
  return render(request,'chambers.html', {'selected_slot':int(slot), 
                                            'slot_list':slot_list,
                                            'hist_list':hist_list,
                                            'dqm_canvases_active':dqm_canvases_active})
