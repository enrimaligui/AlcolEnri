from django.urls import path
from . import views
urlpatterns=[
 path('',views.dashboard,name='dashboard'),path('login/',views.login_page,name='login'),path('logout/',views.logout_page,name='logout'),
 path('profesor/',views.professor_dashboard,name='professor_dashboard'),path('estudiante/',views.student_dashboard,name='student_dashboard'),path('admin-app/',views.admin_dashboard,name='admin_dashboard'),
 path('notas/enviar/',views.publish_grades,name='publish_grades'),path('publicaciones/',views.publications,name='publications'),path('api/sync/',views.sync_api,name='sync_api'),path('api/health/',views.health,name='health')]
