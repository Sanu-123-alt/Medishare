"""
URL configuration for medishare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from . import views

urlpatterns = [
    path('view/<int:doctor_id>/', views.public_doctor_view, name='public_doctor_view'),
    path('admin/', admin.site.urls),
    path('doctor_register',views.doctor_register,name="doctor_register"),
    path('doctor_log',views.doctor_log,name="doctor_log"),
    path('doctor_login_check',views.doctor_login_check,name="doctor_login_check"),
    path('doctor_dashboard',views.doctor_dashboard,name="doctor_dashboard"),
    path('doctor_logout',views.doctor_logout,name="doctor_logout"),
    path('doctor_port',views.doctor_port,name="doctor_port"),
    path('doctor_appointment',views.doctor_appointment,name="doctor_appointment"),
    path('appointment_list',views.appointment_list,name="appointment_list"),
    path('appointment_create',views.appointment_create,name="appointment_create"),
    path('appointment_update/<int:slot_id>/',views.appointment_update,name="appointment_update"),
    path('appointment_delete/<int:slot_id>/',views.appointment_delete,name="appointment_delete"),
    path("booked_appointments/",views.doctor_booked_appointments, name="doctor_booked_appointments"),
    path("cancel_appointment/<int:appointment_id>/",views.doctor_cancel_appointment, name="doctor_cancel_appointment"),
    # Patient records access via security key
    path('patient_records/', views.doctor_patient_records, name="doctor_patient_records"),
    path('submit-review/', views.submit_review, name='submit_review'),
    # Profile update
    path('profile/update/', views.update_doctor_profile, name='update_doctor_profile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)