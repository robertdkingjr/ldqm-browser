import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LightDQM.settings")
# import django
# django.setup()

# from django.conf import settings
# settings.configure()

import datetime
from time import sleep
from ldqm_db.models import *
# from gempython.utils.db.ldqm_db.amcmanager import *

# import gempython.utils.gemlogger as GEMLogger

# query_gemlogger = GEMLogger.getGEMLogger(__name__)
#query_gemlogger.setLevel(GEMLogger.DEBUG)

def configure_db(station="GEM904",setuptype="teststand",runperiod="2017T",shelf=3):
  #amc_list=[1,2,3,4,5,6,7,8,9,10,11,12]
  #geb_list=[[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],[0,1,2,3,4,5,6,7,8,9,10,11],]
  amc_list=[2]
  geb_list=[[0,],]

  zlist = zip(amc_list, geb_list)
  a_list = []
  for amcN, gtx_list in zlist:
    print "On AMC # %s on shelf %s \n" %(amcN, shelf)

    # m_AMCmanager = AMCmanager(shelf,connection_file)
    # m_AMCmanager = AMCmanager()
    g_list = []
    #try:
    #  m_AMCmanager.connect(int(amcN), int(shelf))
    #except ValueError as ve:
    #  msg = "AMC # %s is missing, advancing to the next one\n" %(amcN)
    #  query_gemlogger.info(msg)
    #  continue
    # retrieve VFAT slot numberd and ChipIDs from HW
    # m_AMCmanager.connect(int(amcN), int(shelf))
    # msg = "Connection to AMC # %s successful"%(amcN)
    # query_gemlogger.info(msg)

    for gtx in gtx_list:
      print "On gem.shelf%02d.amc%02d.optohybrid%02d" %(shelf,int(amcN),gtx)
      # query_gemlogger.info(msg)
      #try:
      #  manager = uhal.ConnectionManager( self.connection_file )
      #  ohdevice  = manager.getDevice( "gem.shelf%02d.amc%02d.optohybrid%02d"%(shelf,int(amcN),gtx) )
      #except:
      #  msg = 'OH %s is missing!' %(gtx)
      #  query_gemlogger.info(msg)
      #  continue
      # connection_file = "file://${GEM_ADDRESS_TABLE_PATH}/connections.xml"
      # manager = uhal.ConnectionManager( connection_file )
      # ohdevice  = manager.getDevice( "gem.shelf%02d.amc%02d.optohybrid%02d"%(shelf,int(amcN),gtx) )

      # if m_AMCmanager.checkGTX(ohdevice, gtx):
      if True:
        # chipids = m_AMCmanager.getVFATs(ohdevice,gtx)
        # retrieve VFAT slot numberd and ChipIDs from DB
        vfats = VFAT.objects.all()
        # Check if the VFATs are in DB, add if not
        v_list = []
        # msg = chipids
        # query_gemlogger.debug(msg)
        # msg = chipids.keys()
        # query_gemlogger.debug(msg)
        # for chip in chipids.keys():
        for chip in range(24):
            
          msg = chip
          print msg
          # query_gemlogger.debug(msg)
          t_chipid = "0x%04x"%(0xf000+chip)
          if t_chipid in vfats.filter(Slot=chip).values_list("ChipID", flat=True):
            pass # ends if t_chipid
          else:
            msg = "Adding VFAT(ChipID = %s, Slot = %d)"%(t_chipid,chip)
            print msg
            # query_gemlogger.info(msg)
            v = VFAT(ChipID = t_chipid, Slot = chip)
            v.save()
            pass # ends else (from if t_chipid)
          v_list.append(VFAT.objects.get(ChipID = t_chipid, Slot = chip))
          pass # ends for chip in chipids
        t_chamberID = 'GTX-'+str(gtx) # use gtx link number now, read from HW later when available
        msg = "t_chamberID = %s" %(t_chamberID)
        print msg
        # query_gemlogger.info(msg)
        gebs = GEB.objects.filter(ChamberID=t_chamberID)
        t_flag = False
        for geb in gebs:
          if v_list == list(geb.vfats.all()):
            t_flag = True
            g_list.append(geb)
            break
          pass # ends for geb in gebs
        if t_flag:
          pass # ends if t_flag
        else:
          msg = "Update DB"
          print msg
          # query_gemlogger.info(msg)
          g = GEB(Type="Long",ChamberID = t_chamberID)
          g.save()
          for v in v_list:
            g.vfats.add(v)
            pass # ends for v in v_list
          g_list.append(g)
          pass # ends else, from if t_flag
        pass # ends if m_AMCmanager
      pass # ends for gtx in gtx_list

    t_flag = False
    t_boardID = "AMC-"+str(amcN) # hard code now, read from HW later when available
    amcs = AMC.objects.filter(BoardID = t_boardID)
    for amc in amcs:
      if g_list == list(amc.gebs.all()):
        t_flag = True
        a_list.append(amc)
        msg = "Adding to a_list : %s" %(amc.BoardID)
        print msg
        # query_gemlogger.info(msg)
        pass # ends if g_list
      pass # ends for amc in amcs
    if t_flag:
      pass # ends if t_flag
    else:
      msg = "Update DB"
      print msg
      # query_gemlogger.info(msg)
      a = AMC(Type="GLIB",BoardID = t_boardID)
      a.save()
      for g in g_list:
        a.gebs.add(g)
        pass # ends for g in g_list
      a_list.append(a)
      msg = "Adding to a_list : %s" %(a.BoardID)
      print msg
      # query_gemlogger.info(msg)
      pass # ends else (if t_flag)
    pass # ends for amcs in amcs

  newcrateid = "shelf%.02d"%(shelf)
  newcrate = Crate(CrateID=newcrateid)
  newcrate.save()
  for a in a_list:
    msg = "Adding AMC: %s" %(a.BoardID)
    print msg
    # query_gemlogger.info(msg)
    newcrate.amcs.add(a)
    # newrun.amcs.add(a)
    for g in a.gebs.all():
      msg = "Adding GEB: %s" %(g.ChamberID)
      print msg
      # query_gemlogger.info(msg)
      pass # ends for g in a.gebs.all
    pass # ends for a in a_list
  sleep(0.1) # what is this for?

  newconfig = Config(Tag="dummyConfigTag")
  newconfig.save()
  newconfig.crates.add(newcrate)



  # create a new run. Some values are hard-coded for now
  runs = Run.objects.filter(Period = runperiod, Station = station)
  rns = list(int(x) for x in list(runs.values_list("Number", flat=True)))
  try:
    nrs = u'%s'%(max(rns)+1)
  except ValueError as ve:
    nrs = u'%s'%(1)
    pass # ends try/except
  nrs = nrs.zfill(6)
  t_date = str(datetime.datetime.utcnow()).split(' ')[0]
  m_filename = "run"+str(nrs)+""+"_"+setuptype+"_"+station+"_"+t_date
  print "New run filename:",m_filename
  newrun = Run(Name=m_filename, Type = setuptype, Number = str(nrs), Date = t_date, Period = runperiod, Station = station, ConfigTag = newconfig)
  newrun.save()




if __name__ == "__main__":
    configure_db()
