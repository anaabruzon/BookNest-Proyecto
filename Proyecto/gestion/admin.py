from django.contrib import admin
from .models import Almacen, Libro, PuntuacionLibro, LibreriaLibro

# Configuración para el modelo Libro
@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'edicion', 'propietario', 'isbn')
    search_fields = ('titulo', 'autor', 'isbn')
    
    fieldsets = (
        (None, {
            'fields': ('titulo', 'autor', 'edicion', 'archivo', 'propietario', 'isbn')
        }),
        # He eliminado 'Detalles de lectura' ya que no hay campos relacionados
    )

# Configuración para el modelo PuntuacionLibro
@admin.register(PuntuacionLibro)
class PuntuacionLibroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'puntuacion')
    search_fields = ('usuario__username', 'libro__titulo')

@admin.register(LibreriaLibro)
class LibreriaLibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'edicion', 'isbn', 'portada')
    search_fields = ('titulo', 'autor', 'isbn')

    fieldsets = (
        (None, {
            'fields': ('titulo', 'autor', 'edicion', 'isbn', 'portada')
        }),
    )