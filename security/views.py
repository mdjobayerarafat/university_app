from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReportForm, UpdateReportForm
from .models import Report

def is_teacher(user):
    return user.is_staff

@login_required
def report_list(request):
    if is_teacher(request.user):
        reports = Report.objects.all()
    else:
        reports = Report.objects.filter(reporter=request.user)
    return render(request, 'security/report_list.html', {'reports': reports})

@login_required
def create_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            messages.success(request, 'Report submitted successfully!')
            return redirect('security:report_list')
    else:
        form = ReportForm()
    return render(request, 'security/create_report.html', {'form': form})

@user_passes_test(is_teacher)
def update_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        form = UpdateReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, 'Report updated successfully!')
            return redirect('security:report_list')
    else:
        form = UpdateReportForm(instance=report)
    return render(request, 'security/update_report.html', {'form': form, 'report': report})