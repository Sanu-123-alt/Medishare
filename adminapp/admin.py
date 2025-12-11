from django.contrib import admin
from hospital . models import*
from doctor.models import*
from userapp.models import*
# Register your models here.
admin.site.register(Hospital)
admin.site.register(Doctor)
admin.site.register(Feedback)