from django.db import models
from hospital.models import Hospital



class Doctor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=50)
    specialization = models.CharField(max_length=100)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="doctor_images/", blank=True, null=True)  # profile photo
    qualifications = models.CharField(max_length=255, blank=True, null=True)   # e.g. MBBS, MD
    experience = models.CharField(max_length=255, blank=True, null=True)  # e.g. "10 years in Cardiology"
    twitter = models.URLField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)     # LinkedIn profile link
    portfolio = models.URLField(max_length=255, blank=True, null=True)    # Personal website/portfolio
    bio = models.TextField(blank=True, null=True)                         # About the doctor

    def __str__(self):
        return self.name

class AppointmentSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True)  # allow null for now
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField()
    status = models.CharField(max_length=20, choices=[('available', 'Available'), ('booked', 'Booked')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doctor.name if self.doctor else 'No Doctor'} - {self.date} {self.time} ({self.status})"
