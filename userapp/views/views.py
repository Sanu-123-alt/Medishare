# Import and adjust import paths
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django import forms
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from userapp.models import UserRegistration, MedicalRecord, Notification, Feedback, Appointment
from doctor.models import Doctor, Hospital, AppointmentSlot
from datetime import date, timedelta
from django.db.models import Q
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from userapp.models import*
import qrcode
import io
import base64
from django.http import HttpResponse
# -------------------------
# Home
# -------------------------
def user_home(request):
    # Get featured doctors and hospitals
    featured_doctors = Doctor.objects.all()[:6]
    featured_hospitals = Hospital.objects.all()[:3]
    
    # Get approved feedbacks for display
    feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')[:6]

    # Handle feedback submission
    if request.method == 'POST':
        name = request.POST.get('name')
        role = request.POST.get('role')
        message = request.POST.get('message')
        
        if name and role and message:
            Feedback.objects.create(name=name, role=role, message=message)
            messages.success(request, "Thank you for your feedback!")
            return redirect('user_home')  # Stay on same page
        else:
            messages.error(request, "All fields are required.")

    return render(request, "home.html", {
        "featured_doctors": featured_doctors,
        "featured_hospitals": featured_hospitals,
        "feedbacks": feedbacks,  # Pass feedback to template
    })

# -------------------------
# Choice Login Page
# -------------------------
def choice_login(request):
    return render(request, "choice_base.html")


# -------------------------
# Registration
# -------------------------
def user_reg(request):
    return render(request, "user_reg.html")


from userapp.utils import verify_otp

from userapp.utils import verify_otp

def user_register(request):
    if request.method == "POST":
        # Get form data
        fullname = request.POST.get("fullname")
        phone = request.POST.get("phone")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")
        security_key = request.POST.get("securityKey")
        otp_code = request.POST.get("otp_code")  # Still received, but not used for re-verification

        # Basic validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("user_reg")

        if not (security_key.isdigit() and 6 <= len(security_key) <= 8):
            messages.error(request, "Security key must be 6-8 digits!")
            return redirect("user_reg")

        if UserRegistration.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("user_reg")

        if UserRegistration.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect("user_reg")

        # Check email verification flag from session (set after frontend OTP success)
        if not request.session.get('email_verified', {}).get('verified') or request.session.get('email_verified', {}).get('email') != email:
            messages.error(request, "Email verification required! Please verify OTP first.")
            return redirect("user_reg")

        # Clear the session flag after successful registration (one-time use)
        del request.session['email_verified']

        # Save user
        user = UserRegistration(
            fullname=fullname,
            phone=phone,
            username=username,
            email=email,
            password=make_password(password),
            security_key=security_key,
        )
        user.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect("choice_login")

    return render(request, "user_reg.html")


# -------------------------
# Login
# -------------------------
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next") or request.GET.get("next")

        try:
            user = UserRegistration.objects.get(username=username)
        except UserRegistration.DoesNotExist:
            messages.error(request, "Invalid username or password!")
            return redirect("user_login")

        # check password
        if check_password(password, user.password):
            # Store session values
            request.session["user_id"] = user.id
            request.session["user_name"] = user.fullname
            request.session["user_username"] = user.username
            request.session["is_authenticated"] = True  # Add this line
            request.session.set_expiry(86400)  # Set session to expire in 24 hours
            request.session.modified = True  # Force the session to be saved

            messages.success(request, f"Welcome {user.fullname}!")

            # redirect back if "next" was provided
            if next_url:
                return redirect(next_url)

            return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid username or password!")
            return redirect("user_login")

    # if GET request
    next_url = request.GET.get("next", "")
    return render(request, "user_login.html", {"next": next_url})


def user_logout(request):
    request.session.flush()  # Clear all session data
    messages.success(request, "You have been logged out successfully.")
    return redirect("choice_login")


# -------------------------
# Dashboard
# -------------------------
def user_dashboard(request):
    if "user_id" not in request.session:
        return redirect("user_login")

    user = UserRegistration.objects.get(id=request.session["user_id"])
    
    # Get dynamic data
    total_appointments = Appointment.objects.filter(user=user).count()
    total_records = MedicalRecord.objects.filter(user=user).count()
    doctors_consulted = Appointment.objects.filter(user=user).values('doctor').distinct().count()
    
    # Get recent appointments
    recent_appointments = Appointment.objects.filter(user=user).order_by('-date')[:5]
    
    # Get next appointment
    next_appointment = Appointment.objects.filter(
        user=user, 
        status='booked',
        date__gte=timezone.now().date()
    ).order_by('date', 'time').first()
    
    # Get recent notifications
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
    unread_notifications = Notification.objects.filter(user=user, is_read=False).count()

    return render(request, "user_dashboard.html", {
        "name": request.session.get("user_name"),
        "total_appointments": total_appointments,
        "total_records": total_records,
        "doctors_consulted": doctors_consulted,
        "recent_appointments": recent_appointments,
        "next_appointment": next_appointment,
        "notifications": notifications,
        "unread_notifications": unread_notifications,
    })


# -------------------------
# Medical Record Upload
# -------------------------
class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Chest X-ray - Jan 2025"
            }),
            "file": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
        }


def check_upload_access(request):
    if request.session.get("user_id"):  # user logged in
        return redirect("upload_record")
    else:
        login_url = f"{reverse('user_login')}?next=/upload_record/"
        return redirect(login_url)


def upload_record(request):
    if "user_id" not in request.session:
        return redirect(f"{reverse('user_login')}?next=/upload_record/")

    user = UserRegistration.objects.get(id=request.session["user_id"])

    if request.method == "POST":
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = user
            record.save()
            messages.success(request, "Medical record uploaded successfully!")
            return redirect("view_records")
    else:
        form = MedicalRecordForm()

    return render(request, "upload_record.html", {"form": form})


# -------------------------
# View Records
# -------------------------
def view_records(request):
    # Check if user is logged in OR has temporary security key access
    user_id = request.session.get("user_id") or request.session.get("temp_user_id")
    
    if not user_id:
        messages.error(request, "Please log in or use security key access to view records.")
        return redirect("security_key_access")
    
    try:
        # Get user based on which session ID is available
        if request.session.get("user_id"):
            user = UserRegistration.objects.get(id=request.session["user_id"])
        else:
            user = UserRegistration.objects.get(id=request.session["temp_user_id"])
        
        records = MedicalRecord.objects.filter(user=user).order_by("-uploaded_at")
        
        # If this is security key access, show a warning message
        if request.session.get("security_key_access"):
            messages.warning(request, "You are accessing records via security key. This session will have limited time access.")
        
        return render(request, "view_records.html", {
            "records": records,
            "is_security_key_access": request.session.get("security_key_access", False)
        })
        
    except UserRegistration.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("security_key_access")


# -------------------------
# Delete Record
# -------------------------
def delete_record(request, record_id):
    if "user_id" not in request.session:
        return redirect("user_login")

    user = UserRegistration.objects.get(id=request.session["user_id"])
    record = get_object_or_404(MedicalRecord, id=record_id, user=user)
    record.delete()
    messages.success(request, "Medical record deleted successfully!")
    return redirect("view_records")


def user_appoinment(request):
    # Start with all doctors
    doctor_queryset = Doctor.objects.all()
    hospital_queryset = Hospital.objects.all()

    # Apply filters from GET parameters
    location = request.GET.get('location')
    specialty = request.GET.get('specialty')
    availability = request.GET.get('availability', '')

    if location:
        doctor_queryset = doctor_queryset.filter(
            Q(hospital__location__icontains=location) |
            Q(hospital__name__icontains=location)
        )
        hospital_queryset = hospital_queryset.filter(
            Q(location__icontains=location) | Q(name__icontains=location)
        )

    if specialty:
        doctor_queryset = doctor_queryset.filter(specialization__iexact=specialty)

    # Filter slots based on availability
    doctors = doctor_queryset
    doctor_slots = {}
    for doc in doctors:
        slot_filter = Q(status='available')
        if availability == 'today':
            slot_filter &= Q(date=date.today())
        elif availability == 'this-week':
            end_week = date.today() + timedelta(days=7)
            slot_filter &= Q(date__range=[date.today(), end_week])

        slots = doc.appointmentslot_set.filter(slot_filter).order_by('date', 'time')
        if slots.exists():
            doctor_slots[doc.id] = slots

    # Filter hospitals (simple for now)
    hospitals = hospital_queryset

    return render(request, 'user_appoinment.html', {
        'doctors': doctors,
        'hospitals': hospitals,
        'doctor_slots': doctor_slots,
    })


def book_appointment(request):
    if "user_id" not in request.session:
        return redirect("user_login")

    user = UserRegistration.objects.get(id=request.session["user_id"])
    doctors = Doctor.objects.all()

    if request.method == "POST":
        doctor_id = request.POST.get("doctor")
        slot_id = request.POST.get("slot")
        reason = request.POST.get("reason")

        try:
            doctor = get_object_or_404(Doctor, id=doctor_id)
            slot = get_object_or_404(AppointmentSlot, id=slot_id, doctor=doctor, status="available")

            appointment = Appointment.objects.create(
                user=user,
                doctor=doctor,
                slot=slot,
                date=slot.date,
                time=slot.time,
                reason=reason,
                status="booked"
            )

            # Mark slot as booked
            slot.status = "booked"
            slot.save()

            messages.success(request, "Appointment booked successfully! ✅")
            return redirect("my_appointments")

        except Exception as e:
            messages.error(request, f"Failed to book appointment: {e}")
            return redirect("book_appointment")


def my_appointments(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("user_login")

    user = UserRegistration.objects.get(id=user_id)
    appointments = Appointment.objects.filter(user=user).order_by("-date")
    return render(request, "my_appointments.html", {"appointments": appointments})


def cancel_appointment(request, appointment_id):
    user = UserRegistration.objects.get(id=request.session["user_id"])
    appointment = get_object_or_404(Appointment, id=appointment_id, user=user)

    # Update the slot
    slot = AppointmentSlot.objects.filter(
        doctor=appointment.doctor,
        date=appointment.date,
        time=appointment.time
    ).first()
    if slot:
        slot.status = 'available'
        slot.save()

    appointment.status = 'cancelled'
    appointment.save()
    messages.success(request, "Appointment cancelled successfully.")
    return redirect('my_appointments')


# -------------------------
# Notifications
# -------------------------
def user_notifications(request):
    if "user_id" not in request.session:
        return redirect("user_login")

    user = UserRegistration.objects.get(id=request.session["user_id"])
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    
    return render(request, "notifications.html", {
        "notifications": notifications,
        "unread_count": notifications.filter(is_read=False).count()
    })


@require_POST
def mark_notification_read(request, notification_id):
    # authentication
    if "user_id" not in request.session:
        # if HTMX request return JSON error; otherwise redirect
        if request.headers.get("HX-Request"):
            return JsonResponse({"error": "unauthenticated"}, status=401)
        return redirect("user_login")

    user = get_object_or_404(UserRegistration, id=request.session["user_id"])
    notification = get_object_or_404(Notification, id=notification_id, user=user)

    if not notification.is_read:
        notification.is_read = True
        notification.save()

    unread_count = Notification.objects.filter(user=user, is_read=False).count()

    # If this is an HTMX request, return the updated partial AND set HX-Trigger header
    if request.headers.get("HX-Request"):
        resp = render(request, "notification_item.html", {"notification": notification})
        # HX-Trigger should be valid JSON string (client will JSON.parse it)
        resp["HX-Trigger"] = json.dumps({"unreadCount": unread_count})
        return resp

    # fallback for non-HTMX requests
    return redirect("user_notifications")


# -------------------------
# Security Key Access
# -------------------------
def security_key_access(request):
    """Allow access to medical data using username and security key, and notify patient."""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        security_key = request.POST.get("security_key", "").strip()
        
        if not username or not security_key:
            messages.error(request, "Username and security key are required.")
            return render(request, "security_key_access.html")
        
        try:
            user = UserRegistration.objects.get(username=username, security_key=security_key)

            # Store in session for temporary access - use consistent naming
            request.session["temp_user_id"] = user.id
            request.session["temp_user_name"] = user.fullname
            request.session["temp_user_username"] = user.username
            request.session["security_key_access"] = True  # Flag for temporary access
            request.session.modified = True

            # ✅ Identify who accessed (doctor or hospital)
            accessed_by = "Security Key Access"  # Default
            doctor = None
            hospital = None

            if "doctor_id" in request.session:  # doctor logged in
                try:
                    doctor = Doctor.objects.get(id=request.session["doctor_id"])
                    accessed_by = f"Dr. {doctor.name}"
                except Doctor.DoesNotExist:
                    pass
            elif "hospital_id" in request.session:  # hospital logged in
                try:
                    hospital = Hospital.objects.get(id=request.session["hospital_id"])
                    accessed_by = f"Hospital: {hospital.name}"
                except Hospital.DoesNotExist:
                    pass
            elif "user_id" in request.session:  # user accessing their own data
                accessed_by = "Self Access via Security Key"

            # ✅ Create Notification
            Notification.objects.create(
                user=user,
                title="Data Access Alert",
                message=f"Your medical records were accessed by {accessed_by} using your security key on {timezone.now().strftime('%Y-%m-%d %H:%M')}.",
                notification_type="security_access",
                doctor=doctor,
                hospital=hospital
            )

            messages.success(request, f"Access granted! Welcome {user.fullname}")
            return redirect("view_records")

        except UserRegistration.DoesNotExist:
            messages.error(request, "Invalid username or security key.")
            return render(request, "security_key_access.html")

    return render(request, "security_key_access.html")




def emergency_access(request, user_id):
    """Public emergency access endpoint"""
    try:
        user = UserRegistration.objects.get(id=user_id)
        emergency_info = EmergencyMedicalInfo.objects.filter(user=user).first()
        emergency_contacts = EmergencyContact.objects.filter(user=user, is_primary=True)
        medical_records = MedicalRecord.objects.filter(user=user).order_by('-uploaded_at')
        
        return render(request, "emergency_access_public.html", {
            "user": user,
            "emergency_info": emergency_info,
            "emergency_contacts": emergency_contacts,
            "medical_records": medical_records,
            "accessed_at": timezone.now()
        })
        
    except UserRegistration.DoesNotExist:
        return render(request, "emergency_access_public.html", {
            "error": "User not found or invalid QR code"
        })





def emergency_dashboard(request):
    if "user_id" not in request.session:
        return redirect("user_login")
    
    try:
        user = UserRegistration.objects.get(id=request.session["user_id"])
        emergency_info = EmergencyMedicalInfo.objects.filter(user=user).first()
        emergency_contacts = EmergencyContact.objects.filter(user=user)
        
        # Generate emergency access URL for JavaScript
        emergency_access_url = request.build_absolute_uri(f'/emergency/auth/{user.id}/')
        
        return render(request, "emergency_dashboard.html", {
            "user": user,
            "emergency_info": emergency_info,
            "emergency_contacts": emergency_contacts,
            "emergency_access_url": emergency_access_url
        })
        
    except UserRegistration.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("user_dashboard")

@csrf_exempt
def add_emergency_contact(request):
    """Add new emergency contact"""
    if "user_id" not in request.session:
        return JsonResponse({"success": False, "error": "Not logged in"})
    
    if request.method == "POST":
        try:
            user = UserRegistration.objects.get(id=request.session["user_id"])
            
            # If setting as primary, unset other primaries
            is_primary = request.POST.get("is_primary") == "on"
            if is_primary:
                EmergencyContact.objects.filter(user=user, is_primary=True).update(is_primary=False)
            
            contact = EmergencyContact(
                user=user,
                name=request.POST.get("name"),
                relationship=request.POST.get("relationship"),
                phone=request.POST.get("phone"),
                email=request.POST.get("email", ""),
                is_primary=is_primary
            )
            contact.save()
            
            messages.success(request, "Emergency contact added successfully!")
            return redirect("emergency_dashboard")
            
        except Exception as e:
            messages.error(request, f"Error adding contact: {str(e)}")
            return redirect("emergency_dashboard")
    
    return redirect("emergency_dashboard")

@csrf_exempt
def update_medical_info(request):
    """Update emergency medical information"""
    if "user_id" not in request.session:
        return JsonResponse({"success": False, "error": "Not logged in"})
    
    if request.method == "POST":
        try:
            user = UserRegistration.objects.get(id=request.session["user_id"])
            
            # Get or create emergency info
            emergency_info, created = EmergencyMedicalInfo.objects.get_or_create(
                user=user
            )
            
            # Update fields
            emergency_info.blood_type = request.POST.get("blood_type", "")
            emergency_info.allergies = request.POST.get("allergies", "")
            emergency_info.current_medications = request.POST.get("current_medications", "")
            emergency_info.chronic_conditions = request.POST.get("chronic_conditions", "")
            emergency_info.emergency_instructions = request.POST.get("emergency_instructions", "")
            emergency_info.organ_donor = request.POST.get("organ_donor") == "true"
            emergency_info.save()
            
            messages.success(request, "Medical information updated successfully!")
            return redirect("emergency_dashboard")
            
        except Exception as e:
            messages.error(request, f"Error updating medical information: {str(e)}")
            return redirect("emergency_dashboard")
    
    return redirect("emergency_dashboard")


# API endpoint for QR code generation
@csrf_exempt
def generate_qr_code_api(request):
    """API endpoint to generate QR code"""
    if "user_id" not in request.session:
        return JsonResponse({"success": False, "error": "Not logged in"})
    
    try:
        user = UserRegistration.objects.get(id=request.session["user_id"])
        # Get the host and build the full URL
        host = request.get_host()
        protocol = "https" if request.is_secure() else "http"
        qr_data = request.build_absolute_uri(f'/emergency/auth/{user.id}/')
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return JsonResponse({
            "success": True,
            "qr_code": f"data:image/png;base64,{img_str}",
            "qr_data": qr_data
        })
        
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
    


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from userapp.utils import send_otp_email, verify_otp, generate_otp, cleanup_expired_otps
from userapp.models import OTP

@csrf_exempt
def send_otp(request):
    """Send OTP to email for registration"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            user_type = data.get('user_type', 'user')  # user, doctor, hospital
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email is required.'
                })
            
            # Clean up expired OTPs first
            cleanup_expired_otps()
            
            # Generate OTP
            otp_code = generate_otp()
            
            # Save OTP to database
            OTP.objects.filter(email=email).delete()  # Remove existing OTPs
            otp = OTP.objects.create(
                email=email,
                otp_code=otp_code
            )
            
            # Send OTP email
            email_sent = send_otp_email(email, otp_code, user_type)
            
            if email_sent:
                return JsonResponse({
                    'success': True,
                    'message': 'OTP sent successfully to your email.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to send OTP. Please try again.'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })

@csrf_exempt
def verify_otp_view(request):
    """Verify OTP code"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp_code = data.get('otp_code')
            
            if not email or not otp_code:
                return JsonResponse({
                    'success': False,
                    'message': 'Email and OTP code are required.'
                })
            
            # Verify OTP
            is_valid, message = verify_otp(email, otp_code)
            
            if is_valid:
                # Set session flag for email verification (expires on registration)
                request.session['email_verified'] = {'verified': True, 'email': email}
                request.session.modified = True  # Ensure session saves
            
            return JsonResponse({
                'success': is_valid,
                'message': message
            })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    })

def update_profile(request):
    """Update user profile"""
    if "user_id" not in request.session:
        return redirect("user_login")
    
    user = get_object_or_404(UserRegistration, id=request.session["user_id"])
    
    if request.method == "POST":
        # Get form data
        username = request.POST.get("username")
        email = request.POST.get("email")
        fullname = request.POST.get("first_name") + " " + request.POST.get("last_name")
        phone = request.POST.get("phone")
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        profile_image = request.FILES.get("profile_image")
        
        # Validate username uniqueness
        if username != user.username and UserRegistration.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("update_profile")
        
        # Validate email uniqueness
        if email != user.email and UserRegistration.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("update_profile")
        
        # Update basic info
        user.username = username
        user.email = email
        user.fullname = fullname
        user.phone = phone
        
        # Handle password change
        if current_password and new_password:
            if not check_password(current_password, user.password):
                messages.error(request, "Current password is incorrect!")
                return redirect("update_profile")
            user.password = make_password(new_password)
        
        # Handle profile image
        if profile_image:
            user.profile_image = profile_image
        
        user.save()
        
        # Update session data
        request.session["user_name"] = user.fullname
        request.session["user_username"] = user.username
        
        messages.success(request, "Profile updated successfully!")
        return redirect("user_dashboard")
    
    # Split fullname into first_name and last_name for the form
    name_parts = user.fullname.split(" ", 1) if user.fullname else ["", ""]
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    context = {
        "user": user,
        "first_name": first_name,
        "last_name": last_name
    }
    return render(request, "profile_update.html", context)