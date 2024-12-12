# Generated by Django 5.1.1 on 2024-12-05 19:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='libro',
            name='fecha_prestamo',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='libro',
            name='usuario_prestamo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='libros_prestados', to=settings.AUTH_USER_MODEL),
        ),
    ]
