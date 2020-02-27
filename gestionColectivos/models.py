from django.db import models
from django.contrib.auth.models import User
from gestionActividades.models import Actividad

# Create your models here.

class Colectivo(models.Model):
    titulo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=250)
    imagen_principal = models.CharField(max_length=500)
    imagen_descripcion = models.CharField(max_length=150)
    fundador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fundador_colectivo_set')
    lider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lider_colectivo_set')

class RelacionColectivoUsuario(models.Model):
    id_colectivo = models.ForeignKey('Colectivo', on_delete=models.CASCADE)
    id_integrante = models.ForeignKey(User, on_delete=models.CASCADE)

class RelacionColectivoActividad(models.Model):
    id_actividad = models.ForeignKey('gestionActividades.Actividad', on_delete=models.CASCADE)
    id_colectivo = models.ForeignKey('Colectivo', on_delete=models.CASCADE, null=True)
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    calificado = models.BooleanField(default=False, null=True)