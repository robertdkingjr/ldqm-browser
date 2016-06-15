import os
from subprocess import call
from webdaq.state_helper import updateStates
from ldqm_db.models import Run
import time

def process_chunk(m_filename, chunk):
  global is_first
  print "Process chunk with base filename %s\n" %(m_filename)
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
    call_command = "hadd -v 0 " 
    command_args = "/tmp/hadd_tmp.root " + "/tmp/" + m_filename+".analyzed.root" + " " + "/tmp/" + t_filename+".analyzed.root"
    os.system(call_command+' '+command_args)
    call(["rm "+ "/tmp/" + t_filename+".analyzed.root"],shell=True)
    call(["mv "+ "/tmp/hadd_tmp.root " + "/tmp/" + m_filename+".analyzed.root"],shell=True)
    command_args = "/tmp/hadd_tmp.root " + "/tmp/" + m_filename+".raw.root" + " " + "/tmp/" + t_filename+".raw.root"
    os.system(call_command+' '+command_args)
    call(["rm "+ "/tmp/" + t_filename+".raw.root"],shell=True)
    call(["mv "+ "/tmp/hadd_tmp.root " + "/tmp/" + m_filename+".raw.root"],shell=True)
    file('/tmp/add_tmp.dat','wb').write(file("/tmp/" + t_filename+".dat",'rb').read()+file("/tmp/" + m_filename+".dat",'rb').read())
    call(["rm "+ "/tmp/" + t_filename+".dat"],shell=True)
    call(["mv "+ "/tmp/add_tmp.dat " + "/tmp/" + m_filename+".dat"],shell=True)
  else:
    call(["mv "+ "/tmp/" + t_filename+".analyzed.root" + " " + "/tmp/" + m_filename+".analyzed.root"],shell=True)
    call(["mv "+ "/tmp/" + t_filename+".raw.root" + " " + "/tmp/" + m_filename+".raw.root"],shell=True)
    call(["mv "+ "/tmp/" + t_filename+".dat" + " " + "/tmp/" + m_filename+".dat"],shell=True)

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
  for dirname, dirnames, filenames in os.walk('/tmp/'):
    for name in filenames:
        if "chunk_0.dat" in name:
          fname_base = name[:-4]
          print "Base name found: %s" % (fname_base)
  run = Run.objects.order_by('-id')[0]
  fname_base = run.Name
  print fname_base
  while True:
    fname = "/tmp/"+fname_base+"_chunk_"+str(chunk)+".dat"
    print fname
    time.sleep(3)
    file_exist = os.path.isfile(fname) 
    if file_exist:
      process_chunk(fname_base, chunk)
      chunk +=1

