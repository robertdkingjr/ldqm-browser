import os
from subprocess import call
import datetime
from datetime import datetime
from time import strptime
from ldqm_db.models import Run, AMC
#dirname=os.getcwd()
dirname="/data/bigdisk/GEM-Data-Taking/Testbeam2015"
command = "/home/mdalchen/private/gem-daq-code/gem-light-dqm/dqm-root/bin/linux/x86_64_slc6/rundqm "
#command = "echo "
idx = 1
#for filename in sorted(os.listdir(dirname)):
for filename in open("gtx0.log"):
  year=filename[-9:-5]
  print year
  month=str(strptime(filename[-25:-22],'%b').tm_mon)
  print month
  day=filename[-21:-19].replace('_','0')
  print day
  newrun = Run(Name=filename[:-9], 
               Type="testbeam", 
               Number=str(idx).zfill(6), 
               Date=datetime.strptime(day+month+year, "%d%m%Y").date(), 
               Period="2015T", 
               Station="H4",
               Status=True)
  newrun.save()
  newrun.amcs.add(AMC.objects.get(id=3))
  idx+=1

