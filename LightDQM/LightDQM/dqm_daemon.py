import os
from subprocess import call
from webdaq.state_helper import updateStates
from ldqm_db.models import Run

def process_chunk(m_filename, chunk):
  global is_first
  t_filename = m_filename+"_chunk_"+str(chunk)
#call root converter
  call_command =  os.getenv('BUILD_HOME')+'/gem-light-dqm/gemtreewriter/bin/'+os.getenv('XDAQ_OS')+'/'+os.getenv('XDAQ_PLATFORM')+'/unpacker'
  command_args = "/tmp/"+t_filename+".dat sdram"
  call([call_command+' '+command_args],shell=True)
#create dirs in tmp
  for i in range (24):
    call(["mkdir -p /tmp/dqm_hists/%s"%(i)],shell=True)
  call(["mkdir -p /tmp/dqm_hists/OtherData"],shell=True)
  call(["mkdir -p /tmp/dqm_hists/canvases"],shell=True)
#call dqm
  call_command =  os.getenv('BUILD_HOME')+'/gem-light-dqm/dqm-root/bin/'+os.getenv('XDAQ_OS')+'/'+os.getenv('XDAQ_PLATFORM')+'/dqm'
  command_args = "/tmp/"+t_filename+".raw.root"
  os.system(call_command+' '+command_args)
#call hadd if not the first chunk, otherwise rename
  if (chunk > 0):
    call_command = "hadd" 
    command_args = m_filename+".analyzed.root" + t_filename+".analyzed.root"
    os.system(call_command+' '+command_args)
    call(["rm "+ t_filename+".analyzed.root"],shell=True)
  else:
    call(["mv "+ t_filename+".analyzed.root" + " " + m_filename+".analyzed.root"],shell=True)

#call dqm printer
  call_command =  os.getenv('BUILD_HOME')+'/gem-light-dqm/dqm-root/bin/'+os.getenv('XDAQ_OS')+'/'+os.getenv('XDAQ_PLATFORM')+'/gtprinter'
  command_args = "/tmp/"+m_filename+".analyzed.root"
  os.system(call_command+' '+command_args)

#update AMC/GEB/VFAT states
  command_args = "/tmp/"+m_filename+".analyzed.root"
  print 'Updating HW states...'
  updateStates(command_args)
  print 'States updated!'

#copy results to DQM display form
  call_command = os.getenv('LDQM_STATIC')+'/'
  call(["mkdir -p "+call_command],shell=True)
  call(["cp -r /tmp/"+m_filename+" "+call_command],shell=True)

def run_dqm():
  chunk = 0
  run = Run.objects.order_by('-id')[0]
  fname_base = run.Name
  while True:
    fname = fname_base+"_chunk_"+str(chunk)+".dat"
    file_exist = os.path.isfile(fname) 
    if file_exist:
      process_chunk(fname_base, chunk)
      chunk +=1

