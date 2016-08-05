import os
from subprocess import call
from webdaq.state_helper import updateStates
from ldqm_db.models import Run
import time
import glob

def show_time(tbef):
  print
  print 'Now:',time.time()
  print 'Dif:',time.time()-tbef
  print
  return time.time()

def process_chunk(m_filename, chunk, offline_dqm = False):
  global is_first
  tbef = time.time()
  print 'BEGIN'
  tbef = show_time(tbef)
  print "Process chunk with base filename %s\n" %(m_filename)
  t_filename = m_filename+"_chunk_"+str(chunk)
#call root converter
  call_command =  os.getenv('BUILD_HOME')+'/gem-light-dqm/gemtreewriter/bin/'+os.getenv('XDAQ_OS')+'/'+os.getenv('XDAQ_PLATFORM')+'/unpacker'
  command_args = "/tmp/"+t_filename+".dat sdram"
  call([call_command+' '+command_args],shell=True)
  print 'Unpacker'
  tbef = show_time(tbef)
  print 'DQM'
#call dqm
  call_command =  os.getenv('BUILD_HOME')+'/gem-light-dqm/dqm-root/bin/'+os.getenv('XDAQ_OS')+'/'+os.getenv('XDAQ_PLATFORM')+'/dqm'
  command_args = "/tmp/"+t_filename+".raw.root"
  os.system(call_command+' '+command_args)
  print 'DQM'
  tbef = show_time(tbef)
  print 'hadd'
#call hadd if not the first chunk, otherwise rename
  if (os.path.isfile("/tmp/"+m_filename+".analyzed.root")):
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
  print 'hadd'
  tbef = show_time(tbef)
#call dqm printer
  if offline_dqm:
    print 'offline printer'
    call_command = os.getenv('BUILD_HOME')+'/gem-light-dqm/dqm-root/bin/'+os.getenv('XDAQ_OS')+'/'+os.getenv('XDAQ_PLATFORM')+'/gtprinter'
    command_args = "/tmp/"+m_filename+".analyzed.root"
    os.system(call_command+' '+command_args)
    #copy results to DQM display form
    call_command = os.getenv('LDQM_STATIC')+'/'
    call(["mkdir -p "+call_command],shell=True)
    call(["cp -r /tmp/"+m_filename+" "+call_command],shell=True)

  else:
    print 'online printer'
    call_command =  os.getenv('BUILD_HOME')+'/gem-light-dqm/dqm-root/bin/'+os.getenv('XDAQ_OS')+'/'+os.getenv('XDAQ_PLATFORM')+'/onlineprinter'
    command_args = "/tmp/"+m_filename+".analyzed.root"
    os.system(call_command+' '+command_args)
  print 'printer'
  tbef = show_time(tbef)
  print 'updateState'
#update AMC/GEB/VFAT states
  command_args = "/tmp/"+m_filename+".analyzed.root"
  updateStates(command_args)
  print 'updateState'
  tbef = show_time(tbef)
  print 'END'
  return

def run_dqm():
  chunk = 0
  time.sleep(5)  
  while True:
    try:
      run = Run.objects.order_by('-id')[0]
    except IndexError as ie:
      print "Index Error"
      continue
    fname_base = run.Name
    globname = glob.glob('/tmp/'+fname_base+'_chunk_*.dat')
    print len(globname), 'chunks remaining to process for',run.Name
    if len(globname)==0:
      if os.path.isfile('/tmp/'+fname_base+'.analyzed.root'):
        call_command = os.getenv('BUILD_HOME')+'/gem-light-dqm/dqm-root/bin/'+os.getenv('XDAQ_OS')+'/'+os.getenv('XDAQ_PLATFORM')+'/gtprinter'
        command_args = "/tmp/"+fname_base+".analyzed.root"
        os.system(call_command+' '+command_args)
        call_command = os.getenv('LDQM_STATIC')+'/'
        call(["mkdir -p "+call_command],shell=True)
        call(["cp -r /tmp/"+fname_base+" "+call_command],shell=True)
      else:
        time.sleep(5)

    glob_count=0
    for fname in globname:
      glob_count+=1
      # print fname
      chunk = int(fname[fname.find('chunk')+6:fname.find('.dat')])
      # print 'Chunk:',chunk
      file_exist = os.path.isfile(fname) 
      if file_exist:
        if glob_count==len(globname):
          process_chunk(fname_base, chunk, True) #do full print on last glob
        else:
          process_chunk(fname_base, chunk, False)



