from django.contrib import admin
from .models import Almacen, Libro, PuntuacionLibro, Prestamo

# Configuración para el modelo Libro
@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'edicion', 'propietario', 'en_prestamo', 'isbn')
    search_fields = ('titulo', 'autor', 'isbn')
    
    fieldsets = (
        (None, {
            'fields': ('titulo', 'autor', 'edicion', 'archivo', 'propietario', 'isbn', 'en_prestamo')
        }),
        # He eliminado 'Detalles de lectura' ya que no hay campos relacionados
    )

# Configuración para el modelo PuntuacionLibro
@admin.register(PuntuacionLibro)
class PuntuacionLibroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'libro', 'puntuacion')
    search_fields = ('usuario__username', 'libro__titulo')

# Configuración para el modelo Prestamo
@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('libro', 'mostrar_usuarios', 'fecha_inicio', 'fecha_fin')
    search_fields = ('libro__titulo', 'usuarios__username')
    list_filter = ('fecha_inicio', 'fecha_fin')

    def mostrar_usuarios(self, obj):
        return ", ".join([usuario.username for usuario in obj.usuarios.all()])
    mostrar_usuarios.short_description = 'Usuarios'

@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('usuario','codigo')