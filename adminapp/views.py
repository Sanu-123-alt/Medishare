from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# Import your models
from hospital.models import Hospital, Department, HospitalService, HospitalAchievement
from doctor.models import Doctor, AppointmentSlot
from userapp.models import UserRegistration, Appointment, Review, Feedback, MedicalRecord
from .models import AdminProfile, AdminActivity, AdminDashboardStats, AdminNotification

def admin_login_required(view_func):
    """Custom decorator to check if user is admin/staff"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_login_required
def admin_dashboard(request):
    # Calculate statistics
    total_hospitals = Hospital.objects.count()
    total_doctors = Doctor.objects.count()
    total_users = UserRegistration.objects.count()
    total_appointments = Appointment.objects.count()
    
    # Recent activities
    recent_activities = AdminActivity.objects.select_related('admin').all().order_by('-timestamp')[:10]
    
    # Recent notifications
    recent_notifications = AdminNotification.objects.all().order_by('-created_at')[:5]
    
    # Recent registrations
    recent_hospitals = Hospital.objects.all().order_by('-id')[:5]
    recent_doctors = Doctor.objects.select_related('hospital').all().order_by('-id')[:5]
    recent_users = UserRegistration.objects.all().order_by('-created_at')[:5]
    
    # Appointment statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    monthly_appointments = Appointment.objects.filter(
        date__gte=today.replace(day=1)
    ).count()
    weekly_appointments = Appointment.objects.filter(
        date__gte=week_ago
    ).count()
    
    # Update dashboard stats
    stats, created = AdminDashboardStats.objects.get_or_create(id=1)
    stats.total_hospitals = total_hospitals
    stats.total_doctors = total_doctors
    stats.total_users = total_users
    stats.total_appointments = total_appointments
    stats.save()
    
    # Log admin activity
    AdminActivity.objects.create(
        admin=request.user,
        action="Accessed Dashboard",
        ip_address=get_client_ip(request)
    )
    
    context = {
        'total_hospitals': total_hospitals,
        'total_doctors': total_doctors,
        'total_users': total_users,
        'total_appointments': total_appointments,
        'monthly_appointments': monthly_appointments,
        'weekly_appointments': weekly_appointments,
        'recent_activities': recent_activities,
        'recent_notifications': recent_notifications,
        'recent_hospitals': recent_hospitals,
        'recent_doctors': recent_doctors,
        'recent_users': recent_users,
    }
    return render(request, 'adminapp/dashboard.html', context)

# Hospital Management Views
@admin_login_required
def hospital_list(request):
    hospitals = Hospital.objects.all().order_by('-id')
    return render(request, 'adminapp/hospitals/list.html', {'hospitals': hospitals})

@admin_login_required
def hospital_add(request):
    if request.method == 'POST':
        try:
            hospital = Hospital.objects.create(
                name=request.POST['name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                password=make_password(request.POST['password']),
                location=request.POST['location'],
                description=request.POST.get('description', ''),
                google_maps_link=request.POST.get('google_maps_link', ''),
                established_year=request.POST.get('established_year'),
                website=request.POST.get('website', ''),
                emergency_contact=request.POST.get('emergency_contact', ''),
                ambulance_number=request.POST.get('ambulance_number', ''),
            )
            
            if 'image' in request.FILES:
                hospital.image = request.FILES['image']
                hospital.save()
            
            # Create notification
            AdminNotification.objects.create(
                title="New Hospital Registered",
                message=f"Hospital '{hospital.name}' has been registered.",
                notification_type='hospital_registration',
                related_hospital=hospital
            )
            
            # Log activity
            AdminActivity.objects.create(
                admin=request.user,
                action=f"Added hospital: {hospital.name}",
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Hospital added successfully!')
            return redirect('hospital_list')
            
        except Exception as e:
            messages.error(request, f'Error adding hospital: {str(e)}')
    
    return render(request, 'adminapp/hospitals/add.html')

@admin_login_required
def hospital_edit(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    context = {
        'hospital': hospital,
        'unread_notifications_count': AdminNotification.objects.filter(is_read=False).count(),
    }
    
    if request.method == 'POST':
        try:
            hospital.name = request.POST['name']
            hospital.email = request.POST['email']
            hospital.phone = request.POST['phone']
            hospital.location = request.POST['location']
            hospital.description = request.POST.get('description', '')
            hospital.google_maps_link = request.POST.get('google_maps_link', '')
            hospital.established_year = request.POST.get('established_year')
            hospital.website = request.POST.get('website', '')
            hospital.emergency_contact = request.POST.get('emergency_contact', '')
            hospital.ambulance_number = request.POST.get('ambulance_number', '')
            
            # Update password if provided
            if request.POST.get('password'):
                hospital.password = make_password(request.POST['password'])
            
            # Handle image removal
            if request.POST.get('remove_image') == 'true':
                hospital.image.delete(save=False)
            
            # Handle new image upload
            if 'image' in request.FILES:
                hospital.image = request.FILES['image']
            
            hospital.save()
            
            # Log activity
            AdminActivity.objects.create(
                admin=request.user,
                action=f"Edited hospital: {hospital.name}",
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Hospital updated successfully!')
            return redirect('hospital_list')
            
        except Exception as e:
            messages.error(request, f'Error updating hospital: {str(e)}')
    
    return render(request, 'adminapp/hospitals/edit.html', context)

@admin_login_required
def hospital_delete(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    if request.method == 'POST':
        hospital_name = hospital.name
        hospital.delete()
        
        # Log activity
        AdminActivity.objects.create(
            admin=request.user,
            action=f"Deleted hospital: {hospital_name}",
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, 'Hospital deleted successfully!')
        return redirect('hospital_list')
    
    return render(request, 'adminapp/hospitals/delete.html', {'hospital': hospital})

# Doctor Management Views
@admin_login_required
def doctor_list(request):
    doctors = Doctor.objects.select_related('hospital').all().order_by('-id')
    return render(request, 'adminapp/doctors/list.html', {'doctors': doctors})

@admin_login_required
def doctor_add(request):
    hospitals = Hospital.objects.all()
    
    if request.method == 'POST':
        try:
            hospital = Hospital.objects.get(id=request.POST['hospital'])
            
            doctor = Doctor.objects.create(
                name=request.POST['name'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                password=make_password(request.POST['password']),
                specialization=request.POST['specialization'],
                hospital=hospital,
                qualifications=request.POST.get('qualifications', ''),
                experience=request.POST.get('experience', ''),
                twitter=request.POST.get('twitter', ''),
                linkedin=request.POST.get('linkedin', ''),
                portfolio=request.POST.get('portfolio', ''),
                bio=request.POST.get('bio', ''),
            )
            
            if 'image' in request.FILES:
                doctor.image = request.FILES['image']
                doctor.save()
            
            # Create notification
            AdminNotification.objects.create(
                title="New Doctor Registered",
                message=f"Dr. {doctor.name} has been registered.",
                notification_type='doctor_registration',
                related_doctor=doctor
            )
            
            # Log activity
            AdminActivity.objects.create(
                admin=request.user,
                action=f"Added doctor: {doctor.name}",
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Doctor added successfully!')
            return redirect('doctor_list')
            
        except Exception as e:
            messages.error(request, f'Error adding doctor: {str(e)}')
    
    return render(request, 'adminapp/doctors/add.html', {'hospitals': hospitals})

@admin_login_required
def doctor_edit(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    hospitals = Hospital.objects.all()
    
    if request.method == 'POST':
        try:
            hospital = Hospital.objects.get(id=request.POST['hospital'])
            
            doctor.name = request.POST['name']
            doctor.email = request.POST['email']
            doctor.phone = request.POST['phone']
            doctor.specialization = request.POST['specialization']
            doctor.hospital = hospital
            doctor.qualifications = request.POST.get('qualifications', '')
            doctor.experience = request.POST.get('experience', '')
            doctor.twitter = request.POST.get('twitter', '')
            doctor.linkedin = request.POST.get('linkedin', '')
            doctor.portfolio = request.POST.get('portfolio', '')
            doctor.bio = request.POST.get('bio', '')
            
            # Update password if provided
            if request.POST.get('password'):
                doctor.password = make_password(request.POST['password'])
            
            if 'image' in request.FILES:
                doctor.image = request.FILES['image']
            
            doctor.save()
            
            # Log activity
            AdminActivity.objects.create(
                admin=request.user,
                action=f"Edited doctor: {doctor.name}",
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Doctor updated successfully!')
            return redirect('doctor_list')
            
        except Exception as e:
            messages.error(request, f'Error updating doctor: {str(e)}')
    
    return render(request, 'adminapp/doctors/edit.html', {
        'doctor': doctor,
        'hospitals': hospitals
    })

@admin_login_required
def doctor_delete(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        doctor_name = doctor.name
        doctor.delete()
        
        # Log activity
        AdminActivity.objects.create(
            admin=request.user,
            action=f"Deleted doctor: {doctor_name}",
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, 'Doctor deleted successfully!')
        return redirect('doctor_list')
    
    return render(request, 'adminapp/doctors/delete.html', {'doctor': doctor})

# User Management Views
@admin_login_required
def user_list(request):
    users = UserRegistration.objects.all().order_by('-created_at')
    return render(request, 'adminapp/users/list.html', {'users': users})

@admin_login_required
def user_add(request):
    if request.method == 'POST':
        try:
            user = UserRegistration.objects.create(
                fullname=request.POST['fullname'],
                username=request.POST['username'],
                email=request.POST['email'],
                phone=request.POST['phone'],
                password=make_password(request.POST['password']),
                security_key=request.POST['security_key'],
            )
            
            # Create notification
            AdminNotification.objects.create(
                title="New User Registered",
                message=f"User '{user.fullname}' has been registered.",
                notification_type='user_registration',
                related_user=user
            )
            
            # Log activity
            AdminActivity.objects.create(
                admin=request.user,
                action=f"Added user: {user.fullname}",
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'User added successfully!')
            return redirect('user_list')
            
        except Exception as e:
            messages.error(request, f'Error adding user: {str(e)}')
    
    return render(request, 'adminapp/users/add.html')

@admin_login_required
def user_edit(request, user_id):
    user = get_object_or_404(UserRegistration, id=user_id)
    
    if request.method == 'POST':
        try:
            user.fullname = request.POST['fullname']
            user.username = request.POST['username']
            user.email = request.POST['email']
            user.phone = request.POST['phone']
            user.security_key = request.POST['security_key']
            
            # Update password if provided
            if request.POST.get('password'):
                user.password = make_password(request.POST['password'])
            
            user.save()
            
            # Log activity
            AdminActivity.objects.create(
                admin=request.user,
                action=f"Edited user: {user.fullname}",
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'User updated successfully!')
            return redirect('user_list')
            
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    return render(request, 'adminapp/users/edit.html', {'user': user})

@admin_login_required
def user_delete(request, user_id):
    user = get_object_or_404(UserRegistration, id=user_id)
    
    if request.method == 'POST':
        user_name = user.fullname
        user.delete()
        
        # Log activity
        AdminActivity.objects.create(
            admin=request.user,
            action=f"Deleted user: {user_name}",
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, 'User deleted successfully!')
        return redirect('user_list')
    
    return render(request, 'adminapp/users/delete.html', {'user': user})

# Admin Management Views
@admin_login_required
def admin_list(request):
    admins = AdminProfile.objects.select_related('user').all()
    return render(request, 'adminapp/admins/list.html', {'admins': admins})

@admin_login_required
def admin_add(request):
    if request.method == 'POST':
        try:
            # Create Django User
            user = User.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password'],
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                is_staff=True
            )
            
            # Create AdminProfile
            admin_profile = AdminProfile.objects.create(
                user=user,
                phone=request.POST.get('phone', ''),
                department=request.POST.get('department', ''),
                role=request.POST.get('role', 'General Admin')
            )
            
            # Log activity
            AdminActivity.objects.create(
                admin=request.user,
                action=f"Added admin: {user.username}",
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Admin added successfully!')
            return redirect('admin_list')
            
        except Exception as e:
            messages.error(request, f'Error adding admin: {str(e)}')
    
    return render(request, 'adminapp/admins/add.html')

@admin_login_required
def admin_edit(request, admin_id):
    admin_profile = get_object_or_404(AdminProfile, id=admin_id)
    
    if request.method == 'POST':
        try:
            user = admin_profile.user
            user.username = request.POST['username']
            user.email = request.POST['email']
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            
            # Update password if provided
            if request.POST.get('password'):
                user.set_password(request.POST['password'])
            
            user.save()
            
            admin_profile.phone = request.POST.get('phone', '')
            admin_profile.department = request.POST.get('department', '')
            admin_profile.role = request.POST.get('role', 'General Admin')
            admin_profile.save()
            
            # Log activity
            AdminActivity.objects.create(
                admin=request.user,
                action=f"Edited admin: {user.username}",
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, 'Admin updated successfully!')
            return redirect('admin_list')
            
        except Exception as e:
            messages.error(request, f'Error updating admin: {str(e)}')
    
    return render(request, 'adminapp/admins/edit.html', {'admin_profile': admin_profile})

@admin_login_required
def admin_delete(request, admin_id):
    admin_profile = get_object_or_404(AdminProfile, id=admin_id)
    
    if request.method == 'POST':
        # Prevent self-deletion
        if admin_profile.user == request.user:
            messages.error(request, 'You cannot delete your own account!')
            return redirect('admin_list')
        
        admin_name = admin_profile.user.username
        user = admin_profile.user
        admin_profile.delete()
        user.delete()
        
        # Log activity
        AdminActivity.objects.create(
            admin=request.user,
            action=f"Deleted admin: {admin_name}",
            ip_address=get_client_ip(request)
        )
        
        messages.success(request, 'Admin deleted successfully!')
        return redirect('admin_list')
    
    return render(request, 'adminapp/admins/delete.html', {'admin_profile': admin_profile})

# Notification and Activity Views
@admin_login_required
def notification_list(request):
    notifications = AdminNotification.objects.all().order_by('-created_at')
    
    # Calculate statistics
    total_count = notifications.count()
    read_count = notifications.filter(is_read=True).count()
    today_count = notifications.filter(created_at__date=timezone.now().date()).count()
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'total_count': total_count,
        'read_count': read_count,
        'today_count': today_count,
        'unread_notifications_count': AdminNotification.objects.filter(is_read=False).count(),
    }
    return render(request, 'adminapp/notifications/list.html', context)

@admin_login_required
def activity_list(request):
    activities = AdminActivity.objects.select_related('admin').all().order_by('-timestamp')
    
    # Calculate statistics
    total_count = activities.count()
    today_count = activities.filter(timestamp__date=timezone.now().date()).count()
    admin_count = activities.values('admin').distinct().count()
    unique_ips = activities.exclude(ip_address__isnull=True).values('ip_address').distinct().count()
    
    # Get all admins for filter
    admins = User.objects.filter(is_staff=True)
    
    # Pagination
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'activities': page_obj,
        'admins': admins,
        'total_count': total_count,
        'today_count': today_count,
        'admin_count': admin_count,
        'unique_ips': unique_ips,
        'unread_notifications_count': AdminNotification.objects.filter(is_read=False).count(),
    }
    return render(request, 'adminapp/activities/list.html', context)

# AJAX views for notifications
@admin_login_required
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(AdminNotification, id=notification_id)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})

@admin_login_required
@require_POST
def mark_all_notifications_read(request):
    AdminNotification.objects.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

@admin_login_required
@require_POST
def delete_notification(request, notification_id):
    notification = get_object_or_404(AdminNotification, id=notification_id)
    notification.delete()
    return JsonResponse({'success': True})

@admin_login_required
@require_POST
def clear_all_notifications(request):
    AdminNotification.objects.all().delete()
    return JsonResponse({'success': True})

@admin_login_required
@require_POST
def clear_old_activities(request):
    # Delete activities older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    old_activities = AdminActivity.objects.filter(timestamp__lt=cutoff_date)
    count = old_activities.count()
    old_activities.delete()
    
    return JsonResponse({'success': True, 'count': count})

# Analytics Views
@admin_login_required
def analytics(request):
    # Hospital statistics
    hospitals_by_location = Hospital.objects.values('location').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Doctor statistics
    doctors_by_specialization = Doctor.objects.values('specialization').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Appointment statistics
    appointments_by_status = Appointment.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Monthly appointments
    from django.db.models.functions import TruncMonth
    monthly_appointments = Appointment.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    context = {
        'hospitals_by_location': hospitals_by_location,
        'doctors_by_specialization': doctors_by_specialization,
        'appointments_by_status': appointments_by_status,
        'monthly_appointments': monthly_appointments,
    }
    return render(request, 'adminapp/analytics.html', context)

# Utility function
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip