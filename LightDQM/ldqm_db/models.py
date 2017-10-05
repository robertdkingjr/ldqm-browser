from django.db import models

# Create your models here.
class HWstate(models.Model):
  HWID = models.CharField(max_length=30)
  State = models.CharField(max_length=1, default='0')
  def __unicode__(self):
    return self.HWID 

class SystemState(models.Model):
  amcStates = models.ManyToManyField(HWstate, related_name='amc_states')
  gebStates = models.ManyToManyField(HWstate, related_name='geb_states')
  vfatStates = models.ManyToManyField(HWstate, related_name='vfat_states')
  def __unicode__(self):
    return str(self.id)

class VFAT(models.Model):
  ChipID = models.CharField(max_length=6, default='0xdead')
  Slot = models.PositiveSmallIntegerField(default=255)
  def __unicode__(self):
    return self.ChipID

class GEB(models.Model):
  Type = models.CharField(max_length=30)
  ChamberID = models.CharField(max_length=30)
  Link = models.PositiveSmallIntegerField(default=255)
  vfats = models.ManyToManyField(VFAT)
  def __unicode__(self):
    return self.ChamberID

class AMC(models.Model):
  BoardID = models.CharField(max_length=30)
  Type = models.CharField(max_length=30)
  Slot = models.PositiveSmallIntegerField(default=255)
  gebs = models.ManyToManyField(GEB)
  def __unicode__(self):
    return self.Type # or better id?

class Crate(models.Model):
  CrateID = models.CharField(max_length=30)
  amcs = models.ManyToManyField(AMC)

class Config(models.Model):
  Tag = models.CharField(max_length=50)
  crates = models.ManyToManyField(Crate)

class Run(models.Model):
  Name = models.CharField(max_length=50)
  Type = models.CharField(max_length=10)
  Number = models.CharField(max_length=10)
  Date = models.DateField()
  Period = models.CharField(max_length=10)
  Station = models.CharField(max_length=10)
  ConfigTag = models.ForeignKey(Config, null=True, blank=True, default=None)
  Status = models.BooleanField(default=False) #indicates if the dqm had processed the run
  State = models.ForeignKey(SystemState, null=True, blank=True, default=None)
  def __unicode__(self):
    return self.Name
  
  class Meta:
    ordering = ['Date']
