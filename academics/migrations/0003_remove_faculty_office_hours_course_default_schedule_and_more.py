# Generated by Django 5.1.6 on 2025-03-05 18:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faculty',
            name='office_hours',
        ),
        migrations.AddField(
            model_name='course',
            name='default_schedule',
            field=models.TextField(blank=True, help_text='JSON format of default schedule pattern'),
        ),
        migrations.AddField(
            model_name='faculty',
            name='bio',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='faculty',
            name='office_hours_text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='faculty',
            name='office_phone',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='faculty',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='faculty_profiles/'),
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('degree', models.CharField(max_length=200)),
                ('institution', models.CharField(max_length=200)),
                ('year', models.PositiveIntegerField()),
                ('field_of_study', models.CharField(blank=True, max_length=200)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='education', to='academics.faculty')),
            ],
            options={
                'verbose_name_plural': 'Education',
                'ordering': ['-year'],
            },
        ),
        migrations.CreateModel(
            name='OfficeHour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], max_length=3)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='office_hours', to='academics.faculty')),
            ],
            options={
                'ordering': ['day'],
            },
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('journal', models.CharField(max_length=200)),
                ('year', models.PositiveIntegerField()),
                ('citation', models.TextField()),
                ('url', models.URLField(blank=True, null=True)),
                ('doi', models.CharField(blank=True, max_length=100)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publications', to='academics.faculty')),
            ],
            options={
                'ordering': ['-year', 'title'],
            },
        ),
        migrations.CreateModel(
            name='CourseAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_primary', models.BooleanField(default=False, help_text='Primary instructor for this course')),
                ('date_qualified', models.DateField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qualified_faculty', to='academics.course')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_qualifications', to='academics.faculty')),
            ],
            options={
                'unique_together': {('faculty', 'course')},
            },
        ),
        migrations.CreateModel(
            name='StudentSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.CharField(max_length=20)),
                ('day', models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], max_length=3)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('location', models.CharField(max_length=100)),
                ('attendance_count', models.PositiveIntegerField(default=0)),
                ('last_attended', models.DateField(blank=True, null=True)),
                ('class_section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_schedules', to='academics.classsection')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_schedules', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['day', 'start_time'],
                'unique_together': {('student', 'class_section', 'day')},
            },
        ),
    ]
