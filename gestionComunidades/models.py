from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Comunidad(models.Model):
    titulo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=250)
    imagen_principal = models.CharField(max_length=500)
    imagen_descripcion = models.CharField(max_length=150)
    fundador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fundador_comunidad_set')

class RelacionComunidadUsuario(models.Model):
    id_comunidad = models.ForeignKey('Comunidad', on_delete=models.CASCADE)
    id_integrante = models.ForeignKey(User, on_delete=models.CASCADE)