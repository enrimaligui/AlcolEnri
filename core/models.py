from django.db import models
from django.contrib.auth.models import User

class AcademicYear(models.Model):
    name=models.CharField(max_length=50,unique=True)
    start_date=models.DateField(null=True,blank=True)
    end_date=models.DateField(null=True,blank=True)
    active=models.BooleanField(default=True)
    class Meta: ordering=['-name']
    def __str__(self): return self.name

class Course(models.Model):
    name=models.CharField(max_length=120,unique=True)
    level=models.CharField(max_length=120,blank=True)
    description=models.TextField(blank=True)
    status=models.CharField(max_length=30,default='Activo')
    academic_year=models.ForeignKey(AcademicYear,null=True,blank=True,on_delete=models.PROTECT,related_name='courses')
    tutor=models.ForeignKey('Professor',null=True,blank=True,on_delete=models.SET_NULL,related_name='tutor_courses')
    def __str__(self): return self.name

class Professor(models.Model):
    code=models.CharField(max_length=30,unique=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=120,blank=True)
    phone=models.CharField(max_length=60,blank=True)
    email=models.EmailField(blank=True)
    specialty=models.CharField(max_length=160,blank=True)
    status=models.CharField(max_length=30,default='Activo')
    user=models.OneToOneField(User,null=True,blank=True,on_delete=models.SET_NULL,related_name='professor_profile')
    def __str__(self): return f'{self.code} - {self.first_name} {self.last_name}'.strip()
    @property
    def full_name(self): return f'{self.first_name} {self.last_name}'.strip()

class Student(models.Model):
    code=models.CharField(max_length=30,unique=True)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=120,blank=True)
    birth_date=models.DateField(null=True,blank=True)
    sex=models.CharField(max_length=30,blank=True)
    phone=models.CharField(max_length=60,blank=True)
    email=models.EmailField(blank=True)
    address=models.CharField(max_length=255,blank=True)
    status=models.CharField(max_length=30,default='Activo')
    academic_year=models.ForeignKey(AcademicYear,null=True,blank=True,on_delete=models.SET_NULL,related_name='students')
    course=models.ForeignKey(Course,null=True,blank=True,on_delete=models.SET_NULL,related_name='students')
    user=models.OneToOneField(User,null=True,blank=True,on_delete=models.SET_NULL,related_name='student_profile')
    def __str__(self): return f'{self.code} - {self.first_name} {self.last_name}'.strip()
    @property
    def full_name(self): return f'{self.first_name} {self.last_name}'.strip()

class Subject(models.Model):
    code=models.CharField(max_length=30,unique=True)
    name=models.CharField(max_length=150)
    description=models.TextField(blank=True)
    status=models.CharField(max_length=30,default='Activo')
    def __str__(self): return f'{self.code} - {self.name}'

class CourseSubject(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='course_subjects')
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='course_subjects')
    class Meta: unique_together=('course','subject')

class TeachingAssignment(models.Model):
    professor=models.ForeignKey(Professor,on_delete=models.CASCADE,related_name='assignments')
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='teaching_assignments')
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='teaching_assignments')
    class Meta: unique_together=('professor','course','subject')

class Enrollment(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='enrollments')
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='enrollments')
    academic_year=models.ForeignKey(AcademicYear,on_delete=models.PROTECT,related_name='enrollments')
    enrollment_date=models.DateField(null=True,blank=True)
    status=models.CharField(max_length=30,default='Activa')
    class Meta: unique_together=('student','course','academic_year')

class Grade(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='grades')
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='grades')
    subject=models.ForeignKey(Subject,on_delete=models.PROTECT,related_name='grades')
    professor=models.ForeignKey(Professor,null=True,blank=True,on_delete=models.SET_NULL,related_name='grades')
    evaluation=models.CharField(max_length=120)
    value=models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    observation=models.TextField(blank=True)
    published=models.BooleanField(default=False)
    published_at=models.DateTimeField(null=True,blank=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: unique_together=('student','course','subject','evaluation')

class Attendance(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='attendance')
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='attendance')
    date=models.DateField()
    status=models.CharField(max_length=30)
    observation=models.TextField(blank=True)
    subject=models.ForeignKey(Subject,null=True,blank=True,on_delete=models.SET_NULL)
    professor=models.ForeignKey(Professor,null=True,blank=True,on_delete=models.SET_NULL)
    published=models.BooleanField(default=False)
    published_at=models.DateTimeField(null=True,blank=True)

class Payment(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,related_name='payments')
    concept=models.CharField(max_length=180)
    amount=models.DecimalField(max_digits=14,decimal_places=2)
    date=models.DateField(null=True,blank=True)
    payment_method=models.CharField(max_length=80,blank=True)
    status=models.CharField(max_length=50,default='Pagado')
    observation=models.TextField(blank=True)

class Parent(models.Model):
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=120)
    phone=models.CharField(max_length=60,blank=True)
    email=models.EmailField(blank=True)
    address=models.CharField(max_length=255,blank=True)
    students=models.ManyToManyField(Student,through='StudentParent',related_name='parents')
    def __str__(self): return f'{self.first_name} {self.last_name}'

class StudentParent(models.Model):
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    parent=models.ForeignKey(Parent,on_delete=models.CASCADE)
    relationship=models.CharField(max_length=60,blank=True)
    class Meta: unique_together=('student','parent')

class Schedule(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='schedules')
    subject=models.ForeignKey(Subject,on_delete=models.PROTECT)
    professor=models.ForeignKey(Professor,on_delete=models.PROTECT)
    weekday=models.CharField(max_length=30)
    start_time=models.TimeField()
    end_time=models.TimeField()
    classroom=models.CharField(max_length=80,blank=True)
    status=models.CharField(max_length=30,default='Activo')

class Publication(models.Model):
    title=models.CharField(max_length=200)
    content=models.TextField()
    date=models.DateTimeField(auto_now_add=True)
    author_name=models.CharField(max_length=180,blank=True)
    published=models.BooleanField(default=True)
    def __str__(self): return self.title

class Setting(models.Model):
    key=models.CharField(max_length=100,unique=True)
    value=models.TextField(blank=True)
    def __str__(self): return self.key

class SyncKey(models.Model):
    name=models.CharField(max_length=100,unique=True)
    key=models.CharField(max_length=200,unique=True)
    active=models.BooleanField(default=True)

class SyncState(models.Model):
    name=models.CharField(max_length=80,unique=True,default='desktop')
    version=models.PositiveBigIntegerField(default=0)
    updated_at=models.DateTimeField(auto_now=True)

class DesktopSnapshot(models.Model):
    name=models.CharField(max_length=80,unique=True,default='main')
    data=models.JSONField(default=dict)
    version=models.PositiveBigIntegerField(default=0)
    updated_at=models.DateTimeField(auto_now=True)
