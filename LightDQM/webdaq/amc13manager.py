#!/bin/env python

import uhal
import amc13
import sys
import struct
from helper import OutputGrabber
import time

class AMC13manager:
  def __init__(self):
    pass

  def connect(self,sn,verbosity):
    self.connection = "connection"+str(sn)+".xml" # get connection file
    self.verbosity = verbosity
    self.device = amc13.AMC13(self.connection) # connect to amc13
    #reset amc13
    self.device.AMCInputEnable(0x0)
    self.reset()

  def reset(self):
    self.device.reset(self.device.Board.T1)
    self.device.reset(self.device.Board.T2)
    self.device.resetCounters()
    self.device.resetDAQ()

  def configureInputs(self, inlist):
    mask = self.device.parseInputEnableList(inlist, True)
    self.device.AMCInputEnable(mask)

  def configureTrigger(self, ena, mode = 2, burst = 1, rate = 10, rules = 0):
    self.localTrigger = ena
    if self.localTrigger:
      self.device.configureLocalL1A(ena, mode, burst, rate, rules)

  #def startDataTaking(self, ofile, nevents):
  def startDataTaking(self, ofile):
    if self.localTrigger:
      self.device.startContinuousL1A()
    #submit work loop here
    self.isRunning = True
    c = 1
    #with open (ofile, "wb") as compdata:
    datastring = ''
    packer = struct.Struct('Q')
    pEvt = []
    read_event = self.device.readEvent
    cnt = 0
    while self.isRunning:
      nevt = self.device.read(self.device.Board.T1, 'STATUS.MONITOR_BUFFER.UNREAD_BLOCKS')
      #nevt = self.device.read(self.device.Board.T1, 'STATUS.MONITOR_BUFFER.UNREAD_EVENTS')
      print "Trying to read %s events" % nevt
      for i in range(nevt):
        pEvt += read_event()
      for word in pEvt:
        datastring += packer.pack(word)
      #if nevt > 0:
      with open (ofile+"_chunk_"+str(cnt)+".dat", "wb") as compdata:
        compdata.write(datastring)
      cnt += 1;
      time.sleep(5)


  def stopDataTaking(self):
    if self.localTrigger:
      self.device.stopContinuousL1A()
    #submit work loop here
    self.isRunning = False
