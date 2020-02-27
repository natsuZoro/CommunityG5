from django.db import models
from django.contrib.auth.models import User
from gestionActividades.models import Distrito, Provincia, Departamento

# Create your models here.
class Preferencias(models.Model):
    id_usuario = models.IntegerField()
    id_distrito = models.ForeignKey('gestionActividades.Distrito', on_delete=models.CASCADE)
    id_categoria = models.ForeignKey('gestionActividades.Categoria', on_delete=models.CASCADE)

class Preferencias_valor(models.Model):
    id_usuario = models.IntegerField()
    id_valor = models.ForeignKey('gestionActividades.Valor', on_delete=models.CASCADE)