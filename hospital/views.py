from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import *
from userapp.models import UserRegistration, MedicalRecord
from userapp.models import Review
from doctor.models import Doctor, AppointmentSlot
from django.contrib.auth.decorators import login_required
from userapp.models import Appointment
from django.contrib.auth.hashers import make_password

# Create your views here.

def hospitaldash(request):
    if not request.session.get("u_id"):
        return redirect("log")
    
    hospital_id = request.session.get("u_id")
    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        return redirect("log")
    
    # Get dynamic data for dashboard
    from doctor.models import Doctor
    from userapp.models import Appointment
    
    total_doctors = Doctor.objects.filter(hospital=hospital).count()
    total_appointments = Appointment.objects.filter(doctor__hospital=hospital).count()
    upcoming_appointments = Appointment.objects.filter(
        doctor__hospital=hospital, 
        status='booked',
        date__gte=timezone.now().date()
    ).count()
    
    # Get recent appointments
    recent_appointments = Appointment.objects.filter(
        doctor__hospital=hospital
    ).select_related('user', 'doctor').order_by('-date')[:5]
    
    # Get recent doctors
    recent_doctors = Doctor.objects.filter(hospital=hospital)[:5]
    
    context = {
        "usr_name": request.session.get("u_name"),
        "hospital": hospital,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "upcoming_appointments": upcoming_appointments,
        "recent_appointments": recent_appointments,
        "recent_doctors": recent_doctors,
    }
    return render(request, "hospitaldashboard.html", context)

def log(request):
    return render(request, "hospital_login.html")

def hospital_save(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        location = request.POST.get('location')
        data = Hospital(name=name, email=email, phone=phone, password=password, location=location)
        data.save()
    return redirect('log')

def checkuser(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        if Hospital.objects.filter(email=email, password=password).exists():
            data = Hospital.objects.filter(email=email, password=password).values(
            'id', 'name', 'phone', 'email', 'password', 'location'
             ).first()

            request.session['u_id'] = data['id']
            request.session['u_name'] = data['name']
            request.session['u_email'] = data['email']
            request.session['u_phone'] = data['phone']
            request.session['u_password'] = data['password']
            request.session['u_location'] = data['location']

            return redirect('hospital_home')
        elif email == "admin@gmail.com" and password == "admin":
            return redirect('dash')
        else:
            return render(request, "hospital_login.html", {'msg': "Invalid user credentials"})
    else:
        return redirect('user_log')

def hospitalprofile(request):
    usr_data = {
        'usr_name': request.session.get('u_name'),
        'usr_email': request.session.get('u_email'),
        'usr_phone': request.session.get('u_phone'),
        'usr_password': request.session.get('u_password'),
        'usr_location': request.session.get('u_location'),
    }
    return render(request, "hospitaldashboard.html", usr_data)

def userlogout(request):
    request.session.pop('u_id', None)
    request.session.pop('u_name', None)
    request.session.pop('u_email', None)
    request.session.pop('u_phone', None)
    request.session.pop('u_password', None)
    request.session.pop('u_location', None)
    return redirect('choice_login')

def hospital_home(request):
    # This view is only for logged-in hospitals
    if not request.session.get("u_id"):
        return redirect("log")

    hospital_id = request.session.get("u_id")
    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        return redirect("log")

    # Get dynamic data for hospital
    from doctor.models import Doctor, AppointmentSlot
    from userapp.models import Appointment
    
    total_doctors = Doctor.objects.filter(hospital=hospital).count()
    total_appointments = Appointment.objects.filter(doctor__hospital=hospital).count()
    upcoming_appointments = Appointment.objects.filter(
        doctor__hospital=hospital, 
        status='booked',
        date__gte=timezone.now().date()
    ).count()
    
    # Get recent doctors
    recent_doctors = Doctor.objects.filter(hospital=hospital)[:5]

    context = {
        "hospital": hospital,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "upcoming_appointments": upcoming_appointments,
        "recent_doctors": recent_doctors,
        "is_hospital_admin": True  # Flag to show admin features in template
    }
    return render(request, "hospital_home.html", context)

def public_hospital_view(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    # Get hospital doctors
    doctors = Doctor.objects.filter(hospital=hospital)
    
    # Get hospital reviews - remove is_approved filter
    reviews = Review.objects.filter(hospital=hospital).order_by('-created_at')[:6]
    
    context = {
        'hospital': hospital,
        'recent_doctors': doctors[:8],
        'hospital_reviews': reviews,
        'total_doctors': doctors.count(),
        'total_appointments': 10000,
        'upcoming_appointments': 150,
    }
    
    return render(request, 'hospital_public_view.html', context)
# -------------------------
# Patient Records via Security Key (Hospital)
# -------------------------
def hospital_patient_records(request):
    if not request.session.get("u_id"):
        return redirect("log")

    hospital_id = request.session.get("u_id")
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    context = {
        "hospital": hospital,
        "records": None, 
        "patient": None,
        "usr_name": request.session.get("u_name")
    }

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        security_key = request.POST.get("security_key", "").strip()

        if not username or not security_key:
            messages.error(request, "Username and security key are required.")
            return render(request, "hospital_patient_records.html", context)

        try:
            patient = UserRegistration.objects.get(username=username, security_key=security_key)
        except UserRegistration.DoesNotExist:
            messages.error(request, "Invalid username or security key.")
            return render(request, "hospital_patient_records.html", context)

        # Get the hospital instance
        hospital = Hospital.objects.get(id=request.session.get("u_id"))
        
        # Create notification about data access (if you have this utility)
        # from userapp.utils import create_data_access_notification
        # create_data_access_notification(patient, 'hospital', hospital)

        records = MedicalRecord.objects.filter(user=patient).order_by("-uploaded_at")
        context.update({
            "records": records, 
            "patient": patient,
            "searched_username": username,
            "searched_security_key": security_key
        })
        return render(request, "hospital_patient_records.html", context)

    return render(request, "hospital_patient_records.html", context)
def hospital_management(request):
    """Hospital management dashboard view"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    hospital_id = request.session.get("u_id")
    try:
        hospital = Hospital.objects.get(id=hospital_id)
    except Hospital.DoesNotExist:
        return redirect("log")

    # Get the active tab from query parameters, default to hospital-info
    active_tab = request.GET.get('tab', 'hospital-info')

    # Get all related data
    doctors = Doctor.objects.filter(hospital=hospital)
    departments = Department.objects.filter(hospital=hospital)
    services = HospitalService.objects.filter(hospital=hospital)
    achievements = HospitalAchievement.objects.filter(hospital=hospital)

    # Print debug information
    print(f"Hospital ID: {hospital_id}")
    print(f"Hospital Name: {hospital.name}")
    print(f"Active Tab: {active_tab}")
    print(f"Number of doctors: {doctors.count()}")
    print(f"Number of departments: {departments.count()}")
    print(f"Number of services: {services.count()}")
    print(f"Number of achievements: {achievements.count()}")

    context = {
        "hospital": hospital,
        "doctors": doctors,
        "departments": departments,
        "services": services,
        "achievements": achievements,
        "active_tab": active_tab,
        "debug": True,  # Add debug flag
    }
    return render(request, "hospital_management.html", context)

def update_hospital_profile(request):
    """Update hospital profile"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    hospital = get_object_or_404(Hospital, id=request.session.get("u_id"))
    
    if request.method == "POST":
        # Get form data
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        location = request.POST.get("location")
        description = request.POST.get("description")
        ambulance_number = request.POST.get("ambulance_number")
        facilities = request.POST.get("facilities")
        specialties = request.POST.get("specialties")
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        hospital_image = request.FILES.get("hospital_image")
        
        # Validate email uniqueness
        if email != hospital.email and Hospital.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("update_hospital_profile")
        
        # Update basic info
        hospital.name = name
        hospital.email = email
        hospital.phone = phone
        hospital.location = location
        hospital.description = description
        hospital.ambulance_number = ambulance_number
        hospital.facilities = facilities
        hospital.specialties = specialties
        
        # Handle password change
        if current_password and new_password:
            if hospital.password != current_password:
                messages.error(request, "Current password is incorrect!")
                return redirect("update_hospital_profile")
            hospital.password = new_password
        
        # Handle hospital image
        if hospital_image:
            hospital.image = hospital_image
        
        hospital.save()
        
        # Update session data
        request.session["u_name"] = hospital.name
        request.session["u_email"] = hospital.email
        request.session["u_phone"] = hospital.phone
        request.session["u_location"] = hospital.location
        
        messages.success(request, "Profile updated successfully!")
        return redirect("hospital_home")
    
    return render(request, "hospital_profile_update.html", {"hospital": hospital})



# ... (your existing imports and other views remain the same)

# Doctor Management
@require_POST
def add_doctor(request):
    """Add a new doctor with all required fields"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    try:
        hospital = get_object_or_404(Hospital, id=request.session.get("u_id"))
        
        # Get all form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        specialization = request.POST.get('specialization')
        qualifications = request.POST.get('qualifications', '')
        experience = request.POST.get('experience', '')
        bio = request.POST.get('bio', '')
        consultation_fee = request.POST.get('consultation_fee', 0)
        twitter = request.POST.get('twitter', '')
        linkedin = request.POST.get('linkedin', '')
        portfolio = request.POST.get('portfolio', '')
        
        # Check if email already exists
        if Doctor.objects.filter(email=email).exists():
            messages.error(request, "A doctor with this email already exists.")
            return redirect('hospital_management')
        
        # Create doctor with all fields
        doctor = Doctor(
            hospital=hospital,
            name=name,
            email=email,
            phone=phone,
            password=make_password(password),  # Hash the password
            specialization=specialization,
            qualifications=qualifications,
            experience=experience,
            bio=bio,
            consultation_fee=consultation_fee,
            twitter=twitter,
            linkedin=linkedin,
            portfolio=portfolio
        )
        
        if request.FILES.get('image'):
            doctor.image = request.FILES['image']
        
        doctor.save()
        messages.success(request, "Doctor added successfully!")
        
    except Exception as e:
        messages.error(request, f"Error adding doctor: {str(e)}")
        print(f"Error adding doctor: {str(e)}")  # Debug print

    return redirect('hospital_management')

@require_POST
def update_doctor(request, doctor_id):
    """Update an existing doctor with all fields"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    try:
        hospital = get_object_or_404(Hospital, id=request.session.get("u_id"))
        doctor = get_object_or_404(Doctor, id=doctor_id, hospital=hospital)
        
        # Update all fields
        doctor.name = request.POST.get('name')
        doctor.email = request.POST.get('email')
        doctor.phone = request.POST.get('phone')
        doctor.specialization = request.POST.get('specialization')
        doctor.qualifications = request.POST.get('qualifications', '')
        doctor.experience = request.POST.get('experience', '')
        doctor.bio = request.POST.get('bio', '')
        doctor.twitter = request.POST.get('twitter', '')
        doctor.linkedin = request.POST.get('linkedin', '')
        doctor.portfolio = request.POST.get('portfolio', '')
        
        # Update password if provided
        if request.POST.get('password'):
            doctor.password = make_password(request.POST.get('password'))
        
        if request.FILES.get('image'):
            doctor.image = request.FILES['image']
        
        doctor.save()
        messages.success(request, "Doctor updated successfully.")
        
    except Exception as e:
        messages.error(request, f"Error updating doctor: {str(e)}")
        print(f"Error updating doctor: {str(e)}")  # Debug print

    return redirect('hospital_management')

def get_doctor(request, doctor_id):
    """Get doctor details for editing - return all fields"""
    if not request.session.get("u_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    doctor = get_object_or_404(Doctor, id=doctor_id, hospital_id=request.session.get("u_id"))
    
    return JsonResponse({
        "name": doctor.name,
        "email": doctor.email,
        "phone": doctor.phone,
        "specialization": doctor.specialization,
        "qualifications": doctor.qualifications or "",
        "experience": doctor.experience or "",
        "bio": doctor.bio or "",
        "twitter": doctor.twitter or "",
        "linkedin": doctor.linkedin or "",
        "portfolio": doctor.portfolio or "",
    })

# ... (rest of your views remain the same)

@require_POST
def delete_doctor(request, doctor_id):
    """Delete a doctor"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    doctor = get_object_or_404(Doctor, id=doctor_id, hospital_id=request.session.get("u_id"))
    doctor.delete()
    messages.success(request, "Doctor deleted successfully.")
    return redirect('hospital_management')

# Department Management
@require_POST
def add_department(request):
    """Add a new department"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    try:
        hospital = get_object_or_404(Hospital, id=request.session.get("u_id"))
        
        dept = Department(hospital=hospital)
        dept.name = request.POST.get('name')
        dept.description = request.POST.get('description')
        dept.icon = request.POST.get('icon')
        dept.save()
        messages.success(request, "Department added successfully.")
        
    except Exception as e:
        messages.error(request, f"Error adding department: {str(e)}")
    
    return redirect('hospital_management')

@require_POST
def update_department(request, dept_id):
    """Update an existing department"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    try:
        hospital = get_object_or_404(Hospital, id=request.session.get("u_id"))
        dept = get_object_or_404(Department, id=dept_id, hospital=hospital)
        
        dept.name = request.POST.get('name')
        dept.description = request.POST.get('description')
        dept.icon = request.POST.get('icon')
        dept.save()
        messages.success(request, "Department updated successfully.")
        
    except Exception as e:
        messages.error(request, f"Error updating department: {str(e)}")
        
    return redirect('hospital_management')

def get_department(request, dept_id):
    """Get department details for editing"""
    if not request.session.get("u_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    dept = get_object_or_404(Department, id=dept_id, hospital_id=request.session.get("u_id"))
    
    return JsonResponse({
        "name": dept.name,
        "description": dept.description,
        "icon": dept.icon,
    })

@require_POST
def delete_department(request, dept_id):
    """Delete a department"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    dept = get_object_or_404(Department, id=dept_id, hospital_id=request.session.get("u_id"))
    dept.delete()
    messages.success(request, "Department deleted successfully.")
    return redirect('hospital_management')

# Service Management
@require_POST
def add_service(request):
    """Add a new service"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    try:
        hospital = get_object_or_404(Hospital, id=request.session.get("u_id"))
        
        service = HospitalService(hospital=hospital)
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.icon = request.POST.get('icon')
        service.save()
        messages.success(request, "Service added successfully.")
        
    except Exception as e:
        messages.error(request, f"Error adding service: {str(e)}")
    
    return redirect('hospital_management')

@require_POST
def update_service(request, service_id):
    """Update an existing service"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    try:
        hospital = get_object_or_404(Hospital, id=request.session.get("u_id"))
        service = get_object_or_404(HospitalService, id=service_id, hospital=hospital)
        
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.icon = request.POST.get('icon')
        service.save()
        messages.success(request, "Service updated successfully.")
        
    except Exception as e:
        messages.error(request, f"Error updating service: {str(e)}")
        
    return redirect('hospital_management')

def get_service(request, service_id):
    """Get service details for editing"""
    if not request.session.get("u_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    service = get_object_or_404(HospitalService, id=service_id, hospital_id=request.session.get("u_id"))
    
    return JsonResponse({
        "name": service.name,
        "description": service.description,
        "icon": service.icon,
    })

@require_POST
def delete_service(request, service_id):
    """Delete a service"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    service = get_object_or_404(HospitalService, id=service_id, hospital_id=request.session.get("u_id"))
    service.delete()
    messages.success(request, "Service deleted successfully.")
    return redirect('hospital_management')

# Achievement Management
@require_POST
def add_achievement(request):
    """Add a new achievement"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    try:
        hospital = get_object_or_404(Hospital, id=request.session.get("u_id"))
        
        achievement = HospitalAchievement(hospital=hospital)
        achievement.title = request.POST.get('title')
        achievement.description = request.POST.get('description')
        achievement.year = request.POST.get('year')
        achievement.icon = request.POST.get('icon')
        achievement.save()
        messages.success(request, "Achievement added successfully.")
        
    except Exception as e:
        messages.error(request, f"Error adding achievement: {str(e)}")
    
    return redirect('hospital_management')

@require_POST
def update_achievement(request, achievement_id):
    """Update an existing achievement"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    try:
        hospital = get_object_or_404(Hospital, id=request.session.get("u_id"))
        achievement = get_object_or_404(HospitalAchievement, id=achievement_id, hospital=hospital)
        
        achievement.title = request.POST.get('title')
        achievement.description = request.POST.get('description')
        achievement.year = request.POST.get('year')
        achievement.icon = request.POST.get('icon')
        achievement.save()
        messages.success(request, "Achievement updated successfully.")
        
    except Exception as e:
        messages.error(request, f"Error updating achievement: {str(e)}")
        
    return redirect('hospital_management')

def get_achievement(request, achievement_id):
    """Get achievement details for editing"""
    if not request.session.get("u_id"):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    achievement = get_object_or_404(HospitalAchievement, id=achievement_id, hospital_id=request.session.get("u_id"))
    
    return JsonResponse({
        "title": achievement.title,
        "description": achievement.description,
        "year": achievement.year,
        "icon": achievement.icon,
    })

@require_POST
def delete_achievement(request, achievement_id):
    """Delete an achievement"""
    if not request.session.get("u_id"):
        return redirect("log")
    
    achievement = get_object_or_404(HospitalAchievement, id=achievement_id, hospital_id=request.session.get("u_id"))
    achievement.delete()
    messages.success(request, "Achievement deleted successfully.")
    return redirect('hospital_management')
