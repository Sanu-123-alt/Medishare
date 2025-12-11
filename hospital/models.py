from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=255) 
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='hospital_images/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    google_maps_link = models.URLField(max_length=500, blank=True, null=True)
    established_year = models.PositiveIntegerField(null=True, blank=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    ambulance_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class (e.g., fa-heart)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hospital.name} - {self.name}"

class HospitalService(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hospital.name} - {self.name}"

class HospitalAchievement(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255)
    description = models.TextField()
    year = models.PositiveIntegerField()
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hospital.name} - {self.title} ({self.year})"
