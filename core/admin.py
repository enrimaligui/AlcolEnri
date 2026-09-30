from django.contrib import admin
from .models import *

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin): list_display=('name','start_date','end_date','active'); search_fields=('name',)
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin): list_display=('name','level','academic_year','tutor','status'); search_fields=('name','level'); list_filter=('status','academic_year')
@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin): list_display=('code','first_name','last_name','specialty','status'); search_fields=('code','first_name','last_name'); list_filter=('status',)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin): list_display=('code','first_name','last_name','course','academic_year','status'); search_fields=('code','first_name','last_name'); list_filter=('status','course','academic_year')
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin): list_display=('code','name','status'); search_fields=('code','name'); list_filter=('status',)
for model in [CourseSubject,TeachingAssignment,Enrollment,Grade,Attendance,Payment,Parent,StudentParent,Schedule,Publication,Setting,SyncKey,SyncState,DesktopSnapshot]:
    try: admin.site.register(model)
    except admin.sites.AlreadyRegistered: pass
