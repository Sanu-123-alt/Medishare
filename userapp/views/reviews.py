from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from userapp.models import Review
from doctor.models import Doctor, Hospital

def add_review(request):
    if "user_id" not in request.session:
        return JsonResponse({
            'status': 'error',
            'message': 'Please log in to submit a review'
        }, status=401)

    if request.method == "POST":
        user = request.user
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        entity_type = request.POST.get("entity_type")  # 'doctor' or 'hospital'
        entity_id = request.POST.get("entity_id")

        if not all([rating, comment, entity_type, entity_id]):
            return JsonResponse({
                'status': 'error',
                'message': 'All fields are required!'
            }, status=400)

        try:
            review = Review(
                user_id=request.session["user_id"],
                rating=rating,
                comment=comment
            )

            if entity_type == "doctor":
                doctor = get_object_or_404(Doctor, id=entity_id)
                review.doctor = doctor
            else:
                hospital = get_object_or_404(Hospital, id=entity_id)
                review.hospital = hospital

            review.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Thank you for your review!',
                'review': {
                    'rating': review.rating,
                    'comment': review.comment,
                    'created_at': review.created_at.strftime('%B %d, %Y')
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)