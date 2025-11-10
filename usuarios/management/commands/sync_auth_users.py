from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import Rol, Usuario

class Command(BaseCommand):
    help = 'Sincroniza usuarios de auth.User a usuarios.Usuario. Uso: python manage.py sync_auth_users [--email=email]'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email del usuario a sincronizar (opcional)')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options.get('email')
        qs = User.objects.all()
        if email:
            qs = qs.filter(email=email)
            if not qs.exists():
                self.stdout.write(self.style.ERROR(f"No se encontró auth.User con email {email}"))
                return

        rol_super, _ = Rol.objects.get_or_create(nombre='SuperAdmin', defaults={'descripcion':'Administrador total'})

        for au in qs:
            usuario, created = Usuario.objects.update_or_create(
                email=au.email,
                defaults={
                    'username': au.username or au.email.split('@')[0],
                    'rol': rol_super,  # por defecto SuperAdmin; cambia si quieres lógica diferente
                    'activo': True,
                    'password': au.password,  # copia el hash
                }
            )
            verb = "Creado" if created else "Actualizado"
            self.stdout.write(self.style.SUCCESS(f"{verb}: {usuario.email} -> usuarios.Usuario id={usuario.idUsuario}"))