from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# ---------------------------------------------------
# 1️⃣ MANAGER PERSONALIZADO PARA USUARIO
# ---------------------------------------------------
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Crea y guarda un usuario (manual o por Gmail).
        """
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # Para usuarios de Gmail sin contraseña local

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crea un superusuario (para panel admin de Django o uso interno).
        """
        extra_fields.setdefault('rol', 'ADMINISTRADOR')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# ---------------------------------------------------
# 2️⃣ MODELO DE USUARIO PRINCIPAL
# ---------------------------------------------------
class Usuario(AbstractBaseUser, PermissionsMixin):
    ROL_CHOICES = [
        ('ADMINISTRADOR', 'Administrador'),
        ('VIGILANTE', 'Vigilante'),
        ('RESIDENTE', 'Residente'),
    ]

    usuario_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, verbose_name='Nombres', blank=True)
    last_name = models.CharField(max_length=50, verbose_name='Apellidos', blank=True)
    email = models.EmailField(max_length=100, unique=True, verbose_name='Correo electrónico')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='RESIDENTE')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_staff = models.BooleanField(default=False, verbose_name='Acceso al admin interno')
    is_google_user = models.BooleanField(default=False, verbose_name='Registrado con Google')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'



# ---------------------------------------------------
# 3️⃣ MODELO DE RESIDENTE
# ---------------------------------------------------
class Residente(models.Model):
    residente_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='residente')
    dni = models.CharField(max_length=15, verbose_name='DNI', unique=True)
    direccion = models.CharField(max_length=100, verbose_name='Dirección')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    estado = models.BooleanField(default=True, verbose_name='Activo')

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} ({self.dni})"

# ---------------------------------------------------
# 4️⃣ MODELO DE VEHÍCULO
# ---------------------------------------------------
class Vehiculo(models.Model):
    vehiculo_id = models.AutoField(primary_key=True)
    residente = models.ForeignKey(Residente, on_delete=models.CASCADE, related_name='vehiculos')
    placa = models.CharField(max_length=10, unique=True, verbose_name='Placa')
    marca = models.CharField(max_length=50, verbose_name='Marca')
    modelo = models.CharField(max_length=50, verbose_name='Modelo')
    color = models.CharField(max_length=30, verbose_name='Color')
    imagen = models.ImageField(upload_to='vehiculos/', blank=True, null=True, verbose_name='Foto del vehículo')
    estado = models.CharField(
        max_length=20,
        choices=[('DENTRO', 'Dentro'), ('FUERA', 'Fuera')],
        default='FUERA',
        verbose_name='Ubicación actual'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')

    def __str__(self):
        return f"{self.placa} - {self.marca} ({self.residente.usuario.first_name})"






