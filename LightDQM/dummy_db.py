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

def configure_db(station="GEM904",setuptype="teststand",runperiod="2017T",shelf=4):


    vfats = VFAT.objects.all()
    # Check if the VFATs are in DB, add if not
    v_list = []
    
    # Make 24 dummy VFATs
    for chip in range(24):
        
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



        # query_gemlogger.info(msg)

    
    # Make 12 dummy GEBs (chambers)
    g_list = []
    for i in range(12):
        t_chamberID = 'GTX-'+str(i) # use gtx link number now, read from HW later when available
        geb = GEB.objects.filter(ChamberID=t_chamberID)
        if geb and v_list == list(geb[0].vfats.all()):
            g_list.append(geb[0])
        else:
            g = GEB(Type="Long",ChamberID = t_chamberID)
            g.save()
            for v in v_list:
                g.vfats.add(v)

                g_list.append(g)


                
    # Make 12 dummy AMCs
    a_list = []
    for i in range(12):
        new_boardID = "AMC-"+str(i) 
        a = AMC(Type="CTP7",BoardID = new_boardID)
        a.save()
        for g in g_list:
            a.gebs.add(g)
            pass # ends for g in g_list
        a_list.append(a)
        msg = "Adding to a_list : %s" %(a.BoardID)
        print msg
      # query_gemlogger.info(msg)


        

# Make single crate to hold 12 AMC x 12 Chambers
    newcrateid = "shelf%.02d"%(shelf)
    newcrate = Crate(CrateID=newcrateid)
    newcrate.save()
    for a in a_list:
        msg = "Adding AMC (%s) to shelf" %(a.BoardID)
        print msg

        newcrate.amcs.add(a)

        for g in a.gebs.all():
            msg = "--GEB (%s) in AMC" %(g.ChamberID)
            print msg

            for v in g.vfats.all():
                msg = "----VFAT (%s) in GEB"%(v.ChipID)
                print msg

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
        
