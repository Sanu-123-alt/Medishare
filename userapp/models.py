from django.db import models
from django.contrib.auth.models import User
from doctor.models import *
from doctor.models import Doctor, Hospital
# Create your models here.

from django.db import models
from django.utils import timezone

class UserRegistration(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    fullname = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    security_key = models.CharField(max_length=8)
    profile_image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    
    # Add these fields if they don't exist
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return self.fullname

    class Meta:
        db_table = 'user_registration'
    
class MedicalRecord(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)   # linked to your custom user
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='medical_records/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
from doctor.models import AppointmentSlot

class Appointment(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    slot = models.ForeignKey(AppointmentSlot, on_delete=models.CASCADE, null=True, blank=True)  # new field
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=(('booked', 'Booked'), ('cancelled', 'Cancelled')), 
        default='booked'
    )

    def __str__(self):
        return f"{self.user.username} - {self.doctor.name} on {self.date}"

class Notification(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(
        max_length=20,
        choices=[
            ('appointment', 'Appointment'),
            ('record', 'Medical Record'),
            ('system', 'System'),
            ('reminder', 'Reminder'),
        ],
        default='system',
    )

    # ✅ Add optional references to doctor/hospital who accessed
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


# In userapp/models.py - Update your Review model
class Review(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True, blank=True)
    
    # Add guest name field for non-registered users
    guest_name = models.CharField(max_length=100, null=True, blank=True)
    
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(doctor__isnull=False, hospital__isnull=True) |
                    models.Q(doctor__isnull=True, hospital__isnull=False)
                ),
                name='review_doctor_or_hospital'
            )
        ]
    
    def get_reviewer_name(self):
        """Return the actual reviewer's name"""
        if self.user:
            return self.user.fullname  # Use the registered user's full name
        return self.guest_name or "Anonymous"  # Use guest name or fallback
    
    def __str__(self):
        reviewed = self.doctor.name if self.doctor else self.hospital.name
        return f"{self.get_reviewer_name()}'s review for {reviewed}"

class Feedback(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('hospital', 'Hospital'),
    ]
    
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)  # Optional: for admin moderation

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"
    
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

# Emergency Contact Model (add to models.py)
class EmergencyContact(models.Model):
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    is_primary = models.BooleanField(default=False)

class EmergencyMedicalInfo(models.Model):
    user = models.OneToOneField(UserRegistration, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=5, choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ])
    allergies = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    emergency_instructions = models.TextField(blank=True)
    organ_donor = models.BooleanField(default=False)

from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string

class OTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.email} - {self.otp_code}"
    
    def is_expired(self):
        expiry_time = self.created_at + timedelta(minutes=10)  # 10 minutes expiry
        return timezone.now() > expiry_time
    
    def increment_attempts(self):
        self.attempts += 1
        self.save()
    
    def is_max_attempts_reached(self):
        return self.attempts >= 3
    
    @classmethod
    def generate_otp(cls, email):
        # Delete any existing OTPs for this email
        cls.objects.filter(email=email).delete()
        
        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Create new OTP
        otp = cls.objects.create(
            email=email,
            otp_code=otp_code
        )
        return otp_code

class EmergencyAccessCode(models.Model):
    user = models.OneToOneField(UserRegistration, on_delete=models.CASCADE)
    access_code = models.CharField(max_length=8, unique=True)  # Shorter, memorable code
    qr_code = models.CharField(max_length=64, unique=True)    # Longer, more secure code for QR
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_accessed = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        return timezone.now() <= self.expires_at

    def update_access(self):
        self.last_accessed = timezone.now()
        self.save()

    @classmethod
    def generate_codes(cls, user):
        # Generate a short, memorable access code (like AB123XY)
        def generate_access_code():
            letters = ''.join(random.choices(string.ascii_uppercase, k=4))
            numbers = ''.join(random.choices(string.digits, k=3))
            code = f"{letters[:2]}{numbers}{letters[2:]}"
            return code

        # Generate a longer QR code
        def generate_qr_code():
            return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

        # Keep generating until we get unique codes
        while True:
            access_code = generate_access_code()
            qr_code = generate_qr_code()
            if not cls.objects.filter(access_code=access_code).exists() and \
               not cls.objects.filter(qr_code=qr_code).exists():
                break

        # Set expiry to 1 year from now
        expires_at = timezone.now() + timedelta(days=365)
        
        # Create or update emergency codes
        emergency_code, created = cls.objects.update_or_create(
            user=user,
            defaults={
                'access_code': access_code,
                'qr_code': qr_code,
                'expires_at': expires_at
            }
        )
        return emergency_code

@login_required
@csrf_protect
def generate_qr_code_api(request):
    """Test response"""
    return JsonResponse({'message': 'Test response'})