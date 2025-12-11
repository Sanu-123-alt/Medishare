from django.urls import path
from . import views
from .auth_views import admin_login, admin_logout

urlpatterns = [
    # Authentication
    path('login/', admin_login, name='admin_login'),
    path('logout/', admin_logout, name='admin_logout'),
    
    # Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # Hospital Management
    path('hospitals/', views.hospital_list, name='hospital_list'),
    path('hospitals/add/', views.hospital_add, name='hospital_add'),
    path('hospitals/edit/<int:hospital_id>/', views.hospital_edit, name='hospital_edit'),
    path('hospitals/delete/<int:hospital_id>/', views.hospital_delete, name='hospital_delete'),
    
    # Doctor Management
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.doctor_add, name='doctor_add'),
    path('doctors/edit/<int:doctor_id>/', views.doctor_edit, name='doctor_edit'),
    path('doctors/delete/<int:doctor_id>/', views.doctor_delete, name='doctor_delete'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:user_id>/', views.user_delete, name='user_delete'),
    
    # Admin Management
    path('admins/', views.admin_list, name='admin_list'),
    path('admins/add/', views.admin_add, name='admin_add'),
    path('admins/edit/<int:admin_id>/', views.admin_edit, name='admin_edit'),
    path('admins/delete/<int:admin_id>/', views.admin_delete, name='admin_delete'),
    
    # Notifications & Activities
    path('notifications/', views.notification_list, name='notification_list'),
    path('activities/', views.activity_list, name='activity_list'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),

        # Notifications AJAX endpoints
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),

    # Activities AJAX endpoints
    path('activities/clear-old/', views.clear_old_activities, name='clear_old_activities'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
]