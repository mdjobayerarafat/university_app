import logging
import os

from django.db.models import Q
from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, UpdateView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib import messages

from academics.models import Enrollment, Assignment, ClassSection, Course, Faculty, Department, Exam
from cafeteria.models import Cafeteria, MenuItem, Order, DailyMenu
from .models import User
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm, PasswordChangeForm

# Create logger
logger = logging.getLogger(__name__)

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = form.cleaned_data['user']

        # Debug logging before login
        logger.info(f"Attempting to log in user: {user.username}")
        logger.info(f"User authentication status: {user.is_authenticated}")

        login(self.request, user)

        # Debug logging after login
        logger.info(f"Login successful for user: {user.username}")
        logger.info(f"Session ID: {self.request.session.session_key}")

        display_name = user.first_name if user.first_name else user.username
        messages.success(self.request, f'Welcome back, {display_name}!')

        next_url = self.request.GET.get('next')
        return redirect(next_url) if next_url else redirect(self.success_url)

    def form_invalid(self, form):
        # Enhanced error logging
        logger.warning("Login form validation failed")
        logger.warning(f"Form errors: {form.errors}")
        logger.warning(f"Form data: {form.cleaned_data}")

        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)
class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('login')


class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Let the form's save method handle password hashing
        user = form.save()
        # Don't call user.set_password again (form.save already does this)
        messages.success(self.request, 'Account created successfully! You can now log in.')
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'user_profile'
    login_url = '/accounts/login/'

    def get_object(self):
        return self.request.user














class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('profile')
    login_url = '/accounts/login/'

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # This adds request.FILES to the form
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'files': self.request.FILES
            })
        return kwargs

    def form_valid(self, form):
        # Check if a new profile picture was uploaded
        if 'profile_picture' in self.request.FILES:
            # Delete old profile picture if it exists
            old_picture = self.request.user.profile_picture
            if old_picture and os.path.isfile(old_picture.path):
                try:
                    os.remove(old_picture.path)
                except (FileNotFoundError, PermissionError) as e:
                    # Log the error but continue
                    logger.error(f"Failed to delete old profile picture: {e}")

        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class PasswordChangeView(LoginRequiredMixin, FormView):
    template_name = 'accounts/password_change.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profile')
    login_url = '/accounts/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.set_password(form.cleaned_data.get('new_password'))
        user.save()
        messages.success(self.request, 'Password changed successfully!')
        login(self.request, user)  # Keep user logged in
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, View):
            login_url = '/accounts/login/'
            redirect_field_name = 'next'

            def get(self, request):
                logger.info(f"Dashboard accessed by: {request.user.username} with role {request.user.role}")

                # Redirect to role-specific dashboard
                if request.user.role == 'student':
                    return self.student_dashboard(request)
                elif request.user.role == 'faculty':
                    return self.faculty_dashboard(request)
                elif request.user.role == 'staff':
                    return self.staff_dashboard(request)
                else:
                    return self.admin_dashboard(request)

            def student_dashboard(self, request):
                # Get current semester enrollments
                current_semester = "Spring 2025"
                enrollments = Enrollment.objects.filter(
                    student=request.user,
                    class_section__semester=current_semester
                ).select_related('class_section', 'class_section__course')

                # Get the first enrollment to determine the section
                enrollment = enrollments.first()
                section = enrollment.class_section if enrollment else None

                # Debugging: Print section details
                if section:
                    print(f"Section ID: {section.id}, Section Name: {section.name}")
                else:
                    print("No section found for the student.")

                # Get upcoming assignments and exams
                now = timezone.now()
                section_ids = [e.class_section_id for e in enrollments]
                assignments = Assignment.objects.filter(
                    class_section_id__in=section_ids,
                    due_date__gte=now
                ).order_by('due_date')[:5]

                exams = Exam.objects.filter(
                    class_section_id__in=section_ids,
                    date__gte=now
                ).order_by('date')[:5]

                context = {
                    'enrollments': enrollments,
                    'assignments': assignments,
                    'exams': exams,
                    'role': 'student',
                    'section': section  # Add the section to the context
                }
                return render(request, 'accounts/student_dashboard.html', context)

            def faculty_dashboard(self, request):
                # Get current teaching schedule
                current_semester = "Spring 2025"
                classes = ClassSection.objects.filter(
                    instructor__user=request.user,
                    semester=current_semester
                ).select_related('course')

                # Get upcoming assignments and exams to grade
                section_ids = [c.id for c in classes]
                assignments = Assignment.objects.filter(
                    class_section_id__in=section_ids
                ).order_by('due_date')[:5]

                # Get faculty object for the current user
                try:
                    faculty_member = Faculty.objects.get(user=request.user)
                    department = faculty_member.department

                    # Get department data
                    department_data = {
                        'faculty_count': Faculty.objects.filter(department=department).count(),
                        'course_count': Course.objects.filter(department=department).count(),
                        'student_count': get_user_model().objects.filter(role='student', department=department).count(),
                        'research_count': 15  # Placeholder - replace with actual research project count if available
                    }

                    # Get faculty list with search functionality
                    faculty_list = Faculty.objects.all()
                    department_id = request.GET.get('department')
                    search = request.GET.get('search')

                    if department_id:
                        faculty_list = faculty_list.filter(department_id=department_id)
                    if search:
                        faculty_list = faculty_list.filter(
                            Q(user__first_name__icontains=search) |
                            Q(user__last_name__icontains=search) |
                            Q(title__icontains=search)
                        )

                    # Get courses with search functionality
                    courses = Course.objects.all()
                    if department_id:
                        courses = courses.filter(department_id=department_id)
                    if search:
                        courses = courses.filter(
                            Q(name__icontains=search) |
                            Q(code__icontains=search) |
                            Q(description__icontains=search)
                        )

                except Faculty.DoesNotExist:
                    faculty_member = None
                    department = None
                    department_data = {}
                    faculty_list = Faculty.objects.none()
                    courses = Course.objects.none()

                context = {
                    'classes': classes,
                    'assignments': assignments,
                    'role': 'faculty',
                    'faculty_member': faculty_member,  # Changed from 'faculty' to 'faculty_member'
                    'departments': Department.objects.all(),
                    'department': department,
                    'department_data': department_data,
                    'faculty': faculty_list,  # Changed from 'faculty_list' to 'faculty'
                    'courses': courses
                }
                return render(request, 'accounts/faculty_dashboard.html', context)

            def staff_dashboard(self, request):
                # Get cafeteria info if staff is assigned to one
                try:
                    cafeteria = Cafeteria.objects.get(owner=request.user)
                except Cafeteria.DoesNotExist:
                    cafeteria = None

                if cafeteria:
                    # Get cafeteria-related data
                    menu_items = MenuItem.objects.filter(cafeteria=cafeteria)
                    orders = Order.objects.filter(cafeteria=cafeteria).order_by('-created_at')[:5]
                    daily_menu = DailyMenu.objects.filter(cafeteria=cafeteria, date=timezone.now().date()).first()

                    # Stats for the dashboard
                    pending_orders = Order.objects.filter(cafeteria=cafeteria, status='pending').count()
                    today_revenue = sum(order.total_price for order in Order.objects.filter(
                        cafeteria=cafeteria,
                        status='completed',
                        created_at__date=timezone.now().date()
                    ))

                    # Count items with low availability (assuming we track inventory)
                    low_stock_items = MenuItem.objects.filter(cafeteria=cafeteria, availability=False).count()

                    # Set a default customer satisfaction value
                    customer_satisfaction = 87  # Placeholder value
                else:
                    menu_items = MenuItem.objects.none()
                    orders = Order.objects.none()
                    daily_menu = None
                    pending_orders = 0
                    today_revenue = 0
                    low_stock_items = 0
                    customer_satisfaction = 0

                context = {
                    'cafeteria': cafeteria,
                    'menu_items': menu_items,  # Added the actual menu_items queryset
                    'menu_items_count': menu_items.count(),
                    'orders': orders,
                    'daily_menu': daily_menu,
                    'pending_orders': pending_orders,
                    'today_revenue': today_revenue,
                    'low_stock_items': low_stock_items,
                    'customer_satisfaction': customer_satisfaction,  # Added customer satisfaction
                    'role': 'cafeteria_staff'
                }
                return render(request, 'accounts/staff_dashboard.html', context)

            def admin_dashboard(self, request):
                context = {
                    'total_users': User.objects.count(),
                    'total_courses': Course.objects.count(),
                    'total_departments': Department.objects.count(),
                    'role': 'admin'
                }
                return render(request, 'accounts/admin_dashboard.html', context)


def debug_auth(request):
    """Temporary debug view to troubleshoot authentication issues"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if user exists
        try:
            user = User.objects.get(username=username)

            # Test direct password validation
            password_valid = user.check_password(password)

            # Test authenticate method
            auth_user = authenticate(request, username=username, password=password)

            context = {
                'user_exists': True,
                'password_valid': password_valid,
                'auth_successful': auth_user is not None,
                'is_active': user.is_active
            }
        except User.DoesNotExist:
            context = {'user_exists': False}

        return render(request, 'accounts/debug_auth.html', context)

    return render(request, 'accounts/debug_auth.html')