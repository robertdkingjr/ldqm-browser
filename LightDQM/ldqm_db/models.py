from django.db import models

# Create your models here.
class VFAT(models.Model):
  ChipID = models.CharField(max_length=6, default='0xdead')
  Status = models.CharField(max_length=1, default='0')

class GEB(models.Model):
  Type = models.CharField(max_length=30)
  ChamberID = models.CharField(max_length=30)
  Status = models.CharField(max_length=1, default='0')
  vfats = models.ManyToManyField(VFAT)

  def __unicode__(self):
    return self.Type # or better id?

class AMC(models.Model):
  BoardID = models.CharField(max_length=30)
  Type = models.CharField(max_length=30)
  Status = models.CharField(max_length=1, default='0')
  gebs = models.ManyToManyField(GEB)
  def __unicode__(self):
    return self.Type # or better id?

class Run(models.Model):
  Name = models.CharField(max_length=50)
  Type = models.CharField(max_length=10)
  Number = models.CharField(max_length=10)
  Date = models.DateField()
  Period = models.CharField(max_length=10)
  Station = models.CharField(max_length=10)
  amcs = models.ManyToManyField(AMC)
  Status = models.BooleanField(default=False) #indicates if the dqm had processed the run

  def __unicode__(self):
    return self.Name
  
  class Meta:
    ordering = ['Date']
