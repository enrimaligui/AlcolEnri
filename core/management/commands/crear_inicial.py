import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import SyncKey, AcademicYear, Setting

class Command(BaseCommand):
    help = "Crea la cuenta superadmin, configuración inicial y clave central."
    def handle(self,*args,**kwargs):
        u,_=User.objects.get_or_create(username="maligui",defaults={"first_name":"Superadministrador","is_staff":True,"is_superuser":True})
        u.is_active=True; u.is_staff=True; u.is_superuser=True; u.set_password("contrasena7649"); u.save()
        AcademicYear.objects.get_or_create(name="2026-2027",defaults={"active":True})
        Setting.objects.get_or_create(key="nombre_colegio",defaults={"value":"AlcolEnri"})
        key=os.getenv("ALCOLENRI_SYNC_KEY") or "ALC-uT72lF4HEXgurcND2oIHUKDQ5p1nhaU4zXOECa4KVIw"
        SyncKey.objects.update_or_create(name="desktop",defaults={"key":key,"active":True})
        self.stdout.write(self.style.SUCCESS("Superadmin: maligui / contrasena7649"))
        self.stdout.write(self.style.SUCCESS("ALCOLENRI_SYNC_KEY="+key))
