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
    en_prestamo = models.BooleanField(default=False)
    usuario_prestamo = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='libros_prestados'
    )
    fecha_prestamo = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('almacen','isbn')
        #constraints = [models.UniqueConstraint(fields=['almacen', 'isbn'], name='unique_isbn_per_user')        ]

    def __str__(self):
        return f"{self.titulo} - {self.autor}"


class PuntuacionLibro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='puntuaciones')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='puntuaciones')
    puntuacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    def __str__(self):
        return f"{self.libro.titulo} - {self.usuario.username}: {self.puntuacion}"


class Prestamo(models.Model):
    libro = models.OneToOneField(Libro, on_delete=models.CASCADE, related_name='prestamo')
    usuarios = models.ManyToManyField(User, related_name='prestamos')
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField()

    def save(self, *args, **kwargs):
        if not self.fecha_fin:  # Si fecha_fin no está ya definido
            self.fecha_fin = timezone.now().date() + timedelta(days=150)  # 5 meses
        super().save(*args, **kwargs)
        # Marcar el libro como en préstamo
        self.libro.en_prestamo = True
        self.libro.usuario_prestamo = self.usuarios.first()
        self.libro.fecha_prestamo = self.fecha_inicio
        self.libro.save()

    def finalizar_prestamo(self):
        self.usuarios.clear()
        self.libro.en_prestamo = False
        self.libro.usuario_prestamo = None
        self.libro.fecha_prestamo = None
        self.libro.save()

    def __str__(self):
        return f"Préstamo de {self.libro.titulo} - Hasta {self.fecha_fin}"
