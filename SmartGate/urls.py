from django.urls import path
from . import views

urlpatterns = [
    # Página inicial (redirige al login o muestra una vista simple)
    path('', views.index, name='index'),

    # Registro y autenticación
    path('registro/', views.registrar_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # Dashboards por rol
    path('administrador/dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('vigilante/dashboard/', views.dashboard_vigilante, name='dashboard_vigilante'),
    path('residente/dashboard/', views.dashboard_residente, name='dashboard_residente'),

    #REGISTRO DE VEHICULO EN RESIDENTE
    path('registrar-vehiculo/', views.registrar_vehiculo, name='registrar_vehiculo'),
    path('mis-vehiculos/', views.mis_vehiculos, name='mis_vehiculos'),
    path('dashboard/', views.dashboard_residente, name='dashboard_residente'),


    #COMPLETAR PERFIL
    path('completar-perfil/', views.completar_perfil_residente, name='completar_perfil_residente'),
    path('residente/actualizar-perfil/', views.actualizar_perfil_residente, name='actualizar_perfil_residente'),
    path('datos-personales/', views.ver_datos_personales, name='datos_personales'),


    # Ver residentes desde vigilante
    path('vigilante/residentes/', views.ver_residentes_vigilante, name='ver_residentes_vigilante'),

]

