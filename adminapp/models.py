from django.db import models
from django.contrib.auth.models import User
from hospital.models import Hospital
from doctor.models import Doctor
from userapp.models import UserRegistration
from django.db.models.signals import post_save
from django.dispatch import receiver

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=50, default='General Admin')
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class AdminActivity(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.admin.username} - {self.action}"
    
    class Meta:
        verbose_name_plural = "Admin Activities"

class AdminDashboardStats(models.Model):
    total_hospitals = models.IntegerField(default=0)
    total_doctors = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    total_appointments = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Admin Dashboard Statistics"

class AdminNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('user_registration', 'User Registration'),
        ('doctor_registration', 'Doctor Registration'),
        ('hospital_registration', 'Hospital Registration'),
        ('system_alert', 'System Alert'),
        ('new_appointment', 'New Appointment'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    related_user = models.ForeignKey(UserRegistration, on_delete=models.SET_NULL, null=True, blank=True)
    related_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    related_hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Admin Notifications"
    
    def __str__(self):
        return f"{self.notification_type} - {self.title}"

# Signal to create AdminProfile when a new admin user is created
@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        AdminProfile.objects.create(user=instance)

# Signal to save AdminProfile when admin user is updated
@receiver(post_save, sender=User)
def save_admin_profile(sender, instance, **kwargs):
    if instance.is_staff:
        AdminProfile.objects.get_or_create(user=instance)