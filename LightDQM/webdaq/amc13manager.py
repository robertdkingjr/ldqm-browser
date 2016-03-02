#!/bin/env python

import uhal
import amc13
import sys
import struct

class AMC13manager:
  def __init__(self):
    pass

  def connect(self,sn):
    self.connection = "connection"+str(sn)+".xml" # get connection file
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

  def configureTrigger(self, ena = True, mode = 2, burst = 1, rate = 10, rules = 0):
    self.localTrigger = ena
    self.device.configureLocalL1A(ena, mode, burst, rate, rules)

  def startDataTaking(self, ofile, nevents):
    if self.localTrigger:
      self.device.startContinuousL1A()
    #submit work loop here
    c = 1
    with open (ofile, "wb") as compdata:
      while True:
        nevt = self.device.read(self.device.Board.T1, 'STATUS.MONITOR_BUFFER.UNREAD_EVENTS')
        #print "Trying to read %s events" % nevt
        for i in range(nevt):
          pEvt = self.device.readEvent()
          for word in pEvt:
            #print hex(word)
            compdata.write(struct.pack('Q',word))
          c += 1
          if c > nevents:
            break
        if c > nevents:
          break
      if self.localTrigger:
        self.device.stopContinuousL1A()

  def stopDataTaking(self, ofile):
    if self.localTrigger:
      self.device.stopContinuousL1A()
    #submit work loop here
