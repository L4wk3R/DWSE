from django.db import models

# Create your models here.
class OnionSites(models.Model):
    name = models.CharField(max_length=50)
    body = models.TextField()
    onionscanfile = models.CharField(max_length=50)
    bodyscanned = models.IntegerField(default=0)
    onionscanned = models.IntegerField(default=0)
    
    def __str__(self):
    	return self.name