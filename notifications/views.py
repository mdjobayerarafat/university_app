from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages

from academics.models import ClassSection
from accounts.models import User
from .models import Notification, NotificationPreference
from .forms import NotificationForm, NotificationPreferenceForm


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or \
               self.request.user.is_superuser or \
               hasattr(self.request.user, 'teacher')

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)\
            .order_by('-created_at')


class CreateNotificationView(LoginRequiredMixin, StaffRequiredMixin, FormView):
    form_class = NotificationForm
    template_name = 'notifications/notification_form.html'
    success_url = reverse_lazy('notifications:list')

    def get_target_users(self, form):
        target_type = form.cleaned_data['target_type']
        users = User.objects.none()

        if target_type == 'all':
            users = User.objects.filter(is_active=True)
        elif target_type == 'department':
            department = form.cleaned_data['department']
            if department:
                users = User.objects.filter(
                    is_active=True,
                    department=department
                )
        elif target_type == 'section':
            section = form.cleaned_data['section']
            if section:
                users = User.objects.filter(
                    is_active=True,
                    enrollments__class_section=section
                ).distinct()

        return users

    def form_valid(self, form):
        users = self.get_target_users(form)
        if not users.exists():
            messages.warning(self.request, 'No users found for the selected target.')
            return self.form_invalid(form)

        notifications = []
        for user in users:
            notification = Notification(
                user=user,
                type=form.cleaned_data['type'],
                title=form.cleaned_data['title'],
                message=form.cleaned_data['message'],
                priority=form.cleaned_data['priority'],
                action_url=form.cleaned_data['action_url']
            )
            notifications.append(notification)

        Notification.objects.bulk_create(notifications)
        messages.success(self.request, f'Notification sent to {len(notifications)} users!')
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if 'department' in request.GET:
            department_id = request.GET.get('department')
            sections = ClassSection.objects.filter(
                course__department_id=department_id
            ).select_related('course')
            return JsonResponse({
                'sections': [
                    {'id': section.id, 'name': str(section)}
                    for section in sections
                ]
            })
        return super().get(request, *args, **kwargs)

class MarkNotificationReadView(LoginRequiredMixin, UpdateView):
    model = Notification

    def post(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.user == request.user:
            notification.read = True
            notification.read_at = timezone.now()
            notification.save()
        return redirect('notifications:list')

class DeleteNotificationView(LoginRequiredMixin, DeleteView):
    model = Notification
    success_url = reverse_lazy('notifications:list')

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationPreferenceView(LoginRequiredMixin, UpdateView):
    model = NotificationPreference
    form_class = NotificationPreferenceForm
    template_name = 'notifications/preference_form.html'
    success_url = reverse_lazy('notifications:preferences')

    def get_object(self, queryset=None):
        # Get or create preferences for the user
        obj, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return obj

    def form_valid(self, form):
        messages.success(self.request, 'Notification preferences updated successfully!')
        return super().form_valid(form)