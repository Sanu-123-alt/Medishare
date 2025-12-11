from django.contrib import admin
from django.urls import path
from . import views
from .views.reviews import add_review
from .views.qr import generate_qr  # Updated import
from .views.codes import view_emergency_codes
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.user_home, name="home"),  # Home page at root
    path("user_home/", views.user_home, name="user_home"),
    path("user_reg/", views.user_reg, name="user_reg"),
    path("choice_login/", views.choice_login, name="choice_login"),
    path("user_register/", views.user_register, name="user_register"),
    path("user_login/", views.user_login, name="user_login"),
    path("user_logout/", views.user_logout, name="user_logout"),
    path("user_appoinment/", views.user_appoinment, name="user_appoinment"),
    path("user_dashboard/", views.user_dashboard, name="user_dashboard"),
    path("upload_record/", views.upload_record, name="upload_record"),
    path("view_records/", views.view_records, name="view_records"),
    path("delete_record/<int:record_id>/", views.delete_record, name="delete_record"),
    path("check_upload_access/", views.check_upload_access, name="check_upload_access"),
    path("book/", views.book_appointment, name="book_appointment"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
    path("cancel/<int:slot_id>/", views.cancel_appointment, name="cancel_appointment"),
    path("security-access/", views.security_key_access, name="security_key_access"),
    path("notifications/", views.user_notifications, name="user_notifications"),
    path("user/notifications/mark-read/<int:notification_id>/", views.mark_notification_read, name="mark_notification_read"),
    path("reviews/add/", views.add_review, name="add_review"),
    # Emergency Features
    path("emergency/", views.emergency_dashboard, name="emergency_dashboard"),
    path("emergency/access/<int:user_id>/", views.emergency_access, name="emergency_access"),
    path("emergency/auth/<int:patient_id>/", views.emergency_auth, name="emergency_auth"),
    path("emergency/add-contact/", views.add_emergency_contact, name="add_emergency_contact"),
    path("emergency/update-medical-info/", views.update_medical_info, name="update_medical_info"),
    path("emergency/generate-qr/", generate_qr, name="generate_qr_code"),
    path("emergency/codes/", view_emergency_codes, name="view_emergency_codes"),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
    # Profile Update
    path("profile/update/", views.update_profile, name="update_profile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
