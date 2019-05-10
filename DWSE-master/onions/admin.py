from django.contrib import admin
from .models import OnionSites
# Register your models here.

admin.site.register(OnionSites)
def __str__(self):
	return self.name	