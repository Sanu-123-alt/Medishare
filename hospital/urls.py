from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('log', views.log, name="log"),
    path('hospital_save', views.hospital_save, name="hospital_save"),
    path('checkuser', views.checkuser, name="checkuser"),
    path('userlogout', views.userlogout, name="userlogout"),
    
    # Dashboard and Profile
    path('hospitaldash', views.hospitaldash, name="hospitaldash"),
    path('hospitalprofile', views.hospitalprofile, name="hospitalprofile"),
    path('hospital_home', views.hospital_home, name="hospital_home"),
    # Public Views
    path('view/<int:hospital_id>/', views.public_hospital_view, name="public_hospital_view"),
    path('patient_records/', views.hospital_patient_records, name="hospital_patient_records"),
    
    # Hospital Management
    path('management/', views.hospital_management, name="hospital_management"),
    path('update_hospital/', views.update_hospital_profile, name="update_hospital_profile"),
    
    # Doctor Management
    path('add_doctor/', views.add_doctor, name="add_doctor"),
    path('get_doctor/<int:doctor_id>/', views.get_doctor, name="get_doctor"),
    path('update_doctor/<int:doctor_id>/', views.update_doctor, name="update_doctor"),
    path('delete_doctor/<int:doctor_id>/', views.delete_doctor, name="delete_doctor"),
    
    # Department Management
    path('add_department/', views.add_department, name="add_department"),
    path('get_department/<int:dept_id>/', views.get_department, name="get_department"),
    path('update_department/<int:dept_id>/', views.update_department, name="update_department"),
    path('delete_department/<int:dept_id>/', views.delete_department, name="delete_department"),
    
    # Service Management
    path('add_service/', views.add_service, name="add_service"),
    path('get_service/<int:service_id>/', views.get_service, name="get_service"),
    path('update_service/<int:service_id>/', views.update_service, name="update_service"),
    path('delete_service/<int:service_id>/', views.delete_service, name="delete_service"),
    
    # Achievement Management
    path('add_achievement/', views.add_achievement, name="add_achievement"),
    path('get_achievement/<int:achievement_id>/', views.get_achievement, name="get_achievement"),
    path('update_achievement/<int:achievement_id>/', views.update_achievement, name="update_achievement"),
    path('delete_achievement/<int:achievement_id>/', views.delete_achievement, name="delete_achievement"),
]
