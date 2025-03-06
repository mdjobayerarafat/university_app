# academics/urls.py
from django.urls import path

from . import views
from .views import (
    DepartmentListView,
    DepartmentDetailView,
    FacultyListView,
    FacultyDetailView,
    CourseListView,
    CourseDetailView,
    MyScheduleView,
    ClassSectionDetailView,
    EnrollView,
    DropClassView,
    AssignmentListView,
    ExamListView, FacultyDashboardView, FacultyClassListView, FacultyClassDetailView, FacultyClassScheduleEditView,
    DepartmentHeadFacultyListView, DepartmentHeadCourseListView, FacultyStudentsView, FacultyStudentDetailView,
    AssignmentCreateView, AssignmentUpdateView, AssignmentDeleteView, FacultySectionListView,
)

app_name = 'academics'  # Namespace for the app

urlpatterns = [
    # Department URLs
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department_detail'),

    # Faculty URLs
    path('faculty/', FacultyListView.as_view(), name='faculty_list'),
    path('faculty/<int:pk>/', FacultyDetailView.as_view(), name='faculty_detail'),
    path('faculty/edit-profile/', views.FacultyEditView.as_view(), name='faculty_edit_profile'),
    # Course URLs
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course_detail'),

    # Class Section URLs
    path('sections/<int:pk>/', ClassSectionDetailView.as_view(), name='class_section_detail'),
    path('sections/<int:pk>/enroll/', EnrollView.as_view(), name='enroll'),
    path('sections/<int:pk>/drop/', DropClassView.as_view(), name='drop_class'),

    # My Schedule URL
    path('class-schedule/<int:pk>/', views.ClassScheduleView.as_view(), name='class_schedule'),
    path('my-schedule/', MyScheduleView.as_view(), name='my_schedule'),
    path('my-schedule/<int:section_id>/', MyScheduleView.as_view(), name='my_schedule_section'),

    # Assignment URLs
    path('assignments/', AssignmentListView.as_view(), name='assignment_list'),
    path('schedules/', views.ClassScheduleListView.as_view(), name='class_schedule_list'),

    # Exam URLs
    path('exams/', ExamListView.as_view(), name='exam_list'),

    # Faculty Dashboard
    path('faculty/dashboard/', FacultyDashboardView.as_view(), name='faculty_dashboard'),

    # Faculty Class List
    path('faculty/classes/', FacultyClassListView.as_view(), name='faculty_class_list'),

    # Faculty Class Detail
    path('faculty/classes/<int:pk>/', FacultyClassDetailView.as_view(), name='faculty_class_detail'),

    # Faculty Class Schedule Edit
    path('faculty/classes/<int:pk>/schedule/', FacultyClassScheduleEditView.as_view(),
         name='faculty_class_schedule_edit'),

    # Department Head Faculty List
    path('department/faculty/', DepartmentHeadFacultyListView.as_view(), name='department_faculty_list'),
# academics/urls.py
path('routine/<int:section_id>/', views.RoutineView.as_view(), name='routine_view'),
path('routine/<int:section_id>/pdf/', views.GenerateRoutinePDF.as_view(), name='routine_pdf'),
    # Department Head Course List
    path('department/courses/', DepartmentHeadCourseListView.as_view(), name='department_course_list'),
    path('faculty/students/', FacultyStudentsView.as_view(), name='faculty_students'),
    path('faculty/students/<int:pk>/', FacultyStudentDetailView.as_view(), name='faculty_student_detail'),
    # Faculty Class Detail
    path('faculty/classes/<int:pk>/',
         FacultyClassDetailView.as_view(),
         name='faculty_class_detail'),

    # Assignment Management
    path('class/<int:class_pk>/assignment/add/',
         AssignmentCreateView.as_view(),
         name='assignment_create'),
    path('assignment/<int:pk>/edit/',
         AssignmentUpdateView.as_view(),
         name='assignment_edit'),
    path('assignment/<int:pk>/delete/',
         AssignmentDeleteView.as_view(),
         name='assignment_delete'),
    path('faculty/sections/',
         FacultySectionListView.as_view(),
         name='faculty_section_list'),
]