from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario
from .models import Vehiculo

# ---------------------------------------------------
# 🧾 FORMULARIO DE REGISTRO MANUAL
# ---------------------------------------------------
class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirmar_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'rol', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }

    # 🔍 Validación de contraseñas
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirmar_password = cleaned_data.get('confirmar_password')

        if password and confirmar_password and password != confirmar_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    # 💾 Guardar usuario con contraseña encriptada
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# ---------------------------------------------------
# 🔐 FORMULARIO DE LOGIN
# ---------------------------------------------------
class LoginUsuarioForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


# ---------------------------------------------------
# 🔐 FORMULARIO DE VEHICULO
# ---------------------------------------------------

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['placa', 'marca', 'modelo', 'color', 'imagen']
        widgets = {
            'placa': forms.TextInput(attrs={'placeholder': 'Ingrese la placa'}),
            'marca': forms.TextInput(attrs={'placeholder': 'Ingrese la marca'}),
            'modelo': forms.TextInput(attrs={'placeholder': 'Ingrese el modelo'}),
            'color': forms.TextInput(attrs={'placeholder': 'Ingrese el color'}),
            'imagen': forms.ClearableFileInput(),
        }

# ---------------------------------------------------
# 🔐 actualizar perfil del residente
# ---------------------------------------------------
from django import forms
from django.contrib.auth.models import User
from .models import Residente

class ActualizarPerfilForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombres", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)
    email = forms.EmailField(label="Correo electrónico", required=True)

    class Meta:
        model = Residente
        fields = ['dni', 'direccion', 'telefono']

    def __init__(self, *args, **kwargs):
        # Espera un parámetro extra: 'usuario'
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if self.usuario:
            self.fields['first_name'].initial = self.usuario.first_name
            self.fields['last_name'].initial = self.usuario.last_name
            self.fields['email'].initial = self.usuario.email

    def save(self, commit=True):
        residente = super().save(commit=False)
        if self.usuario:
            self.usuario.first_name = self.cleaned_data['first_name']
            self.usuario.last_name = self.cleaned_data['last_name']
            self.usuario.email = self.cleaned_data['email']
            if commit:
                self.usuario.save()
        if commit:
            residente.save()
        return residente
