from django.http import HttpResponse
from django.template import Template, Context
from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from gestionActividades.models import Categoria, RelacionActividadUsuario, Actividad
from gestionComunidades.models import RelacionComunidadUsuario
from gestionColectivos.models import RelacionColectivoActividad, RelacionColectivoUsuario
from django.db.models import Q, Count, Max, Aggregate
import datetime
from django.contrib.auth.models import User
from django.contrib import auth

def home(request):
    categoria = Categoria.objects.all()
    contexto = {'categoria':categoria}
    return render(request, "inicio/principal.html",contexto)

def buscar_palabra(request):
    mensaje=request.GET['p']
    tipo=request.GET['t']
    if request.user.is_authenticated:
        current_user = request.user

        #acumulamos las actividades en donde el usuario es voluntario
        filtro1 = RelacionActividadUsuario.objects.filter(id_usuario_id=current_user.id)

        #acumulamos las actividades en donde el usuario es creador de la comunidad o integrante del colectivo
        tempo1 = RelacionComunidadUsuario.objects.filter(id_integrante_id=current_user.id)
        filtro2 = Actividad.objects.filter(id_comunidad_id__in=tempo1.values_list('id_comunidad_id',flat=True))
        filtro3 = Actividad.objects.filter(id_usuario_id=current_user.id)

        #segun el criterio mostramos todos excepto los que tienen  alguna interaccion con el usuario
        
        if tipo == '0':
            actividad = Actividad.objects.filter((Q(titulo__contains=request.GET['p']) | Q(descripcion__contains=request.GET['p'])) & Q(fecha_fin__gte=datetime.datetime.now())).order_by('fecha_inicio').exclude(Q(id__in=filtro1.values_list('id_actividad_id',flat=True)) | Q(id__in=filtro2.values_list('id',flat=True)) | Q(id__in=filtro3.values_list('id',flat=True)))
        else:
            actividad = Actividad.objects.filter(Q(titulo__contains=request.GET['p']) | Q(descripcion__contains=request.GET['p'])).order_by('fecha_inicio').exclude(Q(id__in=filtro1.values_list('id_actividad_id',flat=True)) | Q(id__in=filtro2.values_list('id',flat=True)) | Q(id__in=filtro3.values_list('id',flat=True)))
        
    else:
        if tipo == '0':
            actividad = Actividad.objects.filter((Q(titulo__contains=request.GET['p']) | Q(descripcion__contains=request.GET['p'])) & Q(fecha_fin__gte=datetime.datetime.now())).order_by('fecha_inicio')
        else:
            actividad = Actividad.objects.filter(Q(titulo__contains=request.GET['p']) | Q(descripcion__contains=request.GET['p'])).order_by('fecha_inicio')
        
    fecha_actual = datetime.datetime.now()
    contexto = {'actividades':actividad, 'palabra_clave':mensaje, 'tipo':tipo, 'hoy':fecha_actual}
    return render(request, "buscar/palabra.html",contexto)

