from .models import Notification
from doctor.models import Doctor, Hospital

def create_data_access_notification(user, accessor_type, accessor, record_type="medical record"):
    """
    Create a notification when someone accesses user data
    
    Args:
        user: UserRegistration instance of the user whose data was accessed
        accessor_type: string 'doctor' or 'hospital'
        accessor: Doctor or Hospital instance who accessed the data
        record_type: string describing what type of data was accessed
    """
    title = f"Your {record_type} was accessed"
    
    if accessor_type.lower() == 'doctor':
        message = f"Dr. {accessor.name} accessed your {record_type} on {accessor.hospital.name if accessor.hospital else 'Independent Practice'}"
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type='record',
            doctor=accessor
        )
    elif accessor_type.lower() == 'hospital':
        message = f"{accessor.name} accessed your {record_type}"
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type='record',
            hospital=accessor
        )


from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
import random
from userapp.models import OTP

def generate_otp():
    """Generate a 6-digit random OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp_code, user_type='user'):
    """Send OTP email (implement your email logic here, e.g., using Django's send_mail)"""
    from django.core.mail import send_mail
    subject = f'Your {user_type.title()} Verification Code - MediShare'
    message = f'Your verification code is: {otp_code}\n\nThis code expires in 10 minutes.\n\nIf you did not request this, please ignore this email.'
    from_email = 'noreply@medishare.com'
    
    try:
        send_mail(subject, message, from_email, [email])
        return True
    except Exception:
        return False

def verify_otp(email, otp_code, delete_after_use=False):
    """Verify OTP for the given email. OTP expires 10 minutes after creation."""
    try:
        # Query OTP created within the last 10 minutes
        otp = OTP.objects.filter(
            email=email,
            otp_code=otp_code,
            created_at__gte=timezone.now() - timedelta(minutes=10)
        ).first()
        
        if otp:
            if otp.is_verified:
                return False, "OTP already used. Please request a new one."
            
            # Mark as verified (no delete, to allow session-based re-verification if needed)
            otp.is_verified = True
            otp.save()
            
            if delete_after_use:
                otp.delete()
            
            return True, "OTP verified successfully."
        else:
            return False, "OTP not found or expired. Please request a new one."
            
    except OTP.DoesNotExist:
        return False, "OTP not found. Please request a new one."
    except Exception as e:
        return False, f"Verification error: {str(e)}"

def cleanup_expired_otps():
    """Clean up OTPs older than 10 minutes"""
    cutoff = timezone.now() - timedelta(minutes=10)
    OTP.objects.filter(created_at__lt=cutoff).delete()