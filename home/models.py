from django.db import models

# Create your models here.

class Customer(models.Model):
    username = models.CharField(max_length=255, null=False)
    email = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.username + ", " + self.email


class Info(models.Model):
#    file = models.FileField(upload_to='documents/', None=True)
    image = models.ImageField(upload_to='images/') #, None=True
    scaleAmount = models.IntegerField()
    model = models.CharField(max_length=255, null=False)
    qualityMeasure = models.IntegerField()

    def __str__(self):
        return self.scaleAmount + ", " + self.model + ", " + self.qualityMeasure

class ModelInfo(models.Model):
    # model = models.FileField()
    modelDesc = models.CharField(max_length=20, null=False)
    modelfilename = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.modelDesc + ", " + self.modelfilename