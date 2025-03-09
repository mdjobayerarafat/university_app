from django.shortcuts import render
from django.http import JsonResponse
from .models import FAQ
from difflib import SequenceMatcher
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import PrivateMessage

def calculate_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def chatbot_view(request):
    return render(request, 'chatbot/chat.html')


def get_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        # Find the most similar FAQ
        faqs = FAQ.objects.all()
        best_match = None
        highest_similarity = 0

        for faq in faqs:
            similarity = calculate_similarity(user_message, faq.question)
            if similarity > highest_similarity and similarity > 0.6:
                highest_similarity = similarity
                best_match = faq

        if best_match:
            response = best_match.answer
        else:
            response = "I'm sorry, I don't have an answer for that question."

        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)


User = get_user_model()


@login_required
def message_view(request):
    # Check if user has either student or teacher profile
    user_role = None
    if hasattr(request.user, 'student'):
        user_role = 'student'
    elif hasattr(request.user, 'teacher'):
        user_role = 'teacher'

    if not user_role:
        # Instead of returning a 403 error, redirect to an error page or display a message
        return render(request, 'chatbot/access_denied.html', {
            'message': 'You must be a student or teacher to use the messaging system.'
        })

    # Get available users to message
    if user_role == 'student':
        available_users = User.objects.filter(teacher__isnull=False)
    else:  # teacher
        available_users = User.objects.filter(student__isnull=False)

    return render(request, 'chatbot/messages.html', {
        'available_users': available_users,
        'user_role': user_role
    })
@login_required
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    recipient_id = request.POST.get('recipient_id')
    message_text = request.POST.get('message', '').strip()

    if not recipient_id or not message_text:
        return JsonResponse({'error': 'Missing data'}, status=400)

    try:
        recipient = User.objects.get(id=recipient_id)

        # Verify sender and recipient roles
        sender_is_student = hasattr(request.user, 'student')
        recipient_is_teacher = hasattr(recipient, 'teacher')

        if (sender_is_student and not recipient_is_teacher) or \
                (not sender_is_student and recipient_is_teacher):
            return JsonResponse({'error': 'Invalid recipient'}, status=403)

        message = PrivateMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            message=message_text
        )

        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'text': message.message,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'Recipient not found'}, status=404)


@login_required
def get_messages(request):
    other_user_id = request.GET.get('user_id')
    if not other_user_id:
        return JsonResponse({'error': 'Missing user_id'}, status=400)

    try:
        other_user = User.objects.get(id=other_user_id)
        messages = PrivateMessage.objects.filter(
            Q(sender=request.user, recipient=other_user) |
            Q(sender=other_user, recipient=request.user)
        ).order_by('created_at')

        # Mark messages as read
        messages.filter(recipient=request.user, is_read=False).update(is_read=True)

        return JsonResponse({
            'messages': [{
                'id': msg.id,
                'sender': msg.sender.get_full_name() or msg.sender.username,
                'text': msg.message,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_mine': msg.sender == request.user
            } for msg in messages]
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)