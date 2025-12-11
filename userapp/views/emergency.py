from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from userapp.models import (
    UserRegistration, EmergencyMedicalInfo, EmergencyContact, 
    MedicalRecord, Notification, EmergencyAccessCode
)
from doctor.models import Doctor, Hospital
from django.utils import timezone

def emergency_auth(request, patient_id):
    """Handle authentication for emergency code access"""
    try:
        patient = UserRegistration.objects.get(id=patient_id)
        
        # Verify that this patient has valid emergency access codes
        emergency_access = EmergencyAccessCode.objects.filter(user=patient).first()
        if not emergency_access or not emergency_access.is_valid():
            messages.error(request, "Invalid or expired emergency access. Please request new access codes.")
            return render(request, "emergency_code.html")
            
    except UserRegistration.DoesNotExist:
        messages.error(request, "Patient not found.")
        return render(request, "emergency_code.html")

    if request.method == "POST":
        professional_type = request.POST.get("professional_type")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if professional_type == "doctor":
            try:
                doctor = Doctor.objects.get(username=username)
                if doctor.password == password:  # Update this to use proper password hashing in production
                    # Create notification for patient
                    Notification.objects.create(
                        user=patient,
                        title="Emergency Access Alert",
                        message=f"Dr. {doctor.name} accessed your medical records via QR code on {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                        notification_type="emergency_access",
                        doctor=doctor
                    )

                    # Get emergency data
                    emergency_info = EmergencyMedicalInfo.objects.filter(user=patient).first()
                    emergency_contacts = EmergencyContact.objects.filter(user=patient)
                    medical_records = MedicalRecord.objects.filter(user=patient).order_by("-uploaded_at")

                    return render(request, "emergency_view.html", {
                        "patient": patient,
                        "emergency_info": emergency_info,
                        "emergency_contacts": emergency_contacts,
                        "medical_records": medical_records
                    })
                else:
                    messages.error(request, "Invalid credentials.")
            except Doctor.DoesNotExist:
                messages.error(request, "Doctor account not found.")

        elif professional_type == "hospital":
            try:
                hospital = Hospital.objects.get(username=username)
                if hospital.password == password:  # Update this to use proper password hashing in production
                    # Create notification for patient
                    Notification.objects.create(
                        user=patient,
                        title="Emergency Access Alert",
                        message=f"Hospital: {hospital.name} accessed your medical records via QR code on {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                        notification_type="emergency_access",
                        hospital=hospital
                    )

                    # Get emergency data
                    emergency_info = EmergencyMedicalInfo.objects.filter(user=patient).first()
                    emergency_contacts = EmergencyContact.objects.filter(user=patient)
                    medical_records = MedicalRecord.objects.filter(user=patient).order_by("-uploaded_at")

                    return render(request, "emergency_view.html", {
                        "patient": patient,
                        "emergency_info": emergency_info,
                        "emergency_contacts": emergency_contacts,
                        "medical_records": medical_records
                    })
                else:
                    messages.error(request, "Invalid credentials.")
            except Hospital.DoesNotExist:
                messages.error(request, "Hospital account not found.")

    return render(request, "emergency_access.html", {"patient_id": patient_id})