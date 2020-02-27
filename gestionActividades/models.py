from django.db import models
from django.contrib.auth.models import User
from gestionComunidades.models import Comunidad

# Create your models here.

class Actividad(models.Model):
    titulo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=250)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    id_distrito = models.ForeignKey('Distrito', on_delete=models.CASCADE)
    id_comunidad  = models.ForeignKey('gestionComunidades.Comunidad', on_delete=models.CASCADE, null=True)
    id_usuario  = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    id_categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    direccion = models.CharField(max_length=250)
    referencia = models.CharField(max_length=400)
    imagen_principal = models.CharField(max_length=500)
    imagen_descripcion = models.CharField(max_length=150)
    culminada = models.BooleanField(default=False, null=True)

class Valor(models.Model):
    titulo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=300)

class Categoria(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    imagen = models.CharField(max_length=500)

class RelacionActividadValor(models.Model):
    id_actividad = models.ForeignKey('Actividad', on_delete=models.CASCADE)
    id_valor = models.ForeignKey('Valor', on_delete=models.CASCADE)

class RelacionActividadUsuario(models.Model):
    id_actividad = models.ForeignKey('Actividad', on_delete=models.CASCADE)
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    realizado = models.BooleanField(default=False)
    fecha = models.DateField(auto_now_add=True,null=True)

class Distrito(models.Model):
    nombre = models.CharField(max_length=50)
    id_provincia = models.ForeignKey('Provincia', on_delete=models.CASCADE)

class Provincia(models.Model):
    nombre = models.CharField(max_length=50)
    id_departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE)

class Departamento(models.Model):
    nombre = models.CharField(max_length=50)

