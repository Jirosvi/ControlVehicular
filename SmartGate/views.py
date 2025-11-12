from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegistroUsuarioForm, LoginUsuarioForm
from .models import Usuario
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehiculo, Residente
from .forms import VehiculoForm

from django.contrib.auth.decorators import login_required

# ---------------------------------------------------
# 🧾 REGISTRO MANUAL DE USUARIO
# ---------------------------------------------------
def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Usuario registrado correctamente. Ahora puede iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, '❌ Corrige los errores antes de continuar.')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro.html', {'form': form})


# ---------------------------------------------------
# 🔐 LOGIN DE USUARIO
# ---------------------------------------------------
def login_usuario(request):
    if request.method == 'POST':
        form = LoginUsuarioForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"👋 Bienvenido, {user.first_name or user.email}")

                # 🔁 Redirección por rol
                if user.rol == 'ADMINISTRADOR':
                    return redirect('dashboard_admin')
                elif user.rol == 'VIGILANTE':
                    return redirect('dashboard_vigilante')
                else:
                    return redirect('dashboard_residente')
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')
        else:
            messages.error(request, 'Correo o contraseña inválidos.')
    else:
        form = LoginUsuarioForm()
    return render(request, 'login.html', {'form': form})


# ---------------------------------------------------
# 🚪 LOGOUT
# ---------------------------------------------------
@login_required
def logout_usuario(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')

# ---------------------------------------------------
# 📊 DASHBOARDS POR ROL
# ---------------------------------------------------
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# ADMINISTRADOR
@login_required
def dashboard_admin(request):
    user = request.user
    contexto = {
        'nombre': user.first_name,
        'apellido': user.last_name
    }
    return render(request, 'administrador/dashboard.html', contexto)


# VIGILANTE
@login_required
def dashboard_vigilante(request):
    user = request.user
    contexto = {
        'nombre': user.first_name,
        'apellido': user.last_name
    }
    return render(request, 'vigilante/dashboard.html', contexto)


# RESIDENTE
@login_required
def dashboard_residente(request):
    user = request.user
    residente, created = Residente.objects.get_or_create(usuario=user)

    # Si el residente no tiene datos completos, lo redirigimos a completar perfil
    if not residente.dni or not residente.direccion or not residente.telefono:
        return redirect('completar_perfil_residente')

    contexto = {
        'nombre': user.first_name,
        'apellido': user.last_name,
        'residente': residente
    }
    return render(request, 'residente/dashboard.html', contexto)


#vista  para iniciar
from django.shortcuts import render, redirect

def index(request):
    return render(request, 'home.html')



#REGISTRAR VEHICULO
@login_required
def registrar_vehiculo(request):
    if request.user.rol != 'RESIDENTE':
        return redirect('acceso_denegado')

    residente = get_object_or_404(Residente, usuario=request.user)

    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.residente = residente
            vehiculo.save()
            return redirect('mis_vehiculos')
    else:
        form = VehiculoForm()

    return render(request, 'residente/registrar_vehiculo.html', {'form': form})

#VER MIS VEHICULOS
@login_required
def mis_vehiculos(request):
    if request.user.rol != 'RESIDENTE':
        return redirect('acceso_denegado')

    residente = get_object_or_404(Residente, usuario=request.user)
    vehiculos = Vehiculo.objects.filter(residente=residente)

    return render(request, 'residente/mis_vehiculos.html', {'vehiculos': vehiculos})




#completar perfil residente
@login_required
def completar_perfil_residente(request):
    usuario = request.user
    residente, created = Residente.objects.get_or_create(usuario=usuario)

    if request.method == 'POST':
        # 🔹 Actualizar datos del modelo Usuario
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        usuario.email = request.POST.get('email')
        usuario.save()

        # 🔹 Actualizar datos del modelo Residente
        residente.dni = request.POST.get('dni')
        residente.direccion = request.POST.get('direccion')
        residente.telefono = request.POST.get('telefono')
        residente.save()

        messages.success(request, "Tus datos se actualizaron correctamente.")
        return redirect('dashboard_residente')

    return render(request, 'residente/completar_perfil.html', {
        'residente': residente,
        'usuario': usuario
    })

#actualizar perfil de residente
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ActualizarPerfilForm
from .models import Residente

@login_required
def actualizar_perfil_residente(request):
    usuario = request.user
    residente, created = Residente.objects.get_or_create(usuario=usuario)

    if request.method == 'POST':
        form = ActualizarPerfilForm(request.POST, instance=residente, usuario=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos se actualizaron correctamente.")
            return redirect('dashboard_residente')
    else:
        form = ActualizarPerfilForm(instance=residente, usuario=usuario)

    return render(request, 'residente/actualizar_perfil.html', {'form': form})

# Ver datos personales del residente
@login_required
def ver_datos_personales(request):
    usuario = request.user
    residente = Residente.objects.filter(usuario=usuario).first()  # Obtener el residente asociado

    return render(request, 'residente/datos_personales.html', {
        'usuario': usuario,
        'residente': residente
    })

#ver residente en rol vigilante
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Residente


@login_required
def ver_residentes_vigilante(request):
    # Solo vigilante puede acceder
    if request.user.rol != 'VIGILANTE':
        return redirect('acceso_denegado')  # O al dashboard

    # Traemos todos los residentes y su info de usuario
    residentes = Residente.objects.select_related('usuario').all()

    contexto = {
        'residentes': residentes
    }
    return render(request, 'vigilante/ver_residentes.html', contexto)
