from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta


class Almacen(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    codigo = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"Almacén de {self.usuario.username}"


class Libro(models.Model):
    almacen = models.ForeignKey(Almacen, related_name='libros', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255, blank=True, null=True)
    autor = models.CharField(max_length=255, blank=True, null=True)
    edicion = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    archivo = models.FileField(upload_to='libros/', blank=True, null=True)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='libros')

    class Meta:
        unique_together = ('almacen','isbn')
        #constraints = [models.UniqueConstraint(fields=['almacen', 'isbn'], name='unique_isbn_per_user')        ]

    def __str__(self):
        return f"{self.titulo} - {self.autor}"


class PuntuacionLibro(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    puntuacion = models.PositiveIntegerField()

    class Meta:
        unique_together = ('libro', 'usuario')  # Evitar duplicados


class LibreriaLibro(models.Model):
    titulo = models.CharField(max_length=255, blank=True, null=True)
    autor = models.CharField(max_length=255, blank=True, null=True)
    edicion = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    portada = models.ImageField(upload_to='libros_portada/', blank=True, null=True)

class Comentario(models.Model):
    libro = models.ForeignKey(LibreriaLibro, related_name='comentarios', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.usuario.username} sobre {self.libro.titulo}"

