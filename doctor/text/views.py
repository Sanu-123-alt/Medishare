from django.shortcuts import render, redirect
from .models import Doctor, Hospital
from django.contrib import messages

def doctor_register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        specialization = request.POST.get('specialization')
        hospital_id = request.POST.get('hospital')
        hospital = Hospital.objects.get(id=hospital_id)

        image = request.FILES.get('image')

        doctor = Doctor(
            name=name,
            email=email,
            phone=phone,
            password=password,
            specialization=specialization,
            hospital=hospital,
            image=image
        )
        doctor.save()
        return redirect('doctor_log')

    hospitals = Hospital.objects.all()
    return render(request, "doctor_registration.html", {"hospitals": hospitals})

def doctor_log(request):
    return render(request,"doctor_login.html")


def doctor_login_check(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # Check if doctor exists
            doctor = Doctor.objects.get(email=email, password=password)

            # Save session details
            request.session["doctor_id"] = doctor.id
            request.session["doctor_name"] = doctor.name
            request.session["doctor_email"] = doctor.email
            request.session["doctor_phone"] = doctor.phone
            request.session["doctor_specialization"] = doctor.specialization
            request.session["doctor_hospital"] = doctor.hospital.name if doctor.hospital else None
            request.session["doctor_image"] = doctor.image.url if doctor.image else None


            return redirect("doctor_dashboard")  

        except Doctor.DoesNotExist:
            messages.error(request, "Invalid credentials. Please try again.")
            return render(request, "doctor_login.html")

    return redirect("doctor_log")

def doctor_dashboard(request):
    return render(request,"doctor_dashboard.html")

def doctor_logout(request):
    request.session.pop('doctor_id', None)
    request.session.pop('doctor_name', None)
    request.session.pop('doctor_email', None)
    request.session.pop('doctor_phone', None)
    request.session.pop('doctor_specialization', None)
    request.session.pop('doctor_hospital', None)
    request.session.pop('doctor_image', None)
    return redirect('doctor_log')   # redirect back to login page

def doctor_port(request):
    return render(request,"doctor_portfolio.html")