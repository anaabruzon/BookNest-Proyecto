from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    PrestamosView,
    BibliotecaView,
    PrestarLibroView,
    DevolverLibroView,
    DetalleLibroView,
    PuntuarLibroView,
    RankingView,
    AgregarLibroView,
    ServeEpubView,
    RegistroView,
    ProfileView,
    LeerLibroView
)

urlpatterns = [
    # Cambia la ruta principal a PrestamosView
    path('', PrestamosView.as_view(), name='prestamos'),  # Página de inicio
    
    # Otras rutas
    path('prestamos/', PrestamosView.as_view(), name='prestamos'),
    path('prestamos/prestar/<int:libro_id>/', PrestarLibroView.as_view(), name='prestar_libro'),
    path('prestamos/devolver/<int:libro_id>/', DevolverLibroView.as_view(), name='devolver_libro'),
    path('libro/<int:pk>/', DetalleLibroView.as_view(), name='detalle_libro'),
    path('libro/puntuar/<int:libro_id>/', PuntuarLibroView.as_view(), name='puntuar_libro'),
    path('ranking/', RankingView.as_view(), name='ranking'),
    path('agregar-libro/', AgregarLibroView.as_view(), name='agregar_libro'),
    path('epub/<int:libro_id>/', ServeEpubView.as_view(), name='serve_epub'),
    path('biblioteca/', BibliotecaView.as_view(), name='biblioteca'),
    path('register/', RegistroView.as_view(), name='register'),  # Ruta para el registro
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='prestamos'), name='logout'),
    path('libro/<int:libro_id>/leer/', LeerLibroView.as_view(), name='leer_libro'),

]



