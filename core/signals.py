from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Professor, Student, DesktopSnapshot

def ensure_user(kind, obj):
    user, _ = User.objects.get_or_create(username=obj.code, defaults={'is_active': obj.status == 'Activo'})
    user.is_active = obj.status == 'Activo'
    user.set_unusable_password()
    user.save(update_fields=['is_active','password'])
    if obj.user_id != user.id:
        obj.user = user
        obj.save(update_fields=['user'])
    ds,_=DesktopSnapshot.objects.get_or_create(name='main')
    data=ds.data if isinstance(ds.data,dict) else {}
    users=list(data.get('usuarios',[])); links=list(data.get('cuentas_personales',[]))
    role='profesor' if kind=='profesor' else 'estudiante'
    existing=next((u for u in users if u.get('nombre_usuario')==obj.code),None)
    if not existing:
        uid=max([int(u.get('id',0) or 0) for u in users] or [0])+1
        existing={'id':uid,'nombre_usuario':obj.code,'nombre_completo':obj.full_name,'contrasena':'','rol':role,'activo':1 if obj.status=='Activo' else 0,'fecha_creacion':'','telefono':getattr(obj,'phone',''),'correo':getattr(obj,'email',''),'tipo_cuenta':'normal'}; users.append(existing)
    else: existing.update({'nombre_completo':obj.full_name,'activo':1 if obj.status=='Activo' else 0,'telefono':getattr(obj,'phone',''),'correo':getattr(obj,'email','')})
    if not any(int(x.get('usuario_id',0) or 0)==int(existing['id']) and x.get('persona_tipo')==role for x in links):
        lid=max([int(x.get('id',0) or 0) for x in links] or [0])+1; links.append({'id':lid,'usuario_id':existing['id'],'persona_tipo':role,'persona_id':obj.id})
    ds.data={'usuarios':users,'cuentas_personales':links}; ds.save()

@receiver(post_save,sender=Professor)
def professor_user(sender,instance,**kwargs): ensure_user('profesor',instance)
@receiver(post_save,sender=Student)
def student_user(sender,instance,**kwargs): ensure_user('estudiante',instance)
