from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from userapp.models import EmergencyAccessCode, UserRegistration
from django.views.decorators.csrf import ensure_csrf_cookie
import logging
import qrcode
from io import BytesIO
import base64
from django.urls import reverse

logger = logging.getLogger(__name__)

@login_required
@ensure_csrf_cookie
def view_emergency_codes(request):
    """View and manage emergency access codes"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Get the UserRegistration instance for the logged-in user
        user = UserRegistration.objects.filter(username=request.user.username).first()
        if not user:
            if is_ajax:
                return JsonResponse({"error": "User profile not found"}, status=404)
            return render(request, 'emergency_codes.html', {'error': "User profile not found"})
        
        try:
            # Get or create emergency codes
            emergency_code = EmergencyAccessCode.generate_codes(user)
            
            # Generate QR code for the emergency code itself
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(emergency_code.qr_code)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            context = {
                'qr_code': qr_image_base64,
                'access_code': emergency_code.access_code,
                'expires_at': emergency_code.expires_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as qr_error:
            logger.error(f"QR code generation error: {str(qr_error)}")
            if is_ajax:
                return JsonResponse({"error": str(qr_error)}, status=500)
            return render(request, 'emergency_codes.html', {'error': str(qr_error)})
        
        template_name = 'emergency_codes_partial.html' if is_ajax else 'emergency_codes.html'
        return render(request, template_name, context)
        
    except Exception as e:
        logger.error(f"Emergency codes view error: {str(e)}")
        if is_ajax:
            return JsonResponse({"error": str(e)}, status=500)
        return render(request, 'emergency_codes.html', {'error': str(e)})