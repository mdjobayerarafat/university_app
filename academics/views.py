from datetime import datetime
from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO

import datetime

from . import forms
from .forms import FacultyEditForm, AssignmentForm, ExamForm
from .models import Department, Faculty, Course, ClassSection, Enrollment, Assignment, Exam, ClassSchedule, ClassRoutine
from .forms import (
    FacultyEditForm,
    EducationFormSet,
    PublicationFormSet
)

class DepartmentListView(ListView):
    model = Department
    template_name = 'academics/departments.html'
    context_object_name = 'departments'


class DepartmentDetailView(DetailView):
    model = Department
    template_name = 'academics/department_detail.html'
    context_object_name = 'department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department = self.object
        context['faculty'] = Faculty.objects.filter(department=department)
        context['courses'] = Course.objects.filter(department=department)
        return context


class FacultyListView(ListView):
    model = Faculty
    template_name = 'academics/faculty_list.html'
    context_object_name = 'faculty'

    def get_queryset(self):
        queryset = Faculty.objects.all()
        department_id = self.request.GET.get('department')
        search = self.request.GET.get('search')

        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(title__icontains=search)
            )

        return queryset


class FacultyDetailView(DetailView):
    model = Faculty
    template_name = 'academics/faculty_detail.html'
    context_object_name = 'faculty_member'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.object
        current_semester = "Spring 2025"  # This could be determined programmatically
        context['classes'] = ClassSection.objects.filter(instructor=faculty, semester=current_semester)
        return context



class FacultyEditView(LoginRequiredMixin, View):
    template_name = 'academics/faculty/edit_profile.html'

    def get(self, request):
        try:
            faculty = Faculty.objects.get(user=request.user)
            form = FacultyEditForm(instance=faculty)
            education_formset = EducationFormSet(instance=faculty, prefix='education')
            publication_formset = PublicationFormSet(instance=faculty, prefix='publication')
            return render(request, self.template_name, {
                'form': form,
                'faculty': faculty,
                'education_formset': education_formset,
                'publication_formset': publication_formset
            })
        except Faculty.DoesNotExist:
            messages.error(request, "You don't have faculty privileges.")
            return redirect('home')

    def post(self, request):
        try:
            faculty = Faculty.objects.get(user=request.user)
            form = FacultyEditForm(request.POST, request.FILES, instance=faculty)
            education_formset = EducationFormSet(request.POST, instance=faculty, prefix='education')
            publication_formset = PublicationFormSet(request.POST, instance=faculty, prefix='publication')

            if (form.is_valid() and education_formset.is_valid()
                and publication_formset.is_valid()):
                user = faculty.user
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
                user.save()

                form.save()
                education_formset.save()
                publication_formset.save()

                messages.success(request, "Profile updated successfully.")
                return redirect('academics:faculty_detail', pk=faculty.pk)

            return render(request, self.template_name, {
                'form': form,
                'faculty': faculty,
                'education_formset': education_formset,
                'publication_formset': publication_formset
            })
        except Faculty.DoesNotExist:
            messages.error(request, "You don't have faculty privileges.")
            return redirect('home')
class CourseListView(ListView):
    model = Course
    template_name = 'academics/courses.html'
    context_object_name = 'courses'

    def get_queryset(self):
        queryset = Course.objects.all()
        department_id = self.request.GET.get('department')
        search = self.request.GET.get('search')

        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset


class CourseDetailView(DetailView):
    model = Course
    template_name = 'academics/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        current_semester = "Spring 2025"  # This could be determined programmatically
        context['sections'] = ClassSection.objects.filter(course=course, semester=current_semester)
        return context


class ClassScheduleView(LoginRequiredMixin, DetailView):
    model = ClassSection
    template_name = 'academics/class_schedule.html'
    context_object_name = 'section'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = self.object

        # Get all schedules for this class section
        context['schedules'] = section.schedules.all().order_by('day')

        # Add day labels dictionary for easy rendering
        context['day_labels'] = dict(ClassSchedule.DAYS)

        # Add enrollment status if user is logged in
        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user,
                class_section=section
            ).exists()

        return context
class MyScheduleView(LoginRequiredMixin, View):
            template_name = 'academics/my_schedule.html'

            def get(self, request, section_id=None):
                # Get current semester enrollments
                current_semester = "Spring 2025"  # Could be determined programmatically
                enrollments = Enrollment.objects.filter(
                    student=self.request.user,
                    class_section__semester=current_semester
                ).select_related('class_section', 'class_section__course', 'class_section__instructor')

                # Check if user has any enrollments
                if not enrollments.exists():
                    context = {
                        'no_enrollments': True,
                        'day_labels': dict(ClassSchedule.DAYS)
                    }
                    messages.info(request, "You are not enrolled in any classes this semester.")
                    return render(request, self.template_name, context)

                # Get the section ID from the URL parameter or query param or use the first enrollment
                if section_id:
                    try:
                        # Verify user is enrolled in this section
                        section = ClassSection.objects.get(
                            id=section_id,
                            enrollments__student=request.user
                        )
                    except ClassSection.DoesNotExist:
                        # If not enrolled or doesn't exist, use first enrollment
                        section = enrollments.first().class_section
                else:
                    section_id_from_query = request.GET.get('section')
                    if section_id_from_query:
                        try:
                            section = ClassSection.objects.get(
                                id=section_id_from_query,
                                enrollments__student=request.user
                            )
                        except ClassSection.DoesNotExist:
                            section = enrollments.first().class_section
                    else:
                        # Default to first enrollment if no section specified
                        section = enrollments.first().class_section

                # Get all schedules for this specific section
                schedules = section.schedules.all().order_by('day')

                # Get upcoming assignments and exams for this section
                now = timezone.now()
                upcoming_assignments = Assignment.objects.filter(
                    class_section=section,
                    due_date__gte=now
                ).order_by('due_date')[:5]

                upcoming_exams = Exam.objects.filter(
                    class_section=section,
                    date__gte=now
                ).order_by('date')[:5]

                context = {
                    'section': section,
                    'schedules': schedules,
                    'day_labels': dict(ClassSchedule.DAYS),
                    'upcoming_assignments': upcoming_assignments,
                    'upcoming_exams': upcoming_exams,
                    'enrollments': enrollments,
                    'is_enrolled': True,
                    'no_enrollments': False
                }

                return render(request, self.template_name, context)

class ClassSectionDetailView(DetailView):
    model = ClassSection
    template_name = 'academics/class_section_detail.html'
    context_object_name = 'section'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = self.object
        context['schedules'] = section.schedules.all()
        context['assignments'] = Assignment.objects.filter(class_section=section).order_by('due_date')
        context['exams'] = Exam.objects.filter(class_section=section).order_by('date')

        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user,
                class_section=section
            ).exists()

        return context


class EnrollView(LoginRequiredMixin, View):
    def post(self, request, pk):
        section = get_object_or_404(ClassSection, pk=pk)

        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, class_section=section).exists():
            messages.warning(request, "You are already enrolled in this class.")
            return redirect('academics:class_section_detail', pk=pk)

        # Check if class is full
        if section.enrolled >= section.capacity:
            messages.error(request, "This class is full.")
            return redirect('academics:class_section_detail', pk=pk)

        # Create enrollment
        Enrollment.objects.create(student=request.user, class_section=section)

        # Update enrolled count
        section.enrolled += 1
        section.save()

        messages.success(request, f"Successfully enrolled in {section.course.code} {section.section_number}.")
        return redirect('academics:my_schedule')


class DropClassView(LoginRequiredMixin, View):
    def post(self, request, pk):
        section = get_object_or_404(ClassSection, pk=pk)

        # Check if enrolled
        enrollment = Enrollment.objects.filter(student=request.user, class_section=section).first()
        if not enrollment:
            messages.warning(request, "You are not enrolled in this class.")
            return redirect('academics:class_section_detail', pk=pk)

        # Delete enrollment
        enrollment.delete()

        # Update enrolled count
        section.enrolled -= 1
        section.save()

        messages.success(request, f"Successfully dropped {section.course.code} {section.section_number}.")
        return redirect('academics:my_schedule')


class AssignmentListView(LoginRequiredMixin, ListView):
    template_name = 'academics/assignments.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        # Get all class sections the student is enrolled in
        enrollments = Enrollment.objects.filter(student=self.request.user)
        section_ids = [e.class_section_id for e in enrollments]

        # Get assignments for those sections
        queryset = Assignment.objects.filter(class_section_id__in=section_ids)

        # Filter by status if provided
        status = self.request.GET.get('status')
        if status == 'upcoming':
            queryset = queryset.filter(due_date__gte=timezone.now())
        elif status == 'past':
            queryset = queryset.filter(due_date__lt=timezone.now())

        return queryset.order_by('due_date')



class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'academics/faculty/assignment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_section'] = get_object_or_404(ClassSection, pk=self.kwargs['class_pk'])
        return context

    def form_valid(self, form):
        class_section = get_object_or_404(ClassSection, pk=self.kwargs['class_pk'])
        faculty = get_object_or_404(Faculty, user=self.request.user)

        if class_section.instructor != faculty:
            messages.error(self.request, "You are not authorized to add assignments to this class.")
            return redirect('academics:faculty_dashboard')

        form.instance.class_section = class_section
        messages.success(self.request, "Assignment created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('academics:faculty_class_detail',
                          kwargs={'pk': self.kwargs['class_pk']})

class AssignmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'academics/faculty/assignment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_section'] = self.object.class_section
        return context

    def get_success_url(self):
        return reverse_lazy('academics:faculty_class_detail',
                          kwargs={'pk': self.object.class_section.id})

    def dispatch(self, request, *args, **kwargs):
        assignment = self.get_object()
        faculty = get_object_or_404(Faculty, user=request.user)

        if assignment.class_section.instructor != faculty:
            messages.error(request, "You are not authorized to edit this assignment.")
            return redirect('academics:faculty_dashboard')
        return super().dispatch(request, *args, **kwargs)


class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Assignment
    template_name = 'academics/faculty/assignment_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('academics:faculty_class_detail',
                            kwargs={'pk': self.object.class_section.id})

    def dispatch(self, request, *args, **kwargs):
        assignment = self.get_object()
        faculty = get_object_or_404(Faculty, user=request.user)

        if assignment.class_section.instructor != faculty:
            messages.error(request, "You are not authorized to delete this assignment.")
            return redirect('academics:faculty_dashboard')
        return super().dispatch(request, *args, **kwargs)
class ExamListView(LoginRequiredMixin, ListView):
    template_name = 'academics/exams.html'
    context_object_name = 'exams'

    def get_queryset(self):
        # Get all class sections the student is enrolled in
        enrollments = Enrollment.objects.filter(student=self.request.user)
        section_ids = [e.class_section_id for e in enrollments]

        # Get exams for those sections
        queryset = Exam.objects.filter(class_section_id__in=section_ids)

        # Filter by status if provided
        status = self.request.GET.get('status')
        if status == 'upcoming':
            queryset = queryset.filter(date__gte=timezone.now())
        elif status == 'past':
            queryset = queryset.filter(date__lt=timezone.now())

        return queryset.order_by('date')

class FacultyDashboardView(LoginRequiredMixin, View):
    template_name = 'academics/faculty/dashboard.html'

    def get(self, request):
        try:
            faculty = Faculty.objects.get(user=request.user)
            is_department_head = faculty.is_department_head()
            current_semester = "Spring 2025"  # Could be determined programmatically

            # Get classes taught by this faculty
            classes = ClassSection.objects.filter(
                instructor=faculty,
                semester=current_semester
            ).select_related('course')

            # Get qualified courses
            qualified_courses = Course.objects.filter(
                qualified_faculty__faculty=faculty
            ).distinct()

            # Get department data if department head
            department_data = None
            if is_department_head:
                department_faculty = Faculty.objects.filter(department=faculty.department)
                department_courses = Course.objects.filter(department=faculty.department)
                department_sections = ClassSection.objects.filter(
                    course__department=faculty.department,
                    semester=current_semester
                )
                department_data = {
                    'faculty_count': department_faculty.count(),
                    'course_count': department_courses.count(),
                    'section_count': department_sections.count()
                }

            context = {
                'faculty': faculty,
                'is_department_head': is_department_head,
                'classes': classes,
                'qualified_courses': qualified_courses,
                'department_data': department_data
            }
            return render(request, self.template_name, context)
        except Faculty.DoesNotExist:
            messages.error(request, "You don't have faculty privileges.")
            return redirect('home')

class FacultyClassListView(LoginRequiredMixin, ListView):
    template_name = 'academics/faculty/class_list.html'
    context_object_name = 'classes'

    def get_queryset(self):
        try:
            faculty = Faculty.objects.get(user=self.request.user)
            semester = self.request.GET.get('semester', "Spring 2025")

            # Department heads can see all department classes
            if faculty.is_department_head():
                return ClassSection.objects.filter(
                    course__department=faculty.department,
                    semester=semester
                ).select_related('course', 'instructor')

            # Regular faculty see only their classes
            return ClassSection.objects.filter(
                instructor=faculty,
                semester=semester
            ).select_related('course')
        except Faculty.DoesNotExist:
            return ClassSection.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            faculty = Faculty.objects.get(user=self.request.user)
            context['faculty'] = faculty
            context['is_department_head'] = faculty.is_department_head()
            context['current_semester'] = self.request.GET.get('semester', "Spring 2025")
        except Faculty.DoesNotExist:
            context['is_department_head'] = False
        return context

class FacultyClassDetailView(LoginRequiredMixin, DetailView):
    model = ClassSection
    template_name = 'academics/faculty/class_detail.html'
    context_object_name = 'section'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = Faculty.objects.get(user=self.request.user)
        section = self.object

        # Check if user is authorized to view this section
        if section.instructor == faculty or (faculty.is_department_head() and section.course.department == faculty.department):
            context['is_authorized'] = True
            context['is_instructor'] = section.instructor == faculty
            context['is_department_head'] = faculty.is_department_head()
            context['schedules'] = section.schedules.all().order_by('day')
            context['enrolled_students'] = section.enrollments.select_related('student').order_by('student__last_name')
            context['assignments'] = section.assignments.all().order_by('due_date')
            context['exams'] = section.exams.all().order_by('date')
        else:
            context['is_authorized'] = False

        return context

class FacultyClassScheduleEditView(LoginRequiredMixin, View):
    template_name = 'academics/faculty/schedule_edit.html'

    def get(self, request, pk):
        section = get_object_or_404(ClassSection, pk=pk)
        faculty = get_object_or_404(Faculty, user=request.user)

        # Check authorization
        if not (section.instructor == faculty or (faculty.is_department_head() and section.course.department == faculty.department)):
            messages.error(request, "You are not authorized to edit this schedule.")
            return redirect('academics:faculty_dashboard')

        schedules = section.schedules.all().order_by('day')
        context = {
            'section': section,
            'schedules': schedules,
            'day_choices': ClassSchedule.DAYS,
            'is_department_head': faculty.is_department_head(),
            'faculty': faculty
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        section = get_object_or_404(ClassSection, pk=pk)
        faculty = get_object_or_404(Faculty, user=request.user)

        # Check authorization
        if not (section.instructor == faculty or (faculty.is_department_head() and section.course.department == faculty.department)):
            messages.error(request, "You are not authorized to edit this schedule.")
            return redirect('academics:faculty_dashboard')

        # Delete existing schedules if replacing them
        if request.POST.get('replace_schedules'):
            section.schedules.all().delete()

        # Process new schedule entries
        days = request.POST.getlist('day')
        start_times = request.POST.getlist('start_time')
        end_times = request.POST.getlist('end_time')

        for i in range(len(days)):
            if i < len(start_times) and i < len(end_times):
                ClassSchedule.objects.create(
                    class_section=section,
                    day=days[i],
                    start_time=start_times[i],
                    end_time=end_times[i]
                )

        messages.success(request, f"Schedule for {section} has been updated.")
        return redirect('academics:faculty_class_detail', pk=section.pk)

class DepartmentHeadFacultyListView(LoginRequiredMixin, ListView):
    template_name = 'academics/faculty/department_faculty.html'
    context_object_name = 'faculty_members'

    def get_queryset(self):
        try:
            faculty = Faculty.objects.get(user=self.request.user)
            if faculty.is_department_head():
                return Faculty.objects.filter(department=faculty.department)
            return Faculty.objects.none()
        except Faculty.DoesNotExist:
            return Faculty.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            faculty = Faculty.objects.get(user=self.request.user)
            context['faculty'] = faculty
            context['is_department_head'] = faculty.is_department_head()
            context['department'] = faculty.department
        except Faculty.DoesNotExist:
            context['is_department_head'] = False
        return context

class DepartmentHeadCourseListView(LoginRequiredMixin, ListView):
    template_name = 'academics/faculty/department_courses.html'
    context_object_name = 'courses'

    def get_queryset(self):
        try:
            faculty = Faculty.objects.get(user=self.request.user)
            if faculty.is_department_head():
                return Course.objects.filter(department=faculty.department)
            return Course.objects.none()
        except Faculty.DoesNotExist:
            return Course.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            faculty = Faculty.objects.get(user=self.request.user)
            context['faculty'] = faculty
            context['is_department_head'] = faculty.is_department_head()
            context['department'] = faculty.department
        except Faculty.DoesNotExist:
            context['is_department_head'] = False
        return context


class ClassScheduleListView(LoginRequiredMixin, ListView):
    model = ClassSchedule
    template_name = 'academics/faculty/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        """
        Filter schedules for the logged-in user's instructor
        """
        return ClassSchedule.objects.filter(
            class_section__instructor__user=self.request.user
        ).select_related(
            'class_section',
            'class_section__course',
            'class_section__instructor',
            'default_course'
        ).order_by('day', 'start_time')


class FacultyStudentsView(LoginRequiredMixin, View):
    template_name = 'academics/faculty/student_list.html'

    def get(self, request):
        try:
            faculty = Faculty.objects.get(user=request.user)
            current_semester = "Spring 2025"  # Could be determined programmatically

            # Get section ID from query params if provided
            section_id = request.GET.get('section')

            if section_id:
                # View students for a specific section
                section = get_object_or_404(ClassSection, pk=section_id)

                # Check if faculty is instructor for this section
                if section.instructor != faculty:
                    messages.error(request, "You are not authorized to view students for this class section.")
                    return redirect('academics:faculty_dashboard')

                # Get users from User model (need to import)
                from django.contrib.auth import get_user_model
                User = get_user_model()

                students = User.objects.filter(
                    enrollments__class_section=section
                ).order_by('last_name', 'first_name')

                context = {
                    'section': section,
                    'students': students,
                    'faculty': faculty,
                    'view_type': 'section'
                }
            else:
                # Regular faculty see only their classes
                faculty_classes = ClassSection.objects.filter(
                    instructor=faculty,
                    semester=current_semester
                ).select_related('course')

                context = {
                    'faculty': faculty,
                    'faculty_classes': faculty_classes,
                    'view_type': 'list'
                }

            return render(request, self.template_name, context)
        except Faculty.DoesNotExist:
            messages.error(request, "You don't have faculty privileges.")
            return redirect('home')

class FacultyStudentDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'academics/faculty/student_detail.html'
    context_object_name = 'student'

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return get_object_or_404(get_user_model(), pk=user_id, role='student')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        faculty = get_object_or_404(Faculty, user=self.request.user)

        # Check if faculty is authorized to view this student
        authorized = False
        current_semester = "Spring 2025"

        # Faculty can view students in their classes
        if Enrollment.objects.filter(
            student=student,
            class_section__instructor=faculty,
            class_section__semester=current_semester
        ).exists():
            authorized = True

        # Department heads can view any student in their department
        elif faculty.is_department_head() and student.department == faculty.department:
            authorized = True

        if not authorized:
            messages.error(self.request, "You are not authorized to view this student's profile.")
            return {'authorized': False}

        # Get student's current enrollments
        enrollments = Enrollment.objects.filter(
            student=student,
            class_section__semester=current_semester
        ).select_related('class_section', 'class_section__course', 'class_section__instructor')

        context.update({
            'faculty': faculty,
            'is_department_head': faculty.is_department_head(),
            'authorized': authorized,
            'enrollments': enrollments
        })
        return context


class RoutineView(LoginRequiredMixin, View):
    template_name = 'academics/routine/view.html'

    def get(self, request, section_id):
        section = get_object_or_404(ClassSection, id=section_id)
        routines = ClassRoutine.objects.filter(class_section=section).select_related(
            'course', 'faculty'
        )

        organized_routines = {}
        for day_code, day_name in ClassRoutine.DAYS:
            organized_routines[day_code] = {
                'name': day_name,
                'slots': []
            }

        for routine in routines:
            day = routine.day
            organized_routines[day]['slots'].append(routine)

        for day in organized_routines.values():
            day['slots'].sort(key=lambda x: x.start_time)

        return render(request, self.template_name, {
            'section': section,
            'department': section.course.department,
            'organized_routines': organized_routines,
            'days': dict(ClassRoutine.DAYS)
        })


class GenerateRoutinePDF(LoginRequiredMixin, View):
    def get(self, request, section_id):
        section = get_object_or_404(ClassSection, id=section_id)
        routines = ClassRoutine.objects.filter(class_section=section).select_related(
            'course', 'faculty'
        )

        organized_routines = {}
        for day_code, day_name in ClassRoutine.DAYS:
            organized_routines[day_code] = {
                'name': day_name,
                'slots': []
            }

        for routine in routines:
            organized_routines[routine.day]['slots'].append(routine)

        for day in organized_routines.values():
            day['slots'].sort(key=lambda x: x.start_time)

        template = get_template('academics/routine/pdf.html')
        context = {
            'section': section,
            'department': section.course.department,
            'organized_routines': organized_routines,
            'days': dict(ClassRoutine.DAYS),
            'current_date': datetime.datetime.now().strftime('%Y-%m-%d')
        }

        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"Class_Routine_{section.course.department.code}_{section.section_number}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        return HttpResponse("Error generating PDF", status=400)


class FacultyClassDetailView(LoginRequiredMixin, DetailView):
    model = ClassSection
    template_name = 'academics/faculty/class_detail.html'
    context_object_name = 'section'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'faculty'):
            messages.error(request, "Access denied. Faculty only.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faculty = self.request.user.faculty
        section = self.object

        # Check if user is authorized to view this section
        if section.instructor == faculty:
            context['is_authorized'] = True
            context['is_instructor'] = True
            context['schedules'] = section.schedules.all().order_by('day')
            context['enrolled_students'] = section.enrollments.select_related('student').order_by('student__last_name')
            context['assignments'] = section.assignments.all().order_by('due_date')
            context['exams'] = section.exams.all().order_by('date')
            context['faculty'] = faculty

            # Add exam form
            if not self.request.GET.get('edit_exam'):
                context['exam_form'] = ExamForm(initial={'class_section': section})
            else:
                exam = get_object_or_404(Exam, pk=self.request.GET.get('edit_exam'))
                context['exam_form'] = ExamForm(instance=exam)
                context['edit_exam'] = exam
        else:
            context['is_authorized'] = False
            messages.error(self.request, "You are not authorized to view this class section.")

        return context

    def post(self, request, *args, **kwargs):
        section = self.get_object()
        faculty = self.request.user.faculty

        if section.instructor != faculty:
            messages.error(request, "You are not authorized to manage exams for this class.")
            return redirect('academics:faculty_dashboard')

        # Handle exam creation/update
        exam_id = request.POST.get('exam_id')
        if exam_id:
            exam = get_object_or_404(Exam, pk=exam_id)
            form = ExamForm(request.POST, instance=exam)
        else:
            form = ExamForm(request.POST)

        if form.is_valid():
            exam = form.save(commit=False)
            exam.class_section = section
            exam.save()
            messages.success(request, 'Exam successfully saved.')
        else:
            messages.error(request, 'Error saving exam. Please check the form.')

        return redirect('academics:faculty_class_detail', pk=section.pk)

# academics/views.py
class FacultySectionListView(LoginRequiredMixin, ListView):
    model = ClassSection
    template_name = 'academics/faculty/section_list.html'
    context_object_name = 'sections'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'faculty'):
            messages.error(request, "Access denied. Faculty only.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        current_semester = "Spring 2025"
        return (ClassSection.objects
               .filter(instructor=self.request.user.faculty)
               .select_related('course', 'instructor')
               .prefetch_related('schedules', 'enrollments', 'enrollments__student')
               .order_by('course__code'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faculty'] = self.request.user.faculty
        context['current_semester'] = "Spring 2025"
        context['show_debug'] = True  # For debugging purposes
        return context


class ExamCreateView(LoginRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'academics/faculty/exam_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_section'] = get_object_or_404(ClassSection, pk=self.kwargs['class_pk'])
        return context

    def form_valid(self, form):
        class_section = get_object_or_404(ClassSection, pk=self.kwargs['class_pk'])
        faculty = get_object_or_404(Faculty, user=self.request.user)

        if class_section.instructor != faculty:
            messages.error(self.request, "You are not authorized to add exams to this class.")
            return redirect('academics:faculty_dashboard')

        form.instance.class_section = class_section
        messages.success(self.request, "Exam created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('academics:faculty_class_detail', kwargs={'pk': self.kwargs['class_pk']})

class ExamUpdateView(LoginRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'academics/faculty/exam_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['class_section'] = self.object.class_section
        return context

    def get_success_url(self):
        return reverse_lazy('academics:faculty_class_detail', kwargs={'pk': self.object.class_section.id})

    def dispatch(self, request, *args, **kwargs):
        exam = self.get_object()
        faculty = get_object_or_404(Faculty, user=request.user)

        if exam.class_section.instructor != faculty:
            messages.error(request, "You are not authorized to edit this exam.")
            return redirect('academics:faculty_dashboard')
        return super().dispatch(request, *args, **kwargs)

class ExamDeleteView(LoginRequiredMixin, DeleteView):
    model = Exam
    template_name = 'academics/faculty/exam_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('academics:faculty_class_detail', kwargs={'pk': self.object.class_section.id})

    def dispatch(self, request, *args, **kwargs):
        exam = self.get_object()
        faculty = get_object_or_404(Faculty, user=request.user)

        if exam.class_section.instructor != faculty:
            messages.error(request, "You are not authorized to delete this exam.")
            return redirect('academics:faculty_dashboard')
        return super().dispatch(request, *args, **kwargs)


class StudentSectionListView(LoginRequiredMixin, ListView):
    model = ClassSection
    template_name = 'academics/student/section_list.html'
    context_object_name = 'sections'

    def dispatch(self, request, *args, **kwargs):
        # Instead of checking for student attribute, check if user is a student
        if request.user.role != 'student':
            messages.error(request, "Access denied. Students only.")
            return redirect('academics:my_schedule')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        current_semester = "Spring 2025"
        return (ClassSection.objects
               .filter(enrollments__student=self.request.user)
               .select_related('course', 'instructor')
               .prefetch_related('schedules')
               .order_by('course__code'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # No need to access student attribute
        context['current_semester'] = "Spring 2025"
        return context
class StudentClassDetailView(LoginRequiredMixin, DetailView):
    model = ClassSection
    template_name = 'academics/student/class_detail.html'
    context_object_name = 'section'

    def dispatch(self, request, *args, **kwargs):
        # Check user role instead of student attribute
        if request.user.role != 'student':
            messages.error(request, "Access denied. Students only.")
            return redirect('academics:my_schedule')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = self.object

        # Check if student is enrolled in this section
        if section.enrollments.filter(student=self.request.user).exists():
            context['is_authorized'] = True
            context['is_enrolled'] = True
            context['schedules'] = section.schedules.all().order_by('day')
            context['assignments'] = section.assignments.all().order_by('due_date')
            context['exams'] = section.exams.all().order_by('date')
            context['instructor'] = section.instructor
        else:
            context['is_authorized'] = False
            messages.error(self.request, "You are not enrolled in this class section.")

        return context