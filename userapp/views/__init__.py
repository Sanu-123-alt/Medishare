# Import all views from views.py
from userapp.views.reviews import add_review
from userapp.views.emergency import emergency_auth
from userapp.views.views import (
    user_home,
    choice_login,
    user_reg,
    user_register,
    user_login,
    user_logout,
    user_dashboard,
    user_appoinment,
    upload_record,
    view_records,
    delete_record,
    check_upload_access,
    book_appointment,
    my_appointments,
    cancel_appointment,
    security_key_access,
    user_notifications,
    mark_notification_read,
    emergency_access,
    emergency_dashboard,
    update_medical_info,
    generate_qr_code_api,
    add_emergency_contact,
    send_otp,
    verify_otp_view,
    update_profile,  # Add this line
)