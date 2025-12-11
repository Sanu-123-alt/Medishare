import qrcode
from io import BytesIO
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from userapp.models import EmergencyAccessCode, UserRegistration
import logging

logger = logging.getLogger(__name__)

@csrf_protect
def generate_qr(request):
    """Generate QR code for emergency access"""
    if not request.session.get('is_authenticated') or not request.session.get('user_id'):
        return JsonResponse({
            "success": False, 
            "login_required": True,
            "error": "Please log in to generate QR code"
        }, status=401)
        
    try:
        # Get the user's registration record
        user = UserRegistration.objects.get(id=request.session['user_id'])
        if not user:
            return JsonResponse({
                "success": False, 
                "error": "User profile not found. Please complete your profile."
            }, status=404)

        # Get or create emergency codes
        emergency_code = EmergencyAccessCode.generate_codes(user)
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Generate the emergency access URL with fixed IP
        host = '10.66.142.94'  # Your network IP address
        access_url = f"http://{host}:8000{reverse('emergency_access', args=[user.id])}"
        
        # Add the URL to the QR code
        qr.add_data(access_url)
        qr.make(fit=True)
        
        # Create the QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue()).decode()
        
        return JsonResponse({
            "success": True,
            "qr_code": f"data:image/png;base64,{qr_image}",
            "qr_data": access_url,
            "access_code": emergency_code.access_code,
            "expires_at": emergency_code.expires_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        logger.error(f"QR generation error: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
