import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import *

ROLE_ADMIN = {'SUPERADMIN', 'ADMIN'}
EVALUACIONES = ['1ª Evaluación','2ª Evaluación','3ª Evaluación','4ª Evaluación','5ª Evaluación','Evaluación Final','Recuperación']
ESTADOS_ASISTENCIA = ['PRESENTE','AUSENTE','RETRASO','JUSTIFICADO','EXCUSADO']

def profile_role(user):
    if user.is_superuser: return 'SUPERADMIN'
    if hasattr(user, 'professor_profile'): return 'PROFESOR'
    if hasattr(user, 'student_profile'): return 'ESTUDIANTE'
    if user.is_staff: return 'ADMIN'
    return ''

def require_role(request, roles): return profile_role(request.user) in roles

def login_page(request):
    if request.user.is_authenticated: return redirect('dashboard')
    mode = request.POST.get('mode') or request.GET.get('tipo') or 'admin'
    if request.method == 'POST':
        code = request.POST.get('code','').strip().upper()
        password = request.POST.get('password','')
        user = None
        if mode == 'admin':
            user = authenticate(request, username=code, password=password)
        elif mode == 'profesor':
            p = Professor.objects.filter(code=code, status='Activo').select_related('user').first()
            user = p.user if p and p.user_id else None
        elif mode == 'estudiante':
            s = Student.objects.filter(code=code, status='Activo').select_related('user').first()
            user = s.user if s and s.user_id else None
        if user and user.is_active:
            login(request, user)
            return redirect('dashboard')
        return render(request, 'core/login.html', {'error':'El usuario, contraseña o código no son válidos.','mode':mode})
    return render(request, 'core/login.html', {'mode':mode})

def logout_page(request): logout(request); return redirect('login')

@login_required
def dashboard(request):
    r=profile_role(request.user)
    if r in ROLE_ADMIN: return redirect('admin_dashboard')
    if r=='PROFESOR': return redirect('professor_dashboard')
    if r=='ESTUDIANTE': return redirect('student_dashboard')
    return HttpResponseForbidden('Perfil no configurado')

@login_required
def admin_dashboard(request):
    if not require_role(request, ROLE_ADMIN): return HttpResponseForbidden('Acceso no autorizado')
    ctx={'students':Student.objects.count(),'professors':Professor.objects.count(),'courses':Course.objects.count(),'subjects':Subject.objects.count(),'grades':Grade.objects.count(),'payments':Payment.objects.count(),'attendance':Attendance.objects.count(),'publications':Publication.objects.filter(published=True).count(),'recent_students':Student.objects.select_related('course').order_by('-id')[:20]}
    return render(request,'core/admin_dashboard.html',ctx)

@login_required
def professor_dashboard(request):
    if profile_role(request.user)!='PROFESOR': return HttpResponseForbidden('Acceso no autorizado')
    p=request.user.professor_profile
    assignments=list(TeachingAssignment.objects.filter(professor=p).select_related('course','subject'))
    selected_id=request.POST.get('assignment') or request.GET.get('assignment')
    selected_eval=request.POST.get('evaluation') or request.GET.get('evaluation') or EVALUACIONES[0]
    selected=None
    if selected_id:
        try: selected=next((a for a in assignments if str(a.id)==str(selected_id)),None)
        except Exception: selected=None
    if not selected and assignments: selected=assignments[0]
    message=''
    if request.method=='POST' and selected:
        action=request.POST.get('action')
        if action in ('save_grades','publish_grades'):
            student_ids=list(Student.objects.filter(course=selected.course).values_list('id',flat=True))
            for sid in student_ids:
                raw=request.POST.get(f'grade_{sid}','').strip().replace(',','.')
                obs=request.POST.get(f'obs_{sid}','').strip()
                if raw=='': value=None
                else:
                    try:
                        value=float(raw)
                        if value<0 or value>10: raise ValueError
                    except ValueError:
                        continue
                obj=Grade.objects.filter(student_id=sid,course=selected.course,subject=selected.subject,evaluation=selected_eval).first()
                if value is None and not obs and obj:
                    continue
                if obj:
                    obj.value=value; obj.observation=obs; obj.professor=p
                    if action=='publish_grades': obj.published=True; obj.published_at=timezone.now()
                    obj.save()
                elif value is not None or obs:
                    Grade.objects.create(student_id=sid,course=selected.course,subject=selected.subject,professor=p,evaluation=selected_eval,value=value,observation=obs,published=action=='publish_grades',published_at=timezone.now() if action=='publish_grades' else None)
            message='Notas guardadas.' if action=='save_grades' else 'Las notas de esta evaluación han sido publicadas.'
        elif action=='delete_grade':
            gid=request.POST.get('grade_id')
            Grade.objects.filter(id=gid,professor=p).delete(); message='Nota eliminada.'
        elif action in ('save_attendance','publish_attendance'):
            rawdate=request.POST.get('attendance_date')
            date_value=rawdate or timezone.localdate().isoformat()
            student_ids=list(Student.objects.filter(course=selected.course).values_list('id',flat=True))
            for sid in student_ids:
                status=request.POST.get(f'att_{sid}','').strip().upper()
                obs=request.POST.get(f'attobs_{sid}','').strip()
                if status not in ESTADOS_ASISTENCIA: continue
                obj=Attendance.objects.filter(student_id=sid,course=selected.course,subject=selected.subject,date=date_value).first()
                if obj:
                    obj.status=status; obj.observation=obs; obj.professor=p
                    if action=='publish_attendance': obj.published=True; obj.published_at=timezone.now()
                    obj.save()
                else:
                    Attendance.objects.create(student_id=sid,course=selected.course,subject=selected.subject,professor=p,date=date_value,status=status,observation=obs,published=action=='publish_attendance',published_at=timezone.now() if action=='publish_attendance' else None)
            message='Asistencia guardada.' if action=='save_attendance' else 'La asistencia ha sido publicada.'
        elif action=='delete_attendance':
            aid=request.POST.get('attendance_id'); Attendance.objects.filter(id=aid,professor=p).delete(); message='Registro de asistencia eliminado.'
    students=[]
    if selected:
        students=list(Student.objects.filter(course=selected.course,status='Activo').order_by('last_name','first_name'))
        grades_map={g.student_id:g for g in Grade.objects.filter(course=selected.course,subject=selected.subject,evaluation=selected_eval)}
        att_date=request.GET.get('attendance_date') or request.POST.get('attendance_date') or str(timezone.localdate())
        att_map={a.student_id:a for a in Attendance.objects.filter(course=selected.course,subject=selected.subject,date=att_date)}
        for s in students: s.current_grade=grades_map.get(s.id); s.current_attendance=att_map.get(s.id)
    else: att_date=str(timezone.localdate())
    return render(request,'core/professor_dashboard.html',{'professor':p,'assignments':assignments,'selected':selected,'evaluaciones':EVALUACIONES,'selected_eval':selected_eval,'students':students,'attendance_date':att_date,'publications':Publication.objects.filter(published=True).order_by('-date')[:10],'message':message,'estados_asistencia':ESTADOS_ASISTENCIA})

@login_required
def student_dashboard(request):
    if profile_role(request.user)!='ESTUDIANTE': return HttpResponseForbidden('Acceso no autorizado')
    s=request.user.student_profile
    return render(request,'core/student_dashboard.html',{'student':s,'grades':Grade.objects.filter(student=s,published=True).select_related('subject','course','professor').order_by('course__name','subject__name','evaluation'),'attendance':Attendance.objects.filter(student=s,published=True).select_related('subject','course').order_by('-date')[:100],'publications':Publication.objects.filter(published=True).order_by('-date')[:20]})

@login_required
def publications(request): return render(request,'core/publications.html',{'publications':Publication.objects.filter(published=True).order_by('-date')})

def _key_ok(request):
    key=request.headers.get('X-AlcolEnri-Sync-Key') or request.GET.get('key')
    return bool(key and SyncKey.objects.filter(key=key,active=True).exists())

def _snapshot():
    tables={
      'academic_years':list(AcademicYear.objects.values('id','name','start_date','end_date','active')),
      'courses':list(Course.objects.values('id','name','level','description','status','academic_year_id','tutor_id')),
      'professors':list(Professor.objects.values('id','code','first_name','last_name','phone','email','specialty','status')),
      'students':list(Student.objects.values('id','code','first_name','last_name','birth_date','sex','phone','email','address','status','academic_year_id','course_id')),
      'subjects':list(Subject.objects.values('id','code','name','description','status')),
      'course_subjects':list(CourseSubject.objects.values('id','course_id','subject_id')),
      'assignments':list(TeachingAssignment.objects.values('id','professor_id','course_id','subject_id')),
      'enrollments':list(Enrollment.objects.values('id','student_id','course_id','academic_year_id','enrollment_date','status')),
      'grades':list(Grade.objects.values('id','student_id','course_id','subject_id','professor_id','evaluation','value','observation','published','published_at')),
      'attendance':list(Attendance.objects.values('id','student_id','course_id','date','status','observation','subject_id','professor_id','published','published_at')),
      'payments':list(Payment.objects.values('id','student_id','concept','amount','date','payment_method','status','observation')),
      'parents':list(Parent.objects.values('id','first_name','last_name','phone','email','address')),
      'student_parents':list(StudentParent.objects.values('id','student_id','parent_id','relationship')),
      'schedules':list(Schedule.objects.values('id','course_id','subject_id','professor_id','weekday','start_time','end_time','classroom','status')),
      'publications':list(Publication.objects.values('id','title','content','date','author_name','published')),
      'settings':list(Setting.objects.values('id','key','value')),
    }
    ds=DesktopSnapshot.objects.filter(name='main').first(); raw=ds.data if ds and isinstance(ds.data,dict) else {}
    tables['usuarios']=raw.get('usuarios',[]); tables['cuentas_personales']=raw.get('cuentas_personales',[])
    return {'version':SyncState.objects.get_or_create(name='desktop')[0].version,'tables':tables}

def _upsert(model, rows, fields):
    for row in rows:
        data={k:row.get(k) for k in fields if k in row}
        pk=row.get('id')
        if pk: model.objects.update_or_create(pk=pk,defaults=data)
        else: model.objects.create(**data)

@csrf_exempt
def sync_api(request):
    if not _key_ok(request): return JsonResponse({'error':'Clave de sincronización no válida'},status=401)
    if request.method=='GET': return JsonResponse(_snapshot(),safe=False)
    try: payload=json.loads(request.body.decode('utf-8')); tables=payload.get('tables',{})
    except Exception: return JsonResponse({'error':'JSON no válido'},status=400)
    try:
        with transaction.atomic():
            _upsert(AcademicYear,tables.get('academic_years',[]),('name','start_date','end_date','active'))
            _upsert(Professor,tables.get('professors',[]),('code','first_name','last_name','phone','email','specialty','status'))
            _upsert(Subject,tables.get('subjects',[]),('code','name','description','status'))
            _upsert(Course,tables.get('courses',[]),('name','level','description','status','academic_year_id','tutor_id'))
            _upsert(Student,tables.get('students',[]),('code','first_name','last_name','birth_date','sex','phone','email','address','status','academic_year_id','course_id'))
            for p in Professor.objects.all():
                u,_=User.objects.get_or_create(username=p.code,defaults={'is_active':p.status=='Activo'}); u.is_active=p.status=='Activo'; u.set_unusable_password(); u.save(update_fields=['is_active','password']);
                if p.user_id!=u.id: p.user=u; p.save(update_fields=['user'])
            for s in Student.objects.all():
                u,_=User.objects.get_or_create(username=s.code,defaults={'is_active':s.status=='Activo'}); u.is_active=s.status=='Activo'; u.set_unusable_password(); u.save(update_fields=['is_active','password']);
                if s.user_id!=u.id: s.user=u; s.save(update_fields=['user'])
            _upsert(CourseSubject,tables.get('course_subjects',[]),('course_id','subject_id'))
            _upsert(TeachingAssignment,tables.get('assignments',[]),('professor_id','course_id','subject_id'))
            _upsert(Enrollment,tables.get('enrollments',[]),('student_id','course_id','academic_year_id','enrollment_date','status'))
            _upsert(Grade,tables.get('grades',[]),('student_id','course_id','subject_id','professor_id','evaluation','value','observation','published','published_at'))
            _upsert(Attendance,tables.get('attendance',[]),('student_id','course_id','date','status','observation','subject_id','professor_id','published','published_at'))
            _upsert(Payment,tables.get('payments',[]),('student_id','concept','amount','date','payment_method','status','observation'))
            _upsert(Parent,tables.get('parents',[]),('first_name','last_name','phone','email','address'))
            _upsert(StudentParent,tables.get('student_parents',[]),('student_id','parent_id','relationship'))
            _upsert(Schedule,tables.get('schedules',[]),('course_id','subject_id','professor_id','weekday','start_time','end_time','classroom','status'))
            _upsert(Publication,tables.get('publications',[]),('title','content','date','author_name','published'))
            _upsert(Setting,tables.get('settings',[]),('key','value'))
            ds,_=DesktopSnapshot.objects.get_or_create(name='main'); ds.data={k:tables.get(k,[]) for k in ('usuarios','cuentas_personales')}; ds.save()
            st=SyncState.objects.get_or_create(name='desktop')[0]; st.version+=1; st.save()
        return JsonResponse({'ok':True,'version':SyncState.objects.get(name='desktop').version})
    except Exception as e: return JsonResponse({'ok':False,'error':str(e)},status=400)

def health(request): return JsonResponse({'status':'ok','service':'AlcolEnri','central_database':True,'time':timezone.now().isoformat()})
