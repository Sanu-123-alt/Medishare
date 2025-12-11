from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from .models import Doctor, Hospital, AppointmentSlot
from userapp.models import Review, UserRegistration, MedicalRecord, Appointment
from django.db import models
from userapp.utils import verify_otp

def doctor_register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        specialization = request.POST.get('specialization')
        hospital_id = request.POST.get('hospital')

        qualifications = request.POST.get('qualifications')
        experience = request.POST.get('experience')
        twitter = request.POST.get('twitter')
        linkedin = request.POST.get('linkedin')
        portfolio = request.POST.get('portfolio')
        bio = request.POST.get('bio')

        # validate hospital
        try:
            hospital = Hospital.objects.get(id=hospital_id)
        except Hospital.DoesNotExist:
            messages.error(request, "Invalid hospital selected.")
            return redirect("doctor_register")

        image = request.FILES.get('image')

        # prevent duplicate email
        if Doctor.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please login.")
            return redirect("doctor_log")

        doctor = Doctor(
            name=name,
            email=email,
            phone=phone,
            password=password,
            specialization=specialization,
            hospital=hospital,
            image=image,
            qualifications=qualifications,
            experience=experience,
            twitter=twitter,
            linkedin=linkedin,
            portfolio=portfolio,
            bio=bio
        )
        doctor.save()
        messages.success(request, "Doctor registered successfully! Please login.")
        return redirect('doctor_log')

    hospitals = Hospital.objects.all()
    return render(request, "doctor_registration.html", {"hospitals": hospitals})


def doctor_log(request):
    return render(request, "doctor_login.html")


def doctor_login_check(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            doctor = Doctor.objects.get(email=email, password=password)

            # Save session details
            request.session["doctor_id"] = doctor.id
            request.session["doctor_name"] = doctor.name
            request.session["doctor_email"] = doctor.email
            request.session["doctor_phone"] = doctor.phone
            request.session["doctor_specialization"] = doctor.specialization
            request.session["doctor_hospital"] = doctor.hospital.name if doctor.hospital else None
            request.session["doctor_image"] = doctor.image.url if doctor.image else None

            # new portfolio fields
            request.session["doctor_qualifications"] = doctor.qualifications
            request.session["doctor_experience"] = doctor.experience
            request.session["doctor_twitter"] = doctor.twitter
            request.session["doctor_linkedin"] = doctor.linkedin
            request.session["doctor_portfolio"] = doctor.portfolio
            request.session["doctor_bio"] = doctor.bio

            return redirect("doctor_dashboard")

        except Doctor.DoesNotExist:
            messages.error(request, "Invalid credentials. Please try again.")
            return render(request, "doctor_login.html")

    return redirect("doctor_log")


from django.utils import timezone
from datetime import datetime

def doctor_dashboard(request):
    if not request.session.get('doctor_id'):
        return redirect('doctor_login')
    
    try:
        doctor = Doctor.objects.get(id=request.session['doctor_id'])
        
        # Get appointment statistics
        total_slots = AppointmentSlot.objects.filter(doctor=doctor).count()
        available_slots = AppointmentSlot.objects.filter(doctor=doctor, status='available').count()
        booked_slots = AppointmentSlot.objects.filter(doctor=doctor, status='booked').count()
        
        # Get today's appointments
        today = timezone.now().date()
        recent_appointments = Appointment.objects.filter(
            doctor=doctor, 
            date=today
        ).order_by('time')[:5]
        
        # Current hour for greeting
        current_hour = datetime.now().hour
        
        context = {
            'doctor': doctor,
            'total_slots': total_slots,
            'available_slots': available_slots,
            'booked_slots': booked_slots,
            'recent_appointments': recent_appointments,
            'current_hour': current_hour,
        }
        
        return render(request, 'doctor_dashboard.html', context)
        
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('doctor_login')

def doctor_logout(request):
    request.session.flush()
    return redirect('choice_login')


def doctor_port(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_log")

    doctor_id = request.session.get("doctor_id")
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        # Get reviews for this doctor - using the correct field name
        reviews = Review.objects.filter(doctor=doctor).order_by('-created_at')
        
        # Process qualifications for display
        qualifications_list = []
        if doctor.qualifications:
            qualifications_list = [q.strip() for q in doctor.qualifications.split(',') if q.strip()]
        
    except Doctor.DoesNotExist:
        return redirect("doctor_log")

    return render(request, "doctor_portfolio.html", {
        "doctor": doctor,
        "reviews": reviews,
        "doctor_qualifications": qualifications_list,
        "is_public_view": False
    })

def doctor_appointment(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_log")

    doctor_id = request.session.get("doctor_id")
    # Get all appointments for this doctor
    appointments = Appointment.objects.filter(doctor_id=doctor_id).order_by("-date", "-time")
    
    # Calculate statistics
    booked_count = appointments.filter(status="booked").count()
    cancelled_count = appointments.filter(status="cancelled").count()
    completed_count = appointments.filter(status="completed").count()

    context = {
        "appointments": appointments,
        "booked_count": booked_count,
        "cancelled_count": cancelled_count,
        "completed_count": completed_count,
    }
    
    return render(request, "appointment.html", context)

def appointment_list(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_log")

    doctor_id = request.session.get("doctor_id")
    slots = AppointmentSlot.objects.filter(doctor_id=doctor_id).order_by("-date", "-time")

    return render(request, "appointment_list.html", {"slots": slots})


def appointment_create(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_log")

    if request.method == "POST":
        date = request.POST.get("date")
        time = request.POST.get("time")
        duration = request.POST.get("duration")
        status = request.POST.get("status", "available")

        doctor_id = request.session.get("doctor_id")
        doctor = get_object_or_404(Doctor, id=doctor_id)

        slot = AppointmentSlot(
            doctor=doctor,   # ✅ link slot with doctor
            date=date,
            time=time,
            duration=duration,
            status=status,
        )
        slot.save()
        messages.success(request, "Appointment Slot created successfully ✅")
        return redirect("appointment_list")

    return render(request, "appointment.html")


def appointment_update(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)

    if request.method == "POST":
        slot.date = request.POST.get("date")
        slot.time = request.POST.get("time")
        slot.duration = request.POST.get("duration")
        slot.status = request.POST.get("status")
        slot.save()
        messages.success(request, "Appointment Slot updated successfully ✏️")
        return redirect("appointment_list")

    return render(request, "appointment.html", {"slot": slot})

def appointment_delete(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    slot.delete()
    messages.success(request, "Appointment Slot deleted successfully 🗑️")
    return redirect("appointment_list")

def doctor_booked_appointments(request):
    if not request.session.get("doctor_id"):
        return redirect("doctor_log")

    doctor_id = request.session.get("doctor_id")
    # Get all appointments for this doctor where status is booked
    appointments = Appointment.objects.filter(doctor_id=doctor_id, status="booked").order_by("-date", "-time")
    
    # Calculate statistics for the template
    booked_count = appointments.count()
    total_appointments = Appointment.objects.filter(doctor_id=doctor_id).count()
    cancelled_count = Appointment.objects.filter(doctor_id=doctor_id, status="cancelled").count()

    context = {
        "appointments": appointments,
        "booked_count": booked_count,
        "total_appointments": total_appointments,
        "cancelled_count": cancelled_count,
    }
    
    return render(request, "doctor_booked_appointments.html", context)

def doctor_cancel_appointment(request, appointment_id):
    if not request.session.get("doctor_id"):
        return redirect("doctor_log")

    doctor_id = request.session.get("doctor_id")
    # Get the appointment for this doctor
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor_id=doctor_id)

    # Update the corresponding slot to available
    slot = appointment.slot
    if slot:
        slot.status = "available"
        slot.save()

    # Cancel the appointment
    appointment.status = "cancelled"
    appointment.save()
    messages.success(request, "Appointment cancelled successfully.")
    return redirect("doctor_booked_appointments")


# -------------------------
# Patient Records via Security Key (Doctor)
# -------------------------
def public_doctor_view(request, doctor_id):
    """Public view for doctor portfolio"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0
    
    # Split qualifications into a list
    qualifications_list = []
    if doctor.qualifications:
        qualifications_list = [q.strip() for q in doctor.qualifications.split(',') if q.strip()]
    
    return render(request, "doctor_portfolio.html", {
        "doctor": doctor,
        "reviews": reviews,
        "avg_rating": round(avg_rating, 1),
        "doctor_qualifications": qualifications_list,
        "is_public_view": True  # Template can use this to show/hide certain elements
    })

def doctor_patient_records(request):
    # Ensure doctor is logged in
    if not request.session.get("doctor_id"):
        return redirect("doctor_log")

    doctor_id = request.session.get("doctor_id")
    doctor = Doctor.objects.get(id=doctor_id)
    
    context = {
        "records": None, 
        "patient": None,
        "doctor": doctor
    }

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        security_key = request.POST.get("security_key", "").strip()

        if not username or not security_key:
            messages.error(request, "Username and security key are required.")
            return render(request, "doctor_patient_records.html", context)

        try:
            patient = UserRegistration.objects.get(username=username, security_key=security_key)
        except UserRegistration.DoesNotExist:
            messages.error(request, "Invalid username or security key.")
            return render(request, "doctor_patient_records.html", context)

        # Create notification about data access
        from userapp.utils import create_data_access_notification
        create_data_access_notification(patient, 'doctor', doctor)

        records = MedicalRecord.objects.filter(user=patient).order_by("-uploaded_at")
        context.update({"records": records, "patient": patient})
        return render(request, "doctor_patient_records.html", context)

    return render(request, "doctor_patient_records.html", context)


# -------------------------
# Review Submission View
# -------------------------
def submit_review(request):
    if request.method == "POST":
        entity_type = request.POST.get("entity_type")
        entity_id = request.POST.get("entity_id")
        patient_name = request.POST.get("patient_name")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        
        try:
            if entity_type == "doctor":
                doctor = Doctor.objects.get(id=entity_id)
                
                # For reviews, we need to handle the user field
                # Since this is a public form, we have several options:
                
                # Option 1: Create a temporary user for anonymous reviews
                try:
                    # Try to get or create a temporary user for the review
                    temp_user, created = UserRegistration.objects.get_or_create(
                        username=f"reviewer_{patient_name.replace(' ', '_').lower()}",
                        defaults={
                            'fullname': patient_name,
                            'email': f"{patient_name.replace(' ', '.').lower()}@temp.review",
                            'phone': '0000000000',
                            'password': 'temp_password',  # You might want to handle this differently
                            'security_key': '00000000'
                        }
                    )
                    
                    review = Review(
                        user=temp_user,
                        doctor=doctor,
                        rating=rating,
                        comment=comment
                    )
                    review.save()
                    messages.success(request, "Thank you for your review!")
                    
                except Exception as user_error:
                    # Option 2: If user creation fails, try to use a default user
                    try:
                        # Get a default user for reviews
                        default_user = UserRegistration.objects.filter(
                            username='anonymous_reviewer'
                        ).first()
                        
                        if not default_user:
                            # Create a default anonymous user for reviews
                            default_user = UserRegistration.objects.create(
                                fullname="Anonymous Reviewer",
                                username="anonymous_reviewer",
                                email="anonymous@reviews.com",
                                phone="0000000000",
                                password="default_password",
                                security_key="00000000"
                            )
                        
                        review = Review(
                            user=default_user,
                            doctor=doctor,
                            rating=rating,
                            comment=comment
                        )
                        review.save()
                        messages.success(request, "Thank you for your review!")
                        
                    except Exception as default_error:
                        messages.error(request, "Could not submit review. Please try again.")
                        print(f"Review submission error: {default_error}")
                
                # Redirect back to the appropriate page
                if request.session.get("doctor_id"):
                    return redirect("doctor_port")
                else:
                    return redirect("public_doctor_view", doctor_id=entity_id)
                    
        except Doctor.DoesNotExist:
            messages.error(request, "Doctor not found.")
            return redirect("home")
        except Exception as e:
            messages.error(request, f"Error submitting review: {str(e)}")
            return redirect("home")
    
    return redirect("home")

# -------------------------
# Profile Update
# -------------------------
def update_doctor_profile(request):
    """Update doctor profile"""
    if not request.session.get("doctor_id"):
        return redirect("doctor_log")
    
    doctor = get_object_or_404(Doctor, id=request.session.get("doctor_id"))
    
    if request.method == "POST":
        # Get form data
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        specialization = request.POST.get("specialization")
        bio = request.POST.get("bio")
        qualifications = request.POST.get("qualifications")
        experience = request.POST.get("experience")
        twitter = request.POST.get("twitter")
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        profile_image = request.FILES.get("profile_image")
        
        # Validate email uniqueness
        if email != doctor.email and Doctor.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("update_doctor_profile")
        
        # Update basic info
        doctor.name = name
        doctor.email = email
        doctor.phone = phone
        doctor.specialization = specialization
        doctor.bio = bio
        doctor.qualifications = qualifications
        if experience:
            doctor.experience = experience
        doctor.twitter = twitter
        
        # Handle password change
        if current_password and new_password:
            if doctor.password != current_password:
                messages.error(request, "Current password is incorrect!")
                return redirect("update_doctor_profile")
            doctor.password = new_password
        
        # Handle profile image
        if profile_image:
            doctor.image = profile_image
        
        doctor.save()
        
        # Update session data
        request.session["doctor_name"] = doctor.name
        request.session["doctor_email"] = doctor.email
        request.session["doctor_phone"] = doctor.phone
        request.session["doctor_specialization"] = doctor.specialization
        if doctor.image:
            request.session["doctor_image"] = doctor.image.url
        
        messages.success(request, "Profile updated successfully!")
        return redirect("doctor_dashboard")
    
    return render(request, "doctor_profile_update.html", {"doctor": doctor})