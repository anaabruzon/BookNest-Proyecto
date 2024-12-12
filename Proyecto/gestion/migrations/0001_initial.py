# Generated by Django 5.1.1 on 2024-12-03 20:34

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Libro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(blank=True, max_length=255, null=True)),
                ('autor', models.CharField(blank=True, max_length=255, null=True)),
                ('edicion', models.CharField(blank=True, max_length=255, null=True)),
                ('isbn', models.CharField(blank=True, max_length=13, null=True, unique=True)),
                ('archivo', models.FileField(blank=True, null=True, upload_to='libros/')),
                ('en_prestamo', models.BooleanField(default=False)),
                ('propietario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='libros', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Prestamo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField(auto_now_add=True)),
                ('fecha_fin', models.DateField()),
                ('libro', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='prestamo', to='gestion.libro')),
                ('usuarios', models.ManyToManyField(related_name='prestamos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PuntuacionLibro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntuacion', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('libro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntuaciones', to='gestion.libro')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntuaciones', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
