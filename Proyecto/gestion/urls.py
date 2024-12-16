from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    BibliotecaView,
    DetalleLibroView,
    PuntuarLibroView,
    RankingView,
    AgregarLibroView,
    ServeEpubView,
    RegistroView,
    ProfileView,
    LeerLibroView,
    LibreriaView,
    ComentarioCreateView,
    libro_detail,
    BuscarViews
)

urlpatterns = [
    # Cambia la ruta principal a PrestamosView
    path('', BibliotecaView.as_view(), name='biblioteca'),  # Página de inicio
    
    # Otras rutas
    path('libro/<int:pk>/', DetalleLibroView.as_view(), name='detalle_libro'),
    path('libro/puntuar/<int:libro_id>/', PuntuarLibroView.as_view(), name='puntuar_libro'),
    path('ranking/', RankingView.as_view(), name='ranking'),
    path('agregar-libro/', AgregarLibroView.as_view(), name='agregar_libro'),
    path('epub/<int:libro_id>/', ServeEpubView.as_view(), name='serve_epub'),
    path('biblioteca/', BibliotecaView.as_view(), name='biblioteca'),
    path('libreria/', LibreriaView.as_view(), name='libreria'),
    path('register/', RegistroView.as_view(), name='register'),  # Ruta para el registro
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='libreria'), name='logout'),
    path('libro/<int:libro_id>/leer/', LeerLibroView.as_view(), name='leer_libro'),
    path('librerialibro/<int:pk>/', libro_detail, name='libro-detail'),
    path('librerialibro-search/', BuscarViews.as_view(), name='librerialibro-search'),

    path('librerialibro/<int:pk>/comentario/', ComentarioCreateView.as_view(), name='crear-comentario'),
]





