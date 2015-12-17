from django.db import models

# Create your models here.

class GEB(models.Model):
  Type = models.CharField(max_length=30)
  ChamberID = models.CharField(max_length=30)

  def __unicode__(self):
    return self.Type # or better id?

class AMC(models.Model):
  BoardID = models.CharField(max_length=30)
  Type = models.CharField(max_length=30)
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
